import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface DeleteDialogProps {
  open: boolean;
  onClose: () => void;
  itemName: string;
  itemType: 'folder' | 'file' | 'dataroom';
  onConfirm: () => Promise<void>;
}

export function DeleteDialog({
  open,
  onClose,
  itemName,
  itemType,
  onConfirm,
}: DeleteDialogProps) {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
      onClose();
    } catch {
      // Error handling is done in the parent via toast
    } finally {
      setLoading(false);
    }
  };

  const typeLabel =
    itemType === 'dataroom' ? 'data room' : itemType;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Delete {typeLabel}</DialogTitle>
          <DialogDescription>
            Move{' '}
            <span className="font-semibold text-foreground">{itemName}</span>
            {itemType === 'folder'
              ? ' and all of its contents to trash.'
              : itemType === 'dataroom'
                ? ' and everything inside it to trash.'
                : ' to trash.'}
            {' '}You can restore it later.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={loading}
          >
            {loading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
