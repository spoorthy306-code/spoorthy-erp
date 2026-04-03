import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm, useWatch } from 'react-hook-form';
import type { InvoiceCreate } from '@/types/invoice.types';

const GSTIN_RE = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/;

const schema = z.object({
  invoice_no: z.string().min(1, 'Invoice number is required'),
  invoice_date: z.string().min(1, 'Date is required'),
  buyer_name: z.string().min(1, 'Buyer name is required'),
  buyer_gstin: z.string().regex(GSTIN_RE, 'Must be a valid 15-char GSTIN').optional().or(z.literal('')),
  total_amount: z.coerce.number().positive('Must be greater than 0'),
  tax_amount: z.coerce.number().min(0, 'Cannot be negative'),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  entityId: string;
  onSubmit: (payload: InvoiceCreate) => Promise<unknown>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export function InvoiceForm({ entityId, onSubmit, onCancel, isSubmitting }: Props) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isValid },
  } = useForm<FormValues>({
    mode: 'onChange',
    resolver: zodResolver(schema),
    defaultValues: {
      invoice_date: new Date().toISOString().slice(0, 10),
      tax_amount: 0,
    },
  });

  const totalAmount = useWatch({ control, name: 'total_amount' });
  const taxAmount = useWatch({ control, name: 'tax_amount' });
  const netAmount = (Number(totalAmount) || 0) - (Number(taxAmount) || 0);

  const handleFormSubmit = (values: FormValues) => {
    const payload: InvoiceCreate = {
      entity_id: entityId,
      invoice_no: values.invoice_no,
      invoice_date: values.invoice_date,
      buyer_name: values.buyer_name,
      total_amount: values.total_amount,
      tax_amount: values.tax_amount,
      ...(values.buyer_gstin ? { buyer_gstin: values.buyer_gstin } : {}),
    };
    return onSubmit(payload);
  };

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h3 className="text-lg font-semibold text-ink">New Invoice</h3>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Invoice No <span className="text-danger">*</span>
          </label>
          <input
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('invoice_no')}
          />
          {errors.invoice_no && <p className="mt-1 text-xs text-danger">{errors.invoice_no.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Invoice Date <span className="text-danger">*</span>
          </label>
          <input
            type="date"
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('invoice_date')}
          />
          {errors.invoice_date && <p className="mt-1 text-xs text-danger">{errors.invoice_date.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Buyer Name <span className="text-danger">*</span>
          </label>
          <input
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('buyer_name')}
          />
          {errors.buyer_name && <p className="mt-1 text-xs text-danger">{errors.buyer_name.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Buyer GSTIN</label>
          <input
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm uppercase"
            maxLength={15}
            {...register('buyer_gstin')}
          />
          {errors.buyer_gstin && <p className="mt-1 text-xs text-danger">{errors.buyer_gstin.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Total Amount (₹) <span className="text-danger">*</span>
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('total_amount')}
          />
          {errors.total_amount && <p className="mt-1 text-xs text-danger">{errors.total_amount.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Tax Amount (₹)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('tax_amount')}
          />
          {errors.tax_amount && <p className="mt-1 text-xs text-danger">{errors.tax_amount.message}</p>}
        </div>
      </div>

      {/* Totals preview */}
      <div className="mt-4 rounded-lg bg-slate-50 p-3 text-sm">
        <div className="flex justify-between text-slate-600">
          <span>Taxable Amount</span>
          <span className="font-mono">₹{netAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="flex justify-between text-slate-600">
          <span>Tax</span>
          <span className="font-mono">₹{(Number(taxAmount) || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="mt-1 flex justify-between border-t border-slate-200 pt-1 font-semibold text-ink">
          <span>Total</span>
          <span className="font-mono">₹{(Number(totalAmount) || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
      </div>

      <div className="mt-5 flex gap-3">
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="focus-ring rounded-lg bg-brand px-5 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {isSubmitting ? 'Creating…' : 'Create Invoice'}
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
