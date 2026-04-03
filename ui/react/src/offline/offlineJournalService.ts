import { invoke } from '@tauri-apps/api/core';
import { journalEntriesService } from '@/services/journalEntries.service';
import type {
  JournalEntry,
  JournalEntryCreateRequest,
  JournalEntryListParams,
  JournalEntryUpdateRequest,
} from '@/types/journal.types';
import { IS_TAURI } from './tauriBridge';

interface JournalService {
  list: (params: JournalEntryListParams) => Promise<JournalEntry[]>;
  getById: (entryId: string) => Promise<JournalEntry>;
  create: (payload: JournalEntryCreateRequest) => Promise<JournalEntry>;
  update: (entryId: string, payload: JournalEntryUpdateRequest) => Promise<JournalEntry>;
  delete: (entryId: string) => Promise<void>;
  batchCreate: (entries: JournalEntryCreateRequest[]) => Promise<JournalEntry[]>;
  reconcile: (entityId: string) => Promise<{ message: string; entity_id: string }>;
}

const tauriJournalService: JournalService = {
  async list(params) {
    return invoke<JournalEntry[]>('list_journal_entries', {
      params: {
        entity_id: params.entityId,
        period: params.period ?? null,
        skip: params.skip ?? 0,
        limit: params.limit ?? 25,
      },
    });
  },

  async getById(entryId) {
    const result = await invoke<JournalEntry | null>('get_journal_entry', { entryId });
    if (!result) {
      throw new Error(`Journal entry ${entryId} not found in local database.`);
    }
    return result;
  },

  async create(payload) {
    return invoke<JournalEntry>('create_journal_entry', { payload });
  },

  async update(entryId, payload) {
    void entryId;
    void payload;
    throw new Error('Local update command is not yet implemented.');
  },

  async delete(entryId) {
    void entryId;
    throw new Error('Local delete command is not yet implemented.');
  },

  async batchCreate(entries) {
    const created: JournalEntry[] = [];
    for (const entry of entries) {
      created.push(await invoke<JournalEntry>('create_journal_entry', { payload: entry }));
    }
    return created;
  },

  async reconcile(entityId) {
    return {
      entity_id: entityId,
      message: 'Reconcile is queued in desktop mode and handled by sync loop.',
    };
  },
};

export function getJournalService(): JournalService {
  return IS_TAURI ? tauriJournalService : journalEntriesService;
}
