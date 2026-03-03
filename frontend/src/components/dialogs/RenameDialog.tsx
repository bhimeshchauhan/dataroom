import { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface RenameDialogProps {
  open: boolean;
  onClose: () => void;
  currentName: string;
  onRename: (newName: string) => Promise<void>;
  itemType?: string;
}

export function RenameDialog({
  open,
  onClose,
  currentName,
  onRename,
  itemType = 'item',
}: RenameDialogProps) {
  const [name, setName] = useState(currentName);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setName(currentName);
      // Select all text after dialog opens
      setTimeout(() => {
        inputRef.current?.select();
      }, 50);
    }
  }, [open, currentName]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || name.trim() === currentName) return;

    setLoading(true);
    try {
      await onRename(name.trim());
      onClose();
    } catch {
      // Error handling is done in the parent via toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Rename {itemType}</DialogTitle>
            <DialogDescription>
              Enter a new name for this {itemType}.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              ref={inputRef}
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
              disabled={loading}
            />
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!name.trim() || name.trim() === currentName || loading}
            >
              {loading ? 'Renaming...' : 'Rename'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
