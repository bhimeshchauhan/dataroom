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
import { Input } from '@/components/ui/input';
import { api } from '@/api/client';
import { toast } from 'sonner';

interface CreateFolderDialogProps {
  open: boolean;
  onClose: () => void;
  dataroomId: string;
  parentId: string | null;
  onCreated: () => void;
}

export function CreateFolderDialog({
  open,
  onClose,
  dataroomId,
  parentId,
  onCreated,
}: CreateFolderDialogProps) {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      await api.createFolder(dataroomId, name.trim(), parentId);
      toast.success('Folder created');
      setName('');
      onCreated();
      onClose();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to create folder');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setName('');
      onClose();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>New Folder</DialogTitle>
            <DialogDescription>
              Create a new folder to organize your files.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              placeholder="Folder name"
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
            <Button type="submit" disabled={!name.trim() || loading}>
              {loading ? 'Creating...' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
