import { api } from '@/services/api';
import type {
  JournalEntry,
  JournalEntryCreateRequest,
  JournalEntryLineDetail,
  JournalEntryListParams,
  JournalEntryUpdateRequest,
} from '@/types/journal.types';

function normalizeLines(data: { lines?: JournalEntryLineDetail[]; journal_lines?: JournalEntryLineDetail[] }): JournalEntryLineDetail[] | undefined {
  if (Array.isArray(data.lines)) {
    return data.lines;
  }

  if (Array.isArray(data.journal_lines)) {
    return data.journal_lines;
  }

  return undefined;
}

function normalizeEntry(data: JournalEntry & { journal_lines?: JournalEntryLineDetail[] }): JournalEntry {
  return {
    ...data,
    lines: normalizeLines(data),
  };
}

export const journalEntriesService = {
  async list(params: JournalEntryListParams): Promise<JournalEntry[]> {
    const { data } = await api.get<JournalEntry[]>('/api/v1/journal-entries/', {
      params: {
        entity_id: params.entityId,
        period: params.period,
        skip: params.skip ?? 0,
        limit: params.limit ?? 25,
      },
    });
    return data.map((entry) => normalizeEntry(entry));
  },

  async getById(entryId: string): Promise<JournalEntry> {
    const { data } = await api.get<JournalEntry & { journal_lines?: JournalEntryLineDetail[] }>(`/api/v1/journal-entries/${entryId}`);
    return normalizeEntry(data);
  },

  async create(payload: JournalEntryCreateRequest): Promise<JournalEntry> {
    const { data } = await api.post<JournalEntry>('/api/v1/journal-entries/', payload);
    return normalizeEntry(data);
  },

  async update(entryId: string, payload: JournalEntryUpdateRequest): Promise<JournalEntry> {
    void entryId;
    void payload;
    throw new Error('Journal entry update is not available until the backend exposes PUT /api/v1/journal-entries/{id}.');
  },

  async delete(entryId: string): Promise<void> {
    void entryId;
    throw new Error('Journal entry deletion is not available until the backend exposes DELETE /api/v1/journal-entries/{id}.');
  },

  async batchCreate(entries: JournalEntryCreateRequest[]): Promise<JournalEntry[]> {
    void entries;
    throw new Error('Batch journal entry creation is not available until the backend exposes POST /api/v1/journal-entries/batch.');
  },

  async reconcile(entityId: string): Promise<{ message: string; entity_id: string }> {
    const { data } = await api.post<{ message: string; entity_id: string }>(`/api/v1/journal-entries/reconcile/${entityId}`);
    return data;
  },
};
