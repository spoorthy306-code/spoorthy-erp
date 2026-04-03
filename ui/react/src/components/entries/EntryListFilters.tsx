import type { EntryListFilterState, EntrySortField } from '@/types/journal.types';

export const DEFAULT_FILTER_STATE: EntryListFilterState = {
  period: '',
  narration: '',
  sortField: 'entry_date',
  sortDirection: 'desc',
};

interface EntryListFiltersProps {
  filters: EntryListFilterState;
  onChange: (filters: EntryListFilterState) => void;
  disabled?: boolean;
}

export function EntryListFilters({ filters, onChange, disabled = false }: EntryListFiltersProps) {
  const update = <K extends keyof EntryListFilterState>(key: K, value: EntryListFilterState[K]) => {
    onChange({ ...filters, [key]: value });
  };

  const hasActiveFilters = filters.period !== '' || filters.narration !== '';

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
      <div className="min-w-[140px] flex-1">
        <label htmlFor="filter-period" className="block text-xs font-medium text-slate-600">
          Period (YYYY-MM)
        </label>
        <input
          id="filter-period"
          value={filters.period}
          onChange={(e) => update('period', e.target.value)}
          disabled={disabled}
          placeholder="2026-04"
          className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>

      <div className="min-w-[200px] flex-1">
        <label htmlFor="filter-narration" className="block text-xs font-medium text-slate-600">
          Search narration
        </label>
        <input
          id="filter-narration"
          value={filters.narration}
          onChange={(e) => update('narration', e.target.value)}
          disabled={disabled}
          placeholder="Filter by narration..."
          className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>

      <div>
        <label htmlFor="filter-sort-field" className="block text-xs font-medium text-slate-600">
          Sort by
        </label>
        <select
          id="filter-sort-field"
          value={filters.sortField}
          onChange={(e) => update('sortField', e.target.value as EntrySortField)}
          disabled={disabled}
          className="focus-ring mt-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
        >
          <option value="entry_date">Date</option>
          <option value="total_debit">Debit</option>
          <option value="total_credit">Credit</option>
        </select>
      </div>

      <button
        type="button"
        onClick={() => update('sortDirection', filters.sortDirection === 'asc' ? 'desc' : 'asc')}
        disabled={disabled}
        aria-label={`Sort ${filters.sortDirection === 'asc' ? 'descending' : 'ascending'} — click to toggle`}
        className="focus-ring rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50"
      >
        {filters.sortDirection === 'asc' ? '↑ Asc' : '↓ Desc'}
      </button>

      {hasActiveFilters && (
        <button
          type="button"
          onClick={() => onChange(DEFAULT_FILTER_STATE)}
          disabled={disabled}
          className="focus-ring rounded-lg px-3 py-1.5 text-sm text-slate-500 hover:text-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
