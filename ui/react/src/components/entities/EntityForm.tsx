import { useEffect } from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import type { Entity, EntityCreate } from '@/types';

// Real 15-char GSTIN: 2-digit state code + PAN (10) + entity code + Z + check digit
const GSTIN_RE = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/;
const PAN_RE = /^[A-Z]{5}[0-9]{4}[A-Z]$/;
const TAN_RE = /^[A-Z]{4}[0-9]{5}[A-Z]$/;

const schema = z.object({
  name: z.string().min(1).max(255),
  gstin: z.string().regex(GSTIN_RE, 'Must be a valid 15-character GSTIN').optional().or(z.literal('')),
  pan: z.string().regex(PAN_RE, 'Must be a valid 10-character PAN').optional().or(z.literal('')),
  tan: z.string().regex(TAN_RE, 'Must be a valid 10-character TAN').optional().or(z.literal('')),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  phone: z.string().regex(/^[6-9]\d{9}$/, 'Must be a 10-digit Indian mobile number').optional().or(z.literal('')),
  street: z.string().optional().or(z.literal('')),
  city: z.string().optional().or(z.literal('')),
  state: z.string().optional().or(z.literal('')),
  postal: z.string().optional().or(z.literal('')),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  entity?: Entity;
  onSubmit: (payload: EntityCreate) => Promise<unknown>;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

function toFormValues(entity?: Entity): FormValues {
  return {
    name: entity?.name ?? '',
    gstin: entity?.gstin ?? '',
    pan: entity?.pan ?? '',
    tan: entity?.tan ?? '',
    email: entity?.address?.email ?? '',
    phone: entity?.address?.phone ?? '',
    street: entity?.address?.street ?? '',
    city: entity?.address?.city ?? '',
    state: entity?.address?.state ?? '',
    postal: entity?.address?.postal ?? '',
  };
}

export function EntityForm({ entity, onSubmit, onCancel, isSubmitting }: Props) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid },
  } = useForm<FormValues>({
    mode: 'onChange',
    resolver: zodResolver(schema),
    defaultValues: toFormValues(entity),
  });

  useEffect(() => {
    reset(toFormValues(entity));
  }, [entity, reset]);

  const handleFormSubmit = (values: FormValues) => {
    const address: EntityCreate['address'] = {};
    if (values.email) address.email = values.email;
    if (values.phone) address.phone = values.phone;
    if (values.street) address.street = values.street;
    if (values.city) address.city = values.city;
    if (values.state) address.state = values.state;
    if (values.postal) address.postal = values.postal;

    const payload: EntityCreate = {
      name: values.name,
      ...(values.gstin ? { gstin: values.gstin } : {}),
      ...(values.pan ? { pan: values.pan } : {}),
      ...(values.tan ? { tan: values.tan } : {}),
      ...(Object.keys(address).length > 0 ? { address } : {}),
    };
    return onSubmit(payload);
  };

  const isEdit = Boolean(entity);

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h3 className="text-lg font-semibold text-ink">{isEdit ? 'Edit Entity' : 'Create Entity'}</h3>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        {/* Name */}
        <div className="md:col-span-2">
          <label htmlFor="ent-name" className="block text-sm font-medium text-slate-700">
            Entity Name <span className="text-danger">*</span>
          </label>
          <input
            id="ent-name"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('name')}
          />
          {errors.name && <p className="mt-1 text-xs text-danger">{errors.name.message}</p>}
        </div>

        {/* GSTIN */}
        <div>
          <label htmlFor="ent-gstin" className="block text-sm font-medium text-slate-700">
            GSTIN <span className="text-slate-400 text-xs">(15 chars)</span>
          </label>
          <input
            id="ent-gstin"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm uppercase"
            maxLength={15}
            {...register('gstin')}
          />
          {errors.gstin && <p className="mt-1 text-xs text-danger">{errors.gstin.message}</p>}
        </div>

        {/* PAN */}
        <div>
          <label htmlFor="ent-pan" className="block text-sm font-medium text-slate-700">
            PAN <span className="text-slate-400 text-xs">(10 chars)</span>
          </label>
          <input
            id="ent-pan"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm uppercase"
            maxLength={10}
            {...register('pan')}
          />
          {errors.pan && <p className="mt-1 text-xs text-danger">{errors.pan.message}</p>}
        </div>

        {/* TAN */}
        <div>
          <label htmlFor="ent-tan" className="block text-sm font-medium text-slate-700">
            TAN <span className="text-slate-400 text-xs">(10 chars)</span>
          </label>
          <input
            id="ent-tan"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm uppercase"
            maxLength={10}
            {...register('tan')}
          />
          {errors.tan && <p className="mt-1 text-xs text-danger">{errors.tan.message}</p>}
        </div>

        {/* Email */}
        <div>
          <label htmlFor="ent-email" className="block text-sm font-medium text-slate-700">Email</label>
          <input
            id="ent-email"
            type="email"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('email')}
          />
          {errors.email && <p className="mt-1 text-xs text-danger">{errors.email.message}</p>}
        </div>

        {/* Phone */}
        <div>
          <label htmlFor="ent-phone" className="block text-sm font-medium text-slate-700">Phone</label>
          <input
            id="ent-phone"
            type="tel"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            maxLength={10}
            {...register('phone')}
          />
          {errors.phone && <p className="mt-1 text-xs text-danger">{errors.phone.message}</p>}
        </div>

        {/* Street */}
        <div className="md:col-span-2">
          <label htmlFor="ent-street" className="block text-sm font-medium text-slate-700">Street Address</label>
          <input
            id="ent-street"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('street')}
          />
        </div>

        {/* City / State / Postal */}
        <div>
          <label htmlFor="ent-city" className="block text-sm font-medium text-slate-700">City</label>
          <input
            id="ent-city"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('city')}
          />
        </div>
        <div>
          <label htmlFor="ent-state" className="block text-sm font-medium text-slate-700">State</label>
          <input
            id="ent-state"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            {...register('state')}
          />
        </div>
        <div>
          <label htmlFor="ent-postal" className="block text-sm font-medium text-slate-700">Postal Code</label>
          <input
            id="ent-postal"
            className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            maxLength={6}
            {...register('postal')}
          />
        </div>
      </div>

      <div className="mt-6 flex gap-3">
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="focus-ring rounded-lg bg-brand px-5 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {isSubmitting ? 'Saving…' : isEdit ? 'Update Entity' : 'Create Entity'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="focus-ring rounded-lg border border-slate-300 px-5 py-2 text-sm font-medium text-slate-700"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
