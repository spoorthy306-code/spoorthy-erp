import { zodResolver } from '@hookform/resolvers/zod';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useFieldArray, useForm } from 'react-hook-form';
import { z } from 'zod';
import { useJournalEntries } from '@/hooks/useJournalEntries';
import { getEntryValidation } from '@/hooks/useEntryValidation';
import type {
  JournalEntry,
  JournalEntryCreateRequest,
  JournalEntryFormInitialState,
  JournalEntryFormValues,
  JournalEntryLineFormValue,
  JournalEntryMutationResult,
} from '@/types/journal.types';

const STORAGE_KEY = 'journal-entry-draft';

const journalEntryLineSchema = z.object({
  id: z.string().min(1),
  accountCode: z.string().trim().min(1, 'Account code is required'),
  type: z.enum(['DEBIT', 'CREDIT']),
  amount: z.coerce.number().positive('Amount must be greater than zero'),
  description: z.string().max(240, 'Line description must be 240 characters or less'),
});

const journalEntryFormSchema = z
  .object({
    entityId: z.string().trim().min(1, 'Entity ID is required'),
    entryDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Use YYYY-MM-DD'),
    period: z.string().regex(/^\d{4}-\d{2}$/, 'Use YYYY-MM'),
    reference: z.string().max(100, 'Reference must be 100 characters or less'),
    description: z.string().trim().min(3, 'Description must be at least 3 characters').max(500, 'Description must be 500 characters or less'),
    lines: z.array(journalEntryLineSchema).min(2, 'At least two line items are required'),
  })
  .superRefine((value, context) => {
    const validation = getEntryValidation(value.lines);
    if (!validation.isBalanced) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Journal entry must be balanced before it can be submitted.',
        path: ['lines'],
      });
    }
  });

export type JournalEntryFormSchema = z.infer<typeof journalEntryFormSchema>;

interface UseJournalEntryFormOptions extends JournalEntryFormInitialState {
  onSuccess?: (result: JournalEntryMutationResult) => void;
}

function makeLine(type: 'DEBIT' | 'CREDIT', amount = 0, accountCode = '', description = ''): JournalEntryLineFormValue {
  return {
    id: crypto.randomUUID(),
    accountCode,
    type,
    amount,
    description,
  };
}

function getCurrentPeriod(entryDate: string): string {
  return entryDate.slice(0, 7);
}

function getDefaultValues(entityId = ''): JournalEntryFormValues {
  const entryDate = new Date().toISOString().slice(0, 10);
  return {
    entityId,
    entryDate,
    period: getCurrentPeriod(entryDate),
    reference: '',
    description: '',
    lines: [makeLine('DEBIT'), makeLine('CREDIT')],
  };
}

function mapEntryToFormValues(entry: JournalEntry): JournalEntryFormValues {
  const fallbackLines = [
    makeLine('DEBIT', entry.total_debit),
    makeLine('CREDIT', entry.total_credit),
  ];

  return {
    entityId: entry.entity_id,
    entryDate: entry.entry_date,
    period: entry.period,
    reference: '',
    description: entry.narration ?? '',
    lines:
      entry.lines?.map((line) =>
        makeLine(
          Number(line.debit) > 0 ? 'DEBIT' : 'CREDIT',
          Number(line.debit) > 0 ? Number(line.debit) : Number(line.credit),
          line.account_code,
          line.description ?? ''
        )
      ) ?? fallbackLines,
  };
}

function getDraftValues(): JournalEntryFormValues | null {
  const draft = localStorage.getItem(STORAGE_KEY);
  if (!draft) {
    return null;
  }

  try {
    return JSON.parse(draft) as JournalEntryFormValues;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

function toCreatePayload(values: JournalEntryFormValues): JournalEntryCreateRequest {
  return {
    entity_id: values.entityId,
    entry_date: values.entryDate,
    narration: values.description,
    lines: values.lines.map((line) => ({
      account_code: line.accountCode,
      debit: line.type === 'DEBIT' ? Number(line.amount) : 0,
      credit: line.type === 'CREDIT' ? Number(line.amount) : 0,
      description: line.description || undefined,
    })),
  };
}

export function useJournalEntryForm({ entry, entityId, onSuccess }: UseJournalEntryFormOptions = {}) {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const shouldPersistDraftRef = useRef(true);
  const { createEntry, updateEntry, isCreating, isUpdating } = useJournalEntries();
  const defaultValues = useMemo(() => {
    if (entry) {
      return mapEntryToFormValues(entry);
    }

    return getDraftValues() ?? getDefaultValues(entityId);
  }, [entry, entityId]);

  const form = useForm<JournalEntryFormValues>({
    resolver: zodResolver(journalEntryFormSchema),
    mode: 'onChange',
    defaultValues,
  });
  const watchedValues = form.watch();

  const { fields, append, remove, replace } = useFieldArray({
    control: form.control,
    name: 'lines',
  });

  const watchedLines = form.watch('lines');
  const watchedEntryDate = form.watch('entryDate');
  const validation = useMemo(() => getEntryValidation(watchedLines ?? []), [watchedLines]);
  const canEditExistingEntry = Boolean(entry?.lines?.length);

  useEffect(() => {
    form.reset(defaultValues);
  }, [defaultValues, form]);

  useEffect(() => {
    if (!watchedEntryDate) {
      return;
    }

    const nextPeriod = getCurrentPeriod(watchedEntryDate);
    if (form.getValues('period') !== nextPeriod) {
      form.setValue('period', nextPeriod, { shouldDirty: true, shouldValidate: true });
    }
  }, [form, watchedEntryDate]);

  useEffect(() => {
    if (entry || !shouldPersistDraftRef.current || !form.formState.isDirty) {
      return;
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(watchedValues));
  }, [entry, form.formState.isDirty, watchedValues]);

  const appendLine = useCallback(() => {
    append(makeLine('DEBIT'));
  }, [append]);

  const removeLine = useCallback(
    (index: number) => {
      if (form.getValues('lines').length <= 2) {
        return;
      }

      remove(index);
    },
    [form, remove]
  );

  const updateLine = useCallback(
    (id: string, field: keyof JournalEntryLineFormValue, value: string | number) => {
      const lineIndex = form.getValues('lines').findIndex((line) => line.id === id);
      if (lineIndex === -1) {
        return;
      }

      form.setValue(`lines.${lineIndex}.${field}`, value as never, {
        shouldDirty: true,
        shouldTouch: true,
        shouldValidate: true,
      });
    },
    [form]
  );

  const resetForm = useCallback(() => {
    setSubmitError(null);
    shouldPersistDraftRef.current = false;
    localStorage.removeItem(STORAGE_KEY);
    const nextDefaults = entry ? mapEntryToFormValues(entry) : getDefaultValues(form.getValues('entityId'));
    form.reset(nextDefaults);
    replace(nextDefaults.lines);
    queueMicrotask(() => {
      shouldPersistDraftRef.current = true;
    });
  }, [entry, form, replace]);

  const submit = form.handleSubmit(async (values) => {
    setSubmitError(null);

    try {
      if (entry?.entry_id) {
        const updatedEntry = await updateEntry({
          entryId: entry.entry_id,
          payload: {
            entry_date: values.entryDate,
            narration: values.description,
            lines: toCreatePayload(values).lines,
          },
        });

        onSuccess?.({ entry: updatedEntry, mode: 'update' });
        return;
      }

      const createdEntry = await createEntry(toCreatePayload(values));
      shouldPersistDraftRef.current = false;
      localStorage.removeItem(STORAGE_KEY);
      onSuccess?.({ entry: createdEntry, mode: 'create' });

      const nextDefaults = getDefaultValues(values.entityId);
      form.reset(nextDefaults);
      replace(nextDefaults.lines);
      queueMicrotask(() => {
        shouldPersistDraftRef.current = true;
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Journal entry submission failed.';
      setSubmitError(message);
      shouldPersistDraftRef.current = true;
      throw error;
    }
  });

  return {
    form,
    fields,
    values: watchedValues,
    validation,
    submit,
    submitError,
    isSubmitting: isCreating || isUpdating || form.formState.isSubmitting,
    isDirty: form.formState.isDirty,
    isValid: form.formState.isValid,
    errors: form.formState.errors,
    appendLine,
    removeLine,
    updateLine,
    resetForm,
    draftStorageKey: STORAGE_KEY,
    isEditMode: Boolean(entry),
    canEditExistingEntry,
  };
}