import { invoke } from '@tauri-apps/api/core';

const tauriWindow = typeof window !== 'undefined' ? (window as unknown as Record<string, unknown>) : undefined;
export const IS_TAURI = Boolean(tauriWindow && '__TAURI_INTERNALS__' in tauriWindow);

export interface SyncConfigPayload {
  apiUrl: string;
  bearerToken: string;
}

export interface SyncStatus {
  is_online: boolean;
  is_syncing: boolean;
  pending_changes: number;
  last_sync_at: string | null;
  mode: string;
}

export interface SyncRunResult {
  success: boolean;
  message: string;
  pushed: number;
  pulled: number;
  conflicts: number;
}

export async function tauriInvoke<T>(command: string, args?: Record<string, unknown>): Promise<T> {
  return invoke<T>(command, args);
}

export async function getSyncStatus(): Promise<SyncStatus | null> {
  if (!IS_TAURI) return null;
  return invoke<SyncStatus>('get_sync_status');
}

export async function runSyncOnce(): Promise<SyncRunResult | null> {
  if (!IS_TAURI) return null;
  return invoke<SyncRunResult>('run_sync_once');
}

export async function setSyncConfig(payload: SyncConfigPayload): Promise<SyncStatus | null> {
  if (!IS_TAURI) return null;
  return invoke<SyncStatus>('set_sync_config', {
    apiUrl: payload.apiUrl,
    bearerToken: payload.bearerToken,
  });
}

export async function getSyncConfig(): Promise<{ api_url?: string | null; bearer_token?: string | null } | null> {
  if (!IS_TAURI) return null;
  return invoke('get_sync_config');
}

export async function openDatabaseFolder(): Promise<string | null> {
  if (!IS_TAURI) return null;
  return invoke<string>('open_database_folder');
}
