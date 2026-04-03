import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import type { GSTReturnCreate } from '@/types/gst.types';

const schema = z.object({
  return_type: z.enum(['GSTR1', 'GSTR3B', 'GSTR9']),
  period: z.string().regex(/^\d{4}-\d{2}$/, 'Format: YYYY-MM'),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  entityId: string;
  onSubmit: (payload: GSTReturnCreate) => Promise<unknown>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export function GSTReturnForm({ entityId, onSubmit, onCancel, isSubmitting }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<FormValues>({
    mode: 'onChange',
    resolver: zodResolver(schema),
    defaultValues: {
      return_type: 'GSTR1',
      period: new Date().toISOString().slice(0, 7),
    },
  });

  const handleFormSubmit = (values: FormValues) =>
    onSubmit({ entity_id: entityId, ...values });

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h3 className="text-lg font-semibold text-ink">File New GST Return</h3>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Return Type</label>
          <select
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('return_type')}
          >
            <option value="GSTR1">GSTR-1 (Sales)</option>
            <option value="GSTR3B">GSTR-3B (Monthly)</option>
            <option value="GSTR9">GSTR-9 (Annual)</option>
          </select>
          {errors.return_type && <p className="mt-1 text-xs text-danger">{errors.return_type.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Period (YYYY-MM)</label>
          <input
            type="month"
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('period')}
          />
          {errors.period && <p className="mt-1 text-xs text-danger">{errors.period.message}</p>}
        </div>
      </div>
      <div className="mt-5 flex gap-3">
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="focus-ring rounded-lg bg-brand px-5 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {isSubmitting ? 'Creating…' : 'Create Return'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="focus-ring rounded-lg border border-slate-300 px-5 py-2 text-sm font-medium text-slate-700"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
