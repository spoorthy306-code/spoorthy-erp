import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoicesService } from '@/services/invoices.service';
import type { InvoiceCreate } from '@/types/invoice.types';

export function useInvoices(entityId: string, startDate?: string, endDate?: string) {
  const queryClient = useQueryClient();

  const invoicesQuery = useQuery({
    queryKey: ['invoices', entityId, startDate, endDate],
    queryFn: () => invoicesService.list(entityId, startDate, endDate),
    enabled: Boolean(entityId),
    staleTime: 5 * 60 * 1000,
  });

  const createMutation = useMutation({
    mutationFn: (payload: InvoiceCreate) => invoicesService.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['invoices', entityId] });
    },
  });

  const generateIRNMutation = useMutation({
    mutationFn: (invoiceId: string) => invoicesService.generateIRN(invoiceId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['invoices', entityId] });
    },
  });

  return {
    invoices: invoicesQuery.data ?? [],
    isLoading: invoicesQuery.isLoading,
    error: invoicesQuery.error,
    createInvoice: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    generateIRN: generateIRNMutation.mutateAsync,
    isGeneratingIRN: generateIRNMutation.isPending,
  };
}
