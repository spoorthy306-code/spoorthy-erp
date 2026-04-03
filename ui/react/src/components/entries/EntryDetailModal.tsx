import { useEffect } from 'react';
import { EntryDetail } from '@/components/entries/EntryDetail';

interface EntryDetailModalProps {
  entryId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function EntryDetailModal({ entryId, isOpen, onClose }: EntryDetailModalProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !entryId) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4" role="dialog" aria-modal="true">
      <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />
      <div className="relative max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <EntryDetail entryId={entryId} onClose={onClose} />
      </div>
    </div>
  );
}