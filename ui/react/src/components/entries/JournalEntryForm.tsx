import { useState } from 'react';
import { EntryLineItem } from '@/components/entries/EntryLineItem';
import { EntryValidationMessages } from '@/components/entries/EntryValidationMessages';
import { useJournalEntryForm } from '@/hooks/useJournalEntryForm';
import { useUIStore } from '@/store';
import { formatINR } from '@/utils/formatters';
import type { JournalEntry, JournalEntryMutationResult } from '@/types/journal.types';

interface JournalEntryFormProps {
  entry?: JournalEntry | null;
  entityId?: string;
  onSuccess?: (result: JournalEntryMutationResult) => void;
  onCancel?: () => void;
}

export function JournalEntryForm({ entry, entityId, onSuccess, onCancel }: JournalEntryFormProps) {
  const [showReferenceNotice, setShowReferenceNotice] = useState(false);
  const addNotification = useUIStore((state) => state.addNotification);
  const {
    form,
    fields,
    values,
    validation,
    submit,
    submitError,
    isSubmitting,
    isValid,
    errors,
    appendLine,
    removeLine,
    updateLine,
    resetForm,
    isEditMode,
    canEditExistingEntry,
  } = useJournalEntryForm({
    entry,
    entityId,
    onSuccess: (result) => {
      addNotification({
        type: 'success',
        title: result.mode === 'create' ? 'Journal entry created' : 'Journal entry updated',
        message: result.mode === 'create' ? 'The new journal entry was saved successfully.' : 'The journal entry changes were saved successfully.',
      });
      onSuccess?.(result);
    },
  });

  const lines = values.lines ?? [];
  const lineErrorMessage = typeof errors.lines?.message === 'string' ? errors.lines.message : null;
  const submitDisabled = isSubmitting || !isValid || !validation.isBalanced || (isEditMode && !canEditExistingEntry);

  const handleSubmit = async () => {
    try {
      await submit();
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Journal entry save failed',
        message: error instanceof Error ? error.message : 'The journal entry could not be saved.',
      });
    }
  };

  return (
    <form
      className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
      onSubmit={(event) => {
        event.preventDefault();
        void handleSubmit();
      }}
    >
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-ink">{isEditMode ? 'Edit Journal Entry' : 'New Journal Entry'}</h2>
          <p className="mt-1 text-sm text-slate-500">
            Capture a balanced entry first. Update and delete are already abstracted but still blocked by the live backend.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={resetForm}
            className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
          >
            Reset
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
          >
            Cancel
          </button>
        </div>
      </div>

      {submitError ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{submitError}</div>
      ) : null}

      {isEditMode && !canEditExistingEntry ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          This entry can be reviewed, but edit submit is blocked because the live API does not return line items or expose update endpoints yet.
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="text-sm font-medium text-slate-700" htmlFor="entry-entity-id">
            Entity ID
          </label>
          <input
            id="entry-entity-id"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            {...form.register('entityId')}
            placeholder="Entity UUID"
            readOnly={isEditMode}
          />
          {errors.entityId ? <p className="mt-1 text-sm text-rose-600">{errors.entityId.message}</p> : null}
        </div>

        <div>
          <label className="text-sm font-medium text-slate-700" htmlFor="entry-date">
            Entry Date
          </label>
          <input
            id="entry-date"
            type="date"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            {...form.register('entryDate')}
          />
          {errors.entryDate ? <p className="mt-1 text-sm text-rose-600">{errors.entryDate.message}</p> : null}
        </div>

        <div>
          <label className="text-sm font-medium text-slate-700" htmlFor="entry-period">
            Period
          </label>
          <input
            id="entry-period"
            className="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-slate-600"
            {...form.register('period')}
            readOnly
          />
        </div>

        <div>
          <div className="flex items-center justify-between gap-3">
            <label className="text-sm font-medium text-slate-700" htmlFor="entry-reference">
              Reference
            </label>
            <button
              type="button"
              onClick={() => setShowReferenceNotice((current) => !current)}
              className="text-xs font-medium text-brand"
            >
              API note
            </button>
          </div>
          <input
            id="entry-reference"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            {...form.register('reference')}
            placeholder="Optional internal reference"
          />
          {showReferenceNotice ? (
            <p className="mt-1 text-xs text-slate-500">The current backend does not persist a dedicated reference field yet, so this value is retained only in the draft/edit-ready frontend workflow.</p>
          ) : null}
        </div>
      </div>

      <div>
        <label className="text-sm font-medium text-slate-700" htmlFor="entry-description">
          Description
        </label>
        <textarea
          id="entry-description"
          rows={3}
          className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          {...form.register('description')}
          placeholder="Describe the business event that this entry records"
        />
        {errors.description ? <p className="mt-1 text-sm text-rose-600">{errors.description.message}</p> : null}
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-ink">Line Items</h3>
            <p className="text-sm text-slate-500">Add at least one debit line and one credit line.</p>
          </div>
          <button
            type="button"
            onClick={appendLine}
            className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
          >
            Add Line Item
          </button>
        </div>

        {fields.map((field, index) => {
          const line = lines[index] ?? field;
          return (
            <EntryLineItem
              key={field.id}
              line={line}
              index={index}
              onChange={updateLine}
              onRemove={() => removeLine(index)}
              disableRemove={fields.length <= 2}
            />
          );
        })}

        {lineErrorMessage ? <p className="text-sm text-rose-600">{lineErrorMessage}</p> : null}
      </div>

      <EntryValidationMessages lines={lines} />

      <section className="grid gap-4 rounded-xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-3">
        <div>
          <p className="text-sm text-slate-500">Total Debits</p>
          <p className="mt-1 text-xl font-semibold text-ink">{formatINR(validation.totalDebit)}</p>
        </div>
        <div>
          <p className="text-sm text-slate-500">Total Credits</p>
          <p className="mt-1 text-xl font-semibold text-ink">{formatINR(validation.totalCredit)}</p>
        </div>
        <div>
          <p className="text-sm text-slate-500">Difference</p>
          <p className={`mt-1 text-xl font-semibold ${validation.isBalanced ? 'text-emerald-600' : 'text-rose-600'}`}>
            {formatINR(validation.difference)}
          </p>
        </div>
      </section>

      <div className="flex flex-wrap justify-end gap-3">
        <button
          type="submit"
          disabled={submitDisabled}
          className="focus-ring rounded-lg bg-brand px-5 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? 'Saving...' : isEditMode ? 'Save Changes' : 'Save Entry'}
        </button>
      </div>
    </form>
  );
}