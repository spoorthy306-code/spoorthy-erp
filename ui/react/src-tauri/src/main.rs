use std::{
  fs,
  path::PathBuf,
  sync::{Arc, Mutex},
  thread,
  time::Duration,
};

use chrono::Utc;
use reqwest::Client;
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use tauri::{Manager, State};
use uuid::Uuid;

#[derive(Default, Clone, Serialize, Deserialize)]
struct SyncConfig {
  api_url: Option<String>,
  bearer_token: Option<String>,
}

impl SyncConfig {
  fn is_configured(&self) -> bool {
    self.api_url.is_some() && self.bearer_token.is_some()
  }
}

#[derive(Clone, Serialize, Deserialize)]
struct SyncStatus {
  is_online: bool,
  is_syncing: bool,
  pending_changes: i64,
  last_sync_at: Option<String>,
  mode: String,
}

impl Default for SyncStatus {
  fn default() -> Self {
    Self {
      is_online: false,
      is_syncing: false,
      pending_changes: 0,
      last_sync_at: None,
      mode: "offline".to_string(),
    }
  }
}

#[derive(Clone, Serialize, Deserialize)]
struct SyncRunResult {
  success: bool,
  message: String,
  pushed: u32,
  pulled: u32,
  conflicts: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SyncMutation {
  id: String,
  table: String,
  operation: String,
  record_id: Option<String>,
  data: Value,
  created_at: String,
  retry_count: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SyncPayload {
  mutations: Vec<SyncMutation>,
  last_sync_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct PushResponse {
  successful_ids: Vec<String>,
  #[serde(default)]
  conflicts: Vec<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ServerDelta {
  #[serde(default)]
  entities: Vec<Value>,
  #[serde(default)]
  journal_entries: Vec<Value>,
  #[serde(default)]
  deleted_ids: Vec<String>,
  server_timestamp: Option<String>,
}

#[derive(Clone)]
struct AppState {
  db_path: PathBuf,
  db_dir: PathBuf,
  sync_config: Arc<Mutex<SyncConfig>>,
  sync_status: Arc<Mutex<SyncStatus>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct JournalEntry {
  entry_id: String,
  entity_id: String,
  entry_date: String,
  period: String,
  narration: Option<String>,
  total_debit: f64,
  total_credit: f64,
  created_at: String,
  lines: Option<Vec<JournalLineDetail>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct JournalLineDetail {
  line_id: Option<String>,
  account_code: String,
  debit: f64,
  credit: f64,
  description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct JournalEntryLinePayload {
  account_code: String,
  debit: f64,
  credit: f64,
  description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct JournalEntryCreateRequest {
  entity_id: String,
  entry_date: String,
  narration: Option<String>,
  lines: Vec<JournalEntryLinePayload>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct JournalEntryListParams {
  entity_id: String,
  period: Option<String>,
  skip: Option<i64>,
  limit: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct EntityCreatePayload {
  name: String,
  gstin: Option<String>,
  pan: Option<String>,
  tan: Option<String>,
  address: Option<Value>,
  currency: Option<String>,
  reporting_currency: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct EntityRecord {
  entity_id: String,
  name: String,
  gstin: Option<String>,
  pan: Option<String>,
  tan: Option<String>,
  address: Option<Value>,
  currency: String,
  reporting_currency: String,
  created_at: String,
  updated_at: String,
}

fn now_rfc3339() -> String {
  Utc::now().to_rfc3339()
}

fn normalize_api_url(url: &str) -> String {
  url.trim_end_matches('/').to_string()
}

fn json_opt_string(v: &Value, key: &str) -> Option<String> {
  v.get(key).and_then(|x| x.as_str()).map(|x| x.to_string())
}

fn json_number(v: &Value, key: &str) -> f64 {
  if let Some(n) = v.get(key).and_then(|x| x.as_f64()) {
    return n;
  }
  if let Some(n) = v.get(key).and_then(|x| x.as_i64()) {
    return n as f64;
  }
  0.0
}

fn init_db(conn: &Connection) -> Result<(), String> {
  conn
    .execute_batch(
      r#"
      CREATE TABLE IF NOT EXISTS journal_entries (
        entry_id TEXT PRIMARY KEY,
        entity_id TEXT NOT NULL,
        entry_date TEXT NOT NULL,
        period TEXT NOT NULL,
        narration TEXT,
        total_debit REAL NOT NULL,
        total_credit REAL NOT NULL,
        created_at TEXT NOT NULL,
        lines_json TEXT,
        updated_at TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        deleted_at TEXT
      );

      CREATE TABLE IF NOT EXISTS entities (
        entity_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        gstin TEXT,
        pan TEXT,
        tan TEXT,
        address_json TEXT,
        currency TEXT NOT NULL DEFAULT 'INR',
        reporting_currency TEXT NOT NULL DEFAULT 'INR',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT
      );

      CREATE TABLE IF NOT EXISTS accounts (
        account_code TEXT PRIMARY KEY,
        account_name TEXT NOT NULL,
        account_type TEXT,
        parent_code TEXT,
        level INTEGER
      );

      CREATE TABLE IF NOT EXISTS sync_queue (
        id TEXT PRIMARY KEY,
        table_name TEXT NOT NULL,
        operation TEXT NOT NULL,
        record_id TEXT,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        retry_count INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'pending',
        synced_at TEXT
      );

      CREATE TABLE IF NOT EXISTS conflict_log (
        id TEXT PRIMARY KEY,
        table_name TEXT NOT NULL,
        record_id TEXT,
        local_payload_json TEXT NOT NULL,
        server_payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        resolution TEXT NOT NULL DEFAULT 'server_wins'
      );

      CREATE TABLE IF NOT EXISTS sync_metadata (
        key TEXT PRIMARY KEY,
        value TEXT
      );
      "#,
    )
    .map_err(|e| format!("Failed to initialize database schema: {e}"))?;

  Ok(())
}

fn open_conn(db_path: &PathBuf) -> Result<Connection, String> {
  let conn = Connection::open(db_path).map_err(|e| format!("Failed to open SQLite DB: {e}"))?;
  init_db(&conn)?;
  Ok(conn)
}

fn pending_changes(conn: &Connection) -> i64 {
  let mut stmt = match conn.prepare("SELECT COUNT(1) FROM sync_queue WHERE status = 'pending'") {
    Ok(stmt) => stmt,
    Err(_) => return 0,
  };
  stmt.query_row([], |r| r.get::<_, i64>(0)).unwrap_or(0)
}

fn get_last_sync_time(conn: &Connection) -> Result<Option<String>, String> {
  let mut stmt = conn
    .prepare("SELECT value FROM sync_metadata WHERE key = 'last_sync_at'")
    .map_err(|e| format!("Failed to prepare metadata query: {e}"))?;

  let result = stmt.query_row([], |row| row.get::<_, String>(0));
  match result {
    Ok(v) => Ok(Some(v)),
    Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
    Err(e) => Err(format!("Failed to read last sync time: {e}")),
  }
}

fn set_last_sync_time(conn: &Connection, ts: &str) -> Result<(), String> {
  conn
    .execute(
      "INSERT INTO sync_metadata (key, value) VALUES ('last_sync_at', ?1) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
      params![ts],
    )
    .map_err(|e| format!("Failed to update last sync time: {e}"))?;
  Ok(())
}

fn queue_mutation(
  conn: &Connection,
  table_name: &str,
  operation: &str,
  record_id: Option<&str>,
  payload_json: &str,
) -> Result<(), String> {
  conn
    .execute(
      "INSERT INTO sync_queue (id, table_name, operation, record_id, payload_json, created_at, retry_count, status) VALUES (?1, ?2, ?3, ?4, ?5, ?6, 0, 'pending')",
      params![
        Uuid::new_v4().to_string(),
        table_name,
        operation,
        record_id,
        payload_json,
        now_rfc3339()
      ],
    )
    .map_err(|e| format!("Failed to enqueue mutation: {e}"))?;
  Ok(())
}

fn has_local_pending_change(conn: &Connection, table_name: &str, record_id: &str) -> Result<bool, String> {
  let mut stmt = conn
    .prepare(
      "SELECT COUNT(1) FROM sync_queue WHERE table_name = ?1 AND record_id = ?2 AND status = 'pending'",
    )
    .map_err(|e| format!("Failed to prepare pending conflict query: {e}"))?;

  let count: i64 = stmt
    .query_row(params![table_name, record_id], |row| row.get(0))
    .map_err(|e| format!("Failed to execute pending conflict query: {e}"))?;

  Ok(count > 0)
}

fn log_conflict(
  conn: &Connection,
  table_name: &str,
  record_id: Option<&str>,
  local_payload_json: &str,
  server_payload_json: &str,
) -> Result<(), String> {
  conn
    .execute(
      "INSERT INTO conflict_log (id, table_name, record_id, local_payload_json, server_payload_json, created_at, resolution) VALUES (?1, ?2, ?3, ?4, ?5, ?6, 'server_wins')",
      params![
        Uuid::new_v4().to_string(),
        table_name,
        record_id,
        local_payload_json,
        server_payload_json,
        now_rfc3339()
      ],
    )
    .map_err(|e| format!("Failed to log conflict: {e}"))?;
  Ok(())
}

fn get_pending_mutations(conn: &Connection) -> Result<Vec<SyncMutation>, String> {
  let mut stmt = conn
    .prepare(
      "SELECT id, table_name, operation, record_id, payload_json, created_at, retry_count FROM sync_queue WHERE status = 'pending' ORDER BY created_at ASC LIMIT 200",
    )
    .map_err(|e| format!("Failed to prepare pending mutations query: {e}"))?;

  let rows = stmt
    .query_map([], |row| {
      let payload_json: String = row.get(4)?;
      let payload_data = serde_json::from_str::<Value>(&payload_json).unwrap_or(Value::Null);

      Ok(SyncMutation {
        id: row.get(0)?,
        table: row.get(1)?,
        operation: row.get(2)?,
        record_id: row.get(3)?,
        data: payload_data,
        created_at: row.get(5)?,
        retry_count: row.get::<_, i64>(6)? as u32,
      })
    })
    .map_err(|e| format!("Failed to read pending mutations: {e}"))?;

  let mut items = Vec::new();
  for row in rows {
    items.push(row.map_err(|e| format!("Failed to parse pending mutation row: {e}"))?);
  }

  Ok(items)
}

fn mark_mutations_synced(conn: &Connection, successful_ids: &[String]) -> Result<(), String> {
  for id in successful_ids {
    conn
      .execute(
        "UPDATE sync_queue SET status = 'synced', synced_at = ?2 WHERE id = ?1",
        params![id, now_rfc3339()],
      )
      .map_err(|e| format!("Failed to mark mutation as synced: {e}"))?;
  }
  Ok(())
}

fn increment_retry_count(conn: &Connection, mutation_ids: &[String]) -> Result<(), String> {
  for id in mutation_ids {
    conn
      .execute(
        "UPDATE sync_queue SET retry_count = retry_count + 1 WHERE id = ?1",
        params![id],
      )
      .map_err(|e| format!("Failed to increment retry count: {e}"))?;
  }
  Ok(())
}

async fn push_to_server(
  cfg: &SyncConfig,
  mutations: Vec<SyncMutation>,
  last_sync_at: Option<String>,
) -> Result<PushResponse, String> {
  let api_url = cfg
    .api_url
    .as_ref()
    .ok_or_else(|| "Missing API URL in sync config".to_string())?;
  let token = cfg
    .bearer_token
    .as_ref()
    .ok_or_else(|| "Missing bearer token in sync config".to_string())?;

  let payload = SyncPayload {
    mutations,
    last_sync_at,
  };

  let client = Client::new();
  let url = format!("{}/api/sync/batch", normalize_api_url(api_url));

  let response = client
    .post(url)
    .bearer_auth(token)
    .json(&payload)
    .timeout(Duration::from_secs(30))
    .send()
    .await
    .map_err(|e| format!("Push request failed: {e}"))?;

  if !response.status().is_success() {
    return Err(format!("Push endpoint returned {}", response.status()));
  }

  response
    .json::<PushResponse>()
    .await
    .map_err(|e| format!("Push response parse failed: {e}"))
}

async fn pull_from_server(cfg: &SyncConfig, since: Option<String>) -> Result<ServerDelta, String> {
  let api_url = cfg
    .api_url
    .as_ref()
    .ok_or_else(|| "Missing API URL in sync config".to_string())?;
  let token = cfg
    .bearer_token
    .as_ref()
    .ok_or_else(|| "Missing bearer token in sync config".to_string())?;

  let client = Client::new();
  let url = format!("{}/api/sync/delta", normalize_api_url(api_url));

  let mut request = client
    .get(url)
    .bearer_auth(token)
    .timeout(Duration::from_secs(30));

  if let Some(since_value) = since {
    request = request.query(&[("since", since_value)]);
  }

  let response = request
    .send()
    .await
    .map_err(|e| format!("Delta pull request failed: {e}"))?;

  if !response.status().is_success() {
    return Err(format!("Delta endpoint returned {}", response.status()));
  }

  response
    .json::<ServerDelta>()
    .await
    .map_err(|e| format!("Delta response parse failed: {e}"))
}

fn apply_server_deltas(conn: &Connection, delta: ServerDelta) -> Result<(u32, u32), String> {
  let mut applied_count = 0u32;
  let mut conflict_count = 0u32;

  for id in delta.deleted_ids {
    conn
      .execute(
        "UPDATE entities SET deleted_at = ?2, updated_at = ?2 WHERE entity_id = ?1",
        params![id, now_rfc3339()],
      )
      .map_err(|e| format!("Failed to soft-delete entity from delta: {e}"))?;

    conn
      .execute(
        "UPDATE journal_entries SET deleted_at = ?2, updated_at = ?2 WHERE entry_id = ?1",
        params![id, now_rfc3339()],
      )
      .map_err(|e| format!("Failed to soft-delete journal entry from delta: {e}"))?;

    applied_count += 1;
  }

  for entity in delta.entities {
    let entity_id = json_opt_string(&entity, "entity_id")
      .or_else(|| json_opt_string(&entity, "id"))
      .unwrap_or_default();
    if entity_id.is_empty() {
      continue;
    }

    if has_local_pending_change(conn, "entities", &entity_id)? {
      let local = serde_json::json!({ "record_id": entity_id, "table": "entities", "source": "local_pending" });
      log_conflict(
        conn,
        "entities",
        Some(local["record_id"].as_str().unwrap_or_default()),
        &local.to_string(),
        &entity.to_string(),
      )?;
      conflict_count += 1;
    }

    let name = json_opt_string(&entity, "name").unwrap_or_else(|| "Unnamed Entity".to_string());
    let gstin = json_opt_string(&entity, "gstin");
    let pan = json_opt_string(&entity, "pan");
    let tan = json_opt_string(&entity, "tan");
    let currency = json_opt_string(&entity, "currency").unwrap_or_else(|| "INR".to_string());
    let reporting_currency =
      json_opt_string(&entity, "reporting_currency").unwrap_or_else(|| "INR".to_string());

    let address_json = entity
      .get("address")
      .and_then(|v| if v.is_null() { None } else { Some(v.to_string()) });

    conn
      .execute(
        r#"
        INSERT INTO entities (entity_id, name, gstin, pan, tan, address_json, currency, reporting_currency, created_at, updated_at, deleted_at)
        VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?9, NULL)
        ON CONFLICT(entity_id) DO UPDATE SET
          name = excluded.name,
          gstin = excluded.gstin,
          pan = excluded.pan,
          tan = excluded.tan,
          address_json = excluded.address_json,
          currency = excluded.currency,
          reporting_currency = excluded.reporting_currency,
          updated_at = excluded.updated_at,
          deleted_at = NULL
        "#,
        params![
          entity_id,
          name,
          gstin,
          pan,
          tan,
          address_json,
          currency,
          reporting_currency,
          now_rfc3339()
        ],
      )
      .map_err(|e| format!("Failed to apply entity delta: {e}"))?;

    applied_count += 1;
  }

  for entry in delta.journal_entries {
    let entry_id = json_opt_string(&entry, "entry_id")
      .or_else(|| json_opt_string(&entry, "id"))
      .unwrap_or_default();
    if entry_id.is_empty() {
      continue;
    }

    if has_local_pending_change(conn, "journal_entries", &entry_id)? {
      let local = serde_json::json!({ "record_id": entry_id, "table": "journal_entries", "source": "local_pending" });
      log_conflict(
        conn,
        "journal_entries",
        Some(local["record_id"].as_str().unwrap_or_default()),
        &local.to_string(),
        &entry.to_string(),
      )?;
      conflict_count += 1;
    }

    let entity_id = json_opt_string(&entry, "entity_id").unwrap_or_default();
    let entry_date = json_opt_string(&entry, "entry_date").unwrap_or_else(|| now_rfc3339()[0..10].to_string());
    let period = json_opt_string(&entry, "period").unwrap_or_else(|| entry_date.chars().take(7).collect::<String>());
    let narration = json_opt_string(&entry, "narration");
    let total_debit = json_number(&entry, "total_debit");
    let total_credit = json_number(&entry, "total_credit");
    let created_at = json_opt_string(&entry, "created_at").unwrap_or_else(now_rfc3339);

    let lines_json = entry
      .get("lines")
      .or_else(|| entry.get("journal_lines"))
      .and_then(|v| if v.is_null() { None } else { Some(v.to_string()) });

    conn
      .execute(
        r#"
        INSERT INTO journal_entries (
          entry_id, entity_id, entry_date, period, narration, total_debit, total_credit, created_at, lines_json, updated_at, sync_status, deleted_at
        ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, 'synced', NULL)
        ON CONFLICT(entry_id) DO UPDATE SET
          entity_id = excluded.entity_id,
          entry_date = excluded.entry_date,
          period = excluded.period,
          narration = excluded.narration,
          total_debit = excluded.total_debit,
          total_credit = excluded.total_credit,
          lines_json = excluded.lines_json,
          updated_at = excluded.updated_at,
          sync_status = 'synced',
          deleted_at = NULL
        "#,
        params![
          entry_id,
          entity_id,
          entry_date,
          period,
          narration,
          total_debit,
          total_credit,
          created_at,
          lines_json,
          now_rfc3339()
        ],
      )
      .map_err(|e| format!("Failed to apply journal entry delta: {e}"))?;

    applied_count += 1;
  }

  Ok((applied_count, conflict_count))
}

#[tauri::command]
fn get_sync_status(state: State<AppState>) -> Result<SyncStatus, String> {
  let conn = open_conn(&state.db_path)?;
  let mut current = state
    .sync_status
    .lock()
    .map_err(|_| "Failed to acquire sync status lock".to_string())?
    .clone();

  current.pending_changes = pending_changes(&conn);
  Ok(current)
}

#[tauri::command]
fn get_sync_config(state: State<AppState>) -> Result<SyncConfig, String> {
  let cfg = state
    .sync_config
    .lock()
    .map_err(|_| "Failed to acquire sync config lock".to_string())?
    .clone();
  Ok(cfg)
}

#[tauri::command]
fn set_sync_config(api_url: String, bearer_token: String, state: State<AppState>) -> Result<SyncStatus, String> {
  {
    let mut cfg = state
      .sync_config
      .lock()
      .map_err(|_| "Failed to acquire sync config lock".to_string())?;
    cfg.api_url = Some(api_url);
    cfg.bearer_token = Some(bearer_token);
  }

  let mut status = state
    .sync_status
    .lock()
    .map_err(|_| "Failed to acquire sync status lock".to_string())?;
  status.mode = "configured".to_string();
  status.is_online = true;
  status.last_sync_at = Some(now_rfc3339());
  Ok(status.clone())
}

#[tauri::command]
fn open_database_folder(state: State<AppState>) -> Result<String, String> {
  let dir = state.db_dir.to_string_lossy().to_string();

  #[cfg(target_os = "windows")]
  {
    std::process::Command::new("explorer")
      .arg(&dir)
      .spawn()
      .map_err(|e| format!("Failed to open Explorer: {e}"))?;
  }

  #[cfg(target_os = "macos")]
  {
    std::process::Command::new("open")
      .arg(&dir)
      .spawn()
      .map_err(|e| format!("Failed to open Finder: {e}"))?;
  }

  Ok(dir)
}

#[tauri::command]
async fn run_sync_once(state: State<'_, AppState>) -> Result<SyncRunResult, String> {
  let cfg = state
    .sync_config
    .lock()
    .map_err(|_| "Failed to acquire sync config lock".to_string())?
    .clone();

  if !cfg.is_configured() {
    return Ok(SyncRunResult {
      success: false,
      message: "Not configured".to_string(),
      pushed: 0,
      pulled: 0,
      conflicts: 0,
    });
  }

  {
    let mut status = state
      .sync_status
      .lock()
      .map_err(|_| "Failed to acquire sync status lock".to_string())?;
    status.is_syncing = true;
    status.mode = "syncing".to_string();
  }

  let result = async {
    let conn = open_conn(&state.db_path)?;
    let last_sync = get_last_sync_time(&conn)?;
    let pending = get_pending_mutations(&conn)?;

    let mut pushed = 0u32;
    let mut conflicts = 0u32;

    if !pending.is_empty() {
      let mutation_ids: Vec<String> = pending.iter().map(|m| m.id.clone()).collect();
      match push_to_server(&cfg, pending, last_sync.clone()).await {
        Ok(push_response) => {
          pushed = push_response.successful_ids.len() as u32;
          conflicts += push_response.conflicts.len() as u32;

          mark_mutations_synced(&conn, &push_response.successful_ids)?;

          for conflict in push_response.conflicts {
            log_conflict(
              &conn,
              conflict
                .get("table")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown"),
              conflict.get("id").and_then(|v| v.as_str()),
              &conflict
                .get("client_version")
                .cloned()
                .unwrap_or(Value::Null)
                .to_string(),
              &conflict
                .get("server_version")
                .cloned()
                .unwrap_or(Value::Null)
                .to_string(),
            )?;
          }
        }
        Err(err) => {
          increment_retry_count(&conn, &mutation_ids)?;
          return Ok(SyncRunResult {
            success: false,
            message: format!("Push failed: {err}"),
            pushed: 0,
            pulled: 0,
            conflicts: 0,
          });
        }
      }
    }

    let delta = pull_from_server(&cfg, last_sync).await?;
    let (applied, delta_conflicts) = apply_server_deltas(&conn, delta)?;
    let pulled = applied;
    conflicts += delta_conflicts;

    let now = now_rfc3339();
    set_last_sync_time(&conn, &now)?;

    Ok(SyncRunResult {
      success: true,
      message: format!("Synced: {} pushed, {} pulled", pushed, pulled),
      pushed,
      pulled,
      conflicts,
    })
  }
  .await;

  let mut status = state
    .sync_status
    .lock()
    .map_err(|_| "Failed to acquire sync status lock".to_string())?;
  status.is_syncing = false;
  status.pending_changes = open_conn(&state.db_path)
    .map(|c| pending_changes(&c))
    .unwrap_or(0);
  status.last_sync_at = Some(now_rfc3339());
  status.mode = if result.as_ref().map(|r| r.success).unwrap_or(false) {
    "online".to_string()
  } else {
    "offline".to_string()
  };
  status.is_online = result.as_ref().map(|r| r.success).unwrap_or(false);

  result
}

#[tauri::command]
fn list_journal_entries(params: JournalEntryListParams, state: State<AppState>) -> Result<Vec<JournalEntry>, String> {
  let conn = open_conn(&state.db_path)?;
  let skip = params.skip.unwrap_or(0);
  let limit = params.limit.unwrap_or(25);

  let mut sql = "
    SELECT entry_id, entity_id, entry_date, period, narration, total_debit, total_credit, created_at, lines_json
    FROM journal_entries
    WHERE entity_id = ?1 AND deleted_at IS NULL
  "
  .to_string();

  if params.period.is_some() {
    sql.push_str(" AND period = ?2 ");
  }
  sql.push_str(" ORDER BY entry_date DESC LIMIT ?3 OFFSET ?4 ");

  let mut stmt = conn.prepare(&sql).map_err(|e| format!("Failed to prepare list query: {e}"))?;

  if let Some(period) = params.period {
    let rows = stmt
      .query_map(params![params.entity_id, period, limit, skip], |row| {
        let lines_json: Option<String> = row.get(8)?;
        let lines = lines_json
          .as_ref()
          .and_then(|j| serde_json::from_str::<Vec<JournalLineDetail>>(j).ok());

        Ok(JournalEntry {
          entry_id: row.get(0)?,
          entity_id: row.get(1)?,
          entry_date: row.get(2)?,
          period: row.get(3)?,
          narration: row.get(4)?,
          total_debit: row.get(5)?,
          total_credit: row.get(6)?,
          created_at: row.get(7)?,
          lines,
        })
      })
      .map_err(|e| format!("Failed to list journal entries: {e}"))?;

    let mut entries = Vec::new();
    for row in rows {
      entries.push(row.map_err(|e| format!("Failed to parse journal entry row: {e}"))?);
    }
    return Ok(entries);
  }

  let rows = stmt
    .query_map(params![params.entity_id, limit, skip], |row| {
      let lines_json: Option<String> = row.get(8)?;
      let lines = lines_json
        .as_ref()
        .and_then(|j| serde_json::from_str::<Vec<JournalLineDetail>>(j).ok());

      Ok(JournalEntry {
        entry_id: row.get(0)?,
        entity_id: row.get(1)?,
        entry_date: row.get(2)?,
        period: row.get(3)?,
        narration: row.get(4)?,
        total_debit: row.get(5)?,
        total_credit: row.get(6)?,
        created_at: row.get(7)?,
        lines,
      })
    })
    .map_err(|e| format!("Failed to list journal entries: {e}"))?;

  let mut entries = Vec::new();
  for row in rows {
    entries.push(row.map_err(|e| format!("Failed to parse journal entry row: {e}"))?);
  }

  Ok(entries)
}

#[tauri::command]
fn get_journal_entry(entry_id: String, state: State<AppState>) -> Result<Option<JournalEntry>, String> {
  let conn = open_conn(&state.db_path)?;
  let mut stmt = conn
    .prepare(
      "
      SELECT entry_id, entity_id, entry_date, period, narration, total_debit, total_credit, created_at, lines_json
      FROM journal_entries
      WHERE entry_id = ?1 AND deleted_at IS NULL
      ",
    )
    .map_err(|e| format!("Failed to prepare detail query: {e}"))?;

  let result = stmt.query_row(params![entry_id], |row| {
    let lines_json: Option<String> = row.get(8)?;
    let lines = lines_json
      .as_ref()
      .and_then(|j| serde_json::from_str::<Vec<JournalLineDetail>>(j).ok());

    Ok(JournalEntry {
      entry_id: row.get(0)?,
      entity_id: row.get(1)?,
      entry_date: row.get(2)?,
      period: row.get(3)?,
      narration: row.get(4)?,
      total_debit: row.get(5)?,
      total_credit: row.get(6)?,
      created_at: row.get(7)?,
      lines,
    })
  });

  match result {
    Ok(entry) => Ok(Some(entry)),
    Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
    Err(e) => Err(format!("Failed to fetch journal entry: {e}")),
  }
}

#[tauri::command]
fn create_journal_entry(payload: JournalEntryCreateRequest, state: State<AppState>) -> Result<JournalEntry, String> {
  let conn = open_conn(&state.db_path)?;
  let now = now_rfc3339();
  let entry_id = Uuid::new_v4().to_string();

  let total_debit = payload.lines.iter().map(|l| l.debit).sum::<f64>();
  let total_credit = payload.lines.iter().map(|l| l.credit).sum::<f64>();
  let period = payload.entry_date.chars().take(7).collect::<String>();

  let detail_lines: Vec<JournalLineDetail> = payload
    .lines
    .iter()
    .map(|l| JournalLineDetail {
      line_id: Some(Uuid::new_v4().to_string()),
      account_code: l.account_code.clone(),
      debit: l.debit,
      credit: l.credit,
      description: l.description.clone(),
    })
    .collect();
  let lines_json = serde_json::to_string(&detail_lines).map_err(|e| format!("Failed to serialize lines: {e}"))?;

  conn
    .execute(
      "
      INSERT INTO journal_entries (
        entry_id, entity_id, entry_date, period, narration, total_debit, total_credit, created_at, lines_json, updated_at, sync_status, deleted_at
      ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, 'pending', NULL)
      ",
      params![
        entry_id,
        payload.entity_id,
        payload.entry_date,
        period,
        payload.narration,
        total_debit,
        total_credit,
        now,
        lines_json,
        now
      ],
    )
    .map_err(|e| format!("Failed to insert journal entry: {e}"))?;

  let queue_payload = serde_json::to_string(&payload).map_err(|e| format!("Failed to serialize sync payload: {e}"))?;
  queue_mutation(&conn, "journal_entries", "CREATE", Some(&entry_id), &queue_payload)?;

  Ok(JournalEntry {
    entry_id,
    entity_id: payload.entity_id,
    entry_date: payload.entry_date,
    period,
    narration: payload.narration,
    total_debit,
    total_credit,
    created_at: now,
    lines: Some(detail_lines),
  })
}

#[tauri::command]
fn list_entities(skip: Option<i64>, limit: Option<i64>, search: Option<String>, state: State<AppState>) -> Result<Vec<EntityRecord>, String> {
  let conn = open_conn(&state.db_path)?;
  let s = skip.unwrap_or(0);
  let l = limit.unwrap_or(100);

  let mut sql = "
    SELECT entity_id, name, gstin, pan, tan, address_json, currency, reporting_currency, created_at, updated_at
    FROM entities
    WHERE deleted_at IS NULL
  "
  .to_string();

  if let Some(term) = search {
    sql.push_str(" AND name LIKE ?1 ORDER BY updated_at DESC LIMIT ?2 OFFSET ?3 ");
    let mut stmt = conn.prepare(&sql).map_err(|e| format!("Failed to prepare list entities query: {e}"))?;
    let rows = stmt
      .query_map(params![format!("%{}%", term), l, s], |row| {
        let address_json: Option<String> = row.get(5)?;
        let address = address_json
          .as_ref()
          .and_then(|v| serde_json::from_str::<Value>(v).ok());
        Ok(EntityRecord {
          entity_id: row.get(0)?,
          name: row.get(1)?,
          gstin: row.get(2)?,
          pan: row.get(3)?,
          tan: row.get(4)?,
          address,
          currency: row.get(6)?,
          reporting_currency: row.get(7)?,
          created_at: row.get(8)?,
          updated_at: row.get(9)?,
        })
      })
      .map_err(|e| format!("Failed to query entities: {e}"))?;

    let mut entities = Vec::new();
    for row in rows {
      entities.push(row.map_err(|e| format!("Failed to parse entity row: {e}"))?);
    }
    return Ok(entities);
  }

  sql.push_str(" ORDER BY updated_at DESC LIMIT ?1 OFFSET ?2 ");
  let mut stmt = conn.prepare(&sql).map_err(|e| format!("Failed to prepare list entities query: {e}"))?;
  let rows = stmt
    .query_map(params![l, s], |row| {
      let address_json: Option<String> = row.get(5)?;
      let address = address_json
        .as_ref()
        .and_then(|v| serde_json::from_str::<Value>(v).ok());
      Ok(EntityRecord {
        entity_id: row.get(0)?,
        name: row.get(1)?,
        gstin: row.get(2)?,
        pan: row.get(3)?,
        tan: row.get(4)?,
        address,
        currency: row.get(6)?,
        reporting_currency: row.get(7)?,
        created_at: row.get(8)?,
        updated_at: row.get(9)?,
      })
    })
    .map_err(|e| format!("Failed to query entities: {e}"))?;

  let mut entities = Vec::new();
  for row in rows {
    entities.push(row.map_err(|e| format!("Failed to parse entity row: {e}"))?);
  }

  Ok(entities)
}

#[tauri::command]
fn test_database(state: State<AppState>) -> Result<String, String> {
  let conn = open_conn(&state.db_path)?;

  conn
    .execute(
      "CREATE TABLE IF NOT EXISTS desktop_db_test (id INTEGER PRIMARY KEY, value TEXT)",
      [],
    )
    .map_err(|e| format!("Failed creating test table: {e}"))?;

  conn
    .execute(
      "INSERT INTO desktop_db_test (value) VALUES (?1)",
      params!["hello_world"],
    )
    .map_err(|e| format!("Failed writing test row: {e}"))?;

  let mut stmt = conn
    .prepare("SELECT value FROM desktop_db_test ORDER BY id DESC LIMIT 1")
    .map_err(|e| format!("Failed preparing test read: {e}"))?;

  let value: String = stmt
    .query_row([], |row| row.get(0))
    .map_err(|e| format!("Failed reading test row: {e}"))?;

  Ok(format!("Database working! Retrieved: {value}"))
}

#[tauri::command]
fn get_entity(entity_id: String, state: State<AppState>) -> Result<Option<EntityRecord>, String> {
  let conn = open_conn(&state.db_path)?;
  let mut stmt = conn
    .prepare(
      "
      SELECT entity_id, name, gstin, pan, tan, address_json, currency, reporting_currency, created_at, updated_at
      FROM entities WHERE entity_id = ?1 AND deleted_at IS NULL
      ",
    )
    .map_err(|e| format!("Failed to prepare get entity query: {e}"))?;

  let result = stmt.query_row(params![entity_id], |row| {
    let address_json: Option<String> = row.get(5)?;
    let address = address_json
      .as_ref()
      .and_then(|v| serde_json::from_str::<Value>(v).ok());

    Ok(EntityRecord {
      entity_id: row.get(0)?,
      name: row.get(1)?,
      gstin: row.get(2)?,
      pan: row.get(3)?,
      tan: row.get(4)?,
      address,
      currency: row.get(6)?,
      reporting_currency: row.get(7)?,
      created_at: row.get(8)?,
      updated_at: row.get(9)?,
    })
  });

  match result {
    Ok(entity) => Ok(Some(entity)),
    Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
    Err(e) => Err(format!("Failed to fetch entity: {e}")),
  }
}

#[tauri::command]
fn create_entity(payload: EntityCreatePayload, state: State<AppState>) -> Result<EntityRecord, String> {
  let conn = open_conn(&state.db_path)?;
  let now = now_rfc3339();
  let entity_id = Uuid::new_v4().to_string();

  let currency = payload.currency.unwrap_or_else(|| "INR".to_string());
  let reporting_currency = payload.reporting_currency.unwrap_or_else(|| "INR".to_string());
  let address_json = payload.address.as_ref().map(|v| v.to_string());

  conn
    .execute(
      "
      INSERT INTO entities (entity_id, name, gstin, pan, tan, address_json, currency, reporting_currency, created_at, updated_at, deleted_at)
      VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?9, NULL)
      ",
      params![
        entity_id,
        payload.name,
        payload.gstin,
        payload.pan,
        payload.tan,
        address_json,
        currency,
        reporting_currency,
        now
      ],
    )
    .map_err(|e| format!("Failed to create entity: {e}"))?;

  let payload_value = serde_json::json!({
    "entity_id": entity_id,
    "name": payload.name,
    "gstin": payload.gstin,
    "pan": payload.pan,
    "tan": payload.tan,
    "address": payload.address,
    "currency": currency,
    "reporting_currency": reporting_currency,
  });
  queue_mutation(&conn, "entities", "CREATE", Some(&entity_id), &payload_value.to_string())?;

  Ok(EntityRecord {
    entity_id,
    name: payload_value.get("name").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
    gstin: payload_value.get("gstin").and_then(|v| v.as_str()).map(|v| v.to_string()),
    pan: payload_value.get("pan").and_then(|v| v.as_str()).map(|v| v.to_string()),
    tan: payload_value.get("tan").and_then(|v| v.as_str()).map(|v| v.to_string()),
    address: payload_value.get("address").cloned(),
    currency: payload_value
      .get("currency")
      .and_then(|v| v.as_str())
      .unwrap_or("INR")
      .to_string(),
    reporting_currency: payload_value
      .get("reporting_currency")
      .and_then(|v| v.as_str())
      .unwrap_or("INR")
      .to_string(),
    created_at: now.clone(),
    updated_at: now,
  })
}

#[tauri::command]
fn update_entity(entity_id: String, payload: EntityCreatePayload, state: State<AppState>) -> Result<EntityRecord, String> {
  let conn = open_conn(&state.db_path)?;
  let now = now_rfc3339();

  let currency = payload.currency.unwrap_or_else(|| "INR".to_string());
  let reporting_currency = payload.reporting_currency.unwrap_or_else(|| "INR".to_string());
  let address_json = payload.address.as_ref().map(|v| v.to_string());

  conn
    .execute(
      "
      UPDATE entities SET name = ?2, gstin = ?3, pan = ?4, tan = ?5, address_json = ?6, currency = ?7, reporting_currency = ?8, updated_at = ?9, deleted_at = NULL
      WHERE entity_id = ?1
      ",
      params![
        entity_id,
        payload.name,
        payload.gstin,
        payload.pan,
        payload.tan,
        address_json,
        currency,
        reporting_currency,
        now
      ],
    )
    .map_err(|e| format!("Failed to update entity: {e}"))?;

  let payload_value = serde_json::json!({
    "entity_id": entity_id,
    "name": payload.name,
    "gstin": payload.gstin,
    "pan": payload.pan,
    "tan": payload.tan,
    "address": payload.address,
    "currency": currency,
    "reporting_currency": reporting_currency,
  });
  queue_mutation(
    &conn,
    "entities",
    "UPDATE",
    payload_value.get("entity_id").and_then(|v| v.as_str()),
    &payload_value.to_string(),
  )?;

  Ok(EntityRecord {
    entity_id: payload_value
      .get("entity_id")
      .and_then(|v| v.as_str())
      .unwrap_or_default()
      .to_string(),
    name: payload_value.get("name").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
    gstin: payload_value.get("gstin").and_then(|v| v.as_str()).map(|v| v.to_string()),
    pan: payload_value.get("pan").and_then(|v| v.as_str()).map(|v| v.to_string()),
    tan: payload_value.get("tan").and_then(|v| v.as_str()).map(|v| v.to_string()),
    address: payload_value.get("address").cloned(),
    currency: payload_value
      .get("currency")
      .and_then(|v| v.as_str())
      .unwrap_or("INR")
      .to_string(),
    reporting_currency: payload_value
      .get("reporting_currency")
      .and_then(|v| v.as_str())
      .unwrap_or("INR")
      .to_string(),
    created_at: now.clone(),
    updated_at: now,
  })
}

#[tauri::command]
fn delete_entity(entity_id: String, state: State<AppState>) -> Result<(), String> {
  let conn = open_conn(&state.db_path)?;
  conn
    .execute(
      "UPDATE entities SET deleted_at = ?2, updated_at = ?2 WHERE entity_id = ?1",
      params![entity_id, now_rfc3339()],
    )
    .map_err(|e| format!("Failed to delete entity: {e}"))?;

  let payload = serde_json::json!({ "entity_id": entity_id });
  queue_mutation(
    &conn,
    "entities",
    "DELETE",
    payload.get("entity_id").and_then(|v| v.as_str()),
    &payload.to_string(),
  )?;

  Ok(())
}

fn resolve_app_dirs(app: &tauri::AppHandle) -> Result<(PathBuf, PathBuf), String> {
  let app_data_dir = app
    .path()
    .app_data_dir()
    .map_err(|e| format!("Failed to resolve app data dir: {e}"))?;

  if !app_data_dir.exists() {
    fs::create_dir_all(&app_data_dir).map_err(|e| format!("Failed to create app data dir: {e}"))?;
  }

  let db_path = app_data_dir.join("spoorthy.db");
  Ok((app_data_dir, db_path))
}

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      let (db_dir, db_path) = resolve_app_dirs(&app.handle())?;
      let conn = open_conn(&db_path)?;
      let pending = pending_changes(&conn);

      let app_state = AppState {
        db_path,
        db_dir,
        sync_config: Arc::new(Mutex::new(SyncConfig::default())),
        sync_status: Arc::new(Mutex::new(SyncStatus {
          pending_changes: pending,
          ..Default::default()
        })),
      };

      let loop_state = app_state.clone();
      thread::spawn(move || loop {
        thread::sleep(Duration::from_secs(30));

        if let Ok(conn) = open_conn(&loop_state.db_path) {
          let pending = pending_changes(&conn);
          let configured = loop_state
            .sync_config
            .lock()
            .ok()
            .map(|cfg| cfg.is_configured())
            .unwrap_or(false);

          if let Ok(mut status) = loop_state.sync_status.lock() {
            status.pending_changes = pending;
            status.is_online = configured;
            status.mode = if configured {
              "online".to_string()
            } else {
              "offline".to_string()
            };
          }
        }
      });

      app.manage(app_state);

      Ok(())
    })
    .invoke_handler(tauri::generate_handler![
      get_sync_status,
      get_sync_config,
      set_sync_config,
      open_database_folder,
      run_sync_once,
      list_journal_entries,
      get_journal_entry,
      create_journal_entry,
      list_entities,
      get_entity,
      create_entity,
      update_entity,
      delete_entity,
      test_database
    ])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
