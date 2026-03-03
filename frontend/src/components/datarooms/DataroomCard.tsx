import { useState } from 'react';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { MoreHorizontal, Pencil, Trash2, FolderOpen } from 'lucide-react';
import { RenameDialog } from '@/components/dialogs/RenameDialog';
import { DeleteDialog } from '@/components/dialogs/DeleteDialog';
import { api } from '@/api/client';
import { toast } from 'sonner';
import { formatRelativeDate } from '@/lib/format';
import type { Dataroom } from '@/types';

interface DataroomCardProps {
  dataroom: Dataroom;
  onClick: () => void;
  onRefresh: () => void;
}

export function DataroomCard({ dataroom, onClick, onRefresh }: DataroomCardProps) {
  const [renameOpen, setRenameOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const handleRename = async (newName: string) => {
    try {
      await api.updateDataroom(dataroom.id, { name: newName });
      toast.success('Renamed successfully');
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to rename');
      throw err;
    }
  };

  const handleDelete = async () => {
    try {
      await api.deleteDataroom(dataroom.id);
      toast.success('Deleted successfully');
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to delete');
      throw err;
    }
  };

  return (
    <>
      <Card
        className="group cursor-pointer transition-all hover:shadow-md hover:border-primary/20"
        onClick={onClick}
      >
        <CardHeader className="relative">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <FolderOpen className="h-5 w-5 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <CardTitle className="text-base truncate">{dataroom.name}</CardTitle>
                <CardDescription className="line-clamp-2 mt-1">
                  {dataroom.description || 'No description'}
                </CardDescription>
              </div>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                <DropdownMenuItem onClick={() => setRenameOpen(true)}>
                  <Pencil className="mr-2 h-4 w-4" />
                  Rename
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="text-destructive focus:text-destructive"
                  onClick={() => setDeleteOpen(true)}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            Updated {formatRelativeDate(dataroom.updated_at)}
          </p>
        </CardHeader>
      </Card>

      <RenameDialog
        open={renameOpen}
        onClose={() => setRenameOpen(false)}
        currentName={dataroom.name}
        onRename={handleRename}
        itemType="data room"
      />

      <DeleteDialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        itemName={dataroom.name}
        itemType="dataroom"
        onConfirm={handleDelete}
      />
    </>
  );
}
