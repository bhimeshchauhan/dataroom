import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Folder,
  FileText,
  MoreHorizontal,
  Pencil,
  Trash2,
  Plus,
  Upload,
  FolderOpen,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { Breadcrumbs } from './Breadcrumbs';
import { UploadZone } from '@/components/files/UploadZone';
import { CreateFolderDialog } from '@/components/dialogs/CreateFolderDialog';
import { RenameDialog } from '@/components/dialogs/RenameDialog';
import { DeleteDialog } from '@/components/dialogs/DeleteDialog';
import { api } from '@/api/client';
import { toast } from 'sonner';
import { formatFileSize, formatRelativeDate } from '@/lib/format';
import type {
  ContentsResponse,
  Folder as FolderType,
  FileItem,
  StorageUsage,
} from '@/types';

interface ContentPanelProps {
  contents: ContentsResponse | null;
  storageUsage: StorageUsage | null;
  dataroomId: string;
  folderId: string | null;
  onNavigate: (folderId: string | null) => void;
  onViewFile: (fileId: string, fileName: string) => void;
  onRefresh: () => void;
  loading: boolean;
  page: number;
  onPageChange: (page: number) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export function ContentPanel({
  contents,
  storageUsage,
  dataroomId,
  folderId,
  onNavigate,
  onViewFile,
  onRefresh,
  loading,
  page,
  onPageChange,
  searchQuery,
  onSearchChange,
}: ContentPanelProps) {
  const [createFolderOpen, setCreateFolderOpen] = useState(false);

  // Rename state
  const [renameTarget, setRenameTarget] = useState<{
    type: 'folder' | 'file';
    id: string;
    name: string;
  } | null>(null);

  // Delete state
  const [deleteTarget, setDeleteTarget] = useState<{
    type: 'folder' | 'file';
    id: string;
    name: string;
  } | null>(null);

  const handleRenameFolder = async (newName: string) => {
    if (!renameTarget) return;
    try {
      await api.renameFolder(renameTarget.id, newName);
      toast.success('Folder renamed.');
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Could not rename folder.');
      throw err;
    }
  };

  const handleRenameFile = async (newName: string) => {
    if (!renameTarget) return;
    try {
      await api.renameFile(renameTarget.id, newName);
      toast.success('File renamed.');
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Could not rename file.');
      throw err;
    }
  };

  const handleDeleteFolder = async () => {
    if (!deleteTarget) return;
    try {
      await api.deleteFolder(deleteTarget.id);
      toast.success('Folder moved to trash.');
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Could not remove folder.');
      throw err;
    }
  };

  const handleDeleteFile = async () => {
    if (!deleteTarget) return;
    try {
      await api.deleteFile(deleteTarget.id);
      toast.success('File moved to trash.');
      onRefresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Could not remove file.');
      throw err;
    }
  };

  const isEmpty =
    contents &&
    contents.folders.length === 0 &&
    contents.files.length === 0;

  return (
    <div className="flex-1 overflow-auto">
      <div className="p-6">
        {/* Breadcrumbs */}
        {contents && contents.breadcrumbs.length > 0 && (
          <Breadcrumbs
            breadcrumbs={contents.breadcrumbs}
            onNavigate={onNavigate}
          />
        )}

        {/* Action bar */}
        <div className="flex items-center gap-2 mt-4">
          <Input
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by name..."
            className="max-w-sm"
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCreateFolderOpen(true)}
          >
            <Plus className="mr-1.5 h-3.5 w-3.5" />
            New Folder
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              // Trigger the UploadZone's file input
              const input = document.querySelector(
                'input[type="file"][accept*="pdf"]'
              ) as HTMLInputElement;
              if (input) input.click();
            }}
          >
            <Upload className="mr-1.5 h-3.5 w-3.5" />
            Upload PDF
          </Button>
        </div>

        <Separator className="my-4" />

        {storageUsage && (
          <div className="rounded-lg border bg-muted/30 p-3 mb-4">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Storage usage</span>
              <span>
                {formatFileSize(storageUsage.used_bytes)} /{' '}
                {formatFileSize(storageUsage.quota_bytes)}
              </span>
            </div>
            <div className="mt-2 h-2 w-full rounded-full bg-muted">
              <div
                className="h-2 rounded-full bg-primary transition-all"
                style={{ width: `${Math.min(storageUsage.usage_percent, 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded-lg border px-4 py-3 animate-pulse"
              >
                <div className="h-5 w-5 rounded bg-muted" />
                <div className="h-4 w-40 rounded bg-muted" />
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && isEmpty && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-muted">
              <FolderOpen className="h-7 w-7 text-muted-foreground" />
            </div>
            <h3 className="mt-4 text-base font-semibold">
              {searchQuery ? 'No matches found' : 'This folder is empty'}
            </h3>
            <p className="mt-1 text-sm text-muted-foreground text-center max-w-xs">
              {searchQuery
                ? 'Try a different search term.'
                : 'Create a folder or upload a PDF.'}
            </p>
          </div>
        )}

        {/* Folders */}
        {!loading && contents && contents.folders.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
              Folders
            </p>
            {contents.folders.map((folder: FolderType) => (
              <FolderRow
                key={folder.id}
                folder={folder}
                onClick={() => onNavigate(folder.id)}
                onRename={() =>
                  setRenameTarget({
                    type: 'folder',
                    id: folder.id,
                    name: folder.name,
                  })
                }
                onDelete={() =>
                  setDeleteTarget({
                    type: 'folder',
                    id: folder.id,
                    name: folder.name,
                  })
                }
              />
            ))}
          </div>
        )}

        {/* Files */}
        {!loading && contents && contents.files.length > 0 && (
          <div className="space-y-1 mt-6">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
              Files
            </p>
            {contents.files.map((file: FileItem) => (
              <FileRow
                key={file.id}
                file={file}
                onClick={() => onViewFile(file.id, file.name)}
                onRename={() =>
                  setRenameTarget({
                    type: 'file',
                    id: file.id,
                    name: file.name,
                  })
                }
                onDelete={() =>
                  setDeleteTarget({
                    type: 'file',
                    id: file.id,
                    name: file.name,
                  })
                }
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {!loading && contents && contents.pagination && (() => {
          const p = contents.pagination;
          const maxPages =
            p.pages ??
            Math.max(
              Math.ceil((p.total_folders ?? 0) / p.per_page),
              Math.ceil((p.total_files ?? p.total ?? 0) / p.per_page),
              1
            );
          if (maxPages <= 1) return null;
          return (
            <div className="flex items-center justify-between mt-6 pt-4 border-t">
              <span className="text-xs text-muted-foreground">
                Page {page} of {maxPages}
              </span>
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => onPageChange(page - 1)}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= maxPages}
                  onClick={() => onPageChange(page + 1)}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          );
        })()}

        {/* Upload zone */}
        {!loading && (
          <UploadZone
            dataroomId={dataroomId}
            folderId={folderId}
            onUploaded={onRefresh}
          />
        )}
      </div>

      {/* Dialogs */}
      <CreateFolderDialog
        open={createFolderOpen}
        onClose={() => setCreateFolderOpen(false)}
        dataroomId={dataroomId}
        parentId={folderId}
        onCreated={onRefresh}
      />

      {renameTarget && (
        <RenameDialog
          open={true}
          onClose={() => setRenameTarget(null)}
          currentName={renameTarget.name}
          onRename={
            renameTarget.type === 'folder'
              ? handleRenameFolder
              : handleRenameFile
          }
          itemType={renameTarget.type}
        />
      )}

      {deleteTarget && (
        <DeleteDialog
          open={true}
          onClose={() => setDeleteTarget(null)}
          itemName={deleteTarget.name}
          itemType={deleteTarget.type}
          onConfirm={
            deleteTarget.type === 'folder'
              ? handleDeleteFolder
              : handleDeleteFile
          }
        />
      )}
    </div>
  );
}

// --- Sub-components ---

function FolderRow({
  folder,
  onClick,
  onRename,
  onDelete,
}: {
  folder: FolderType;
  onClick: () => void;
  onRename: () => void;
  onDelete: () => void;
}) {
  return (
    <div
      className="group flex items-center gap-3 rounded-lg border border-transparent hover:border-border hover:bg-accent/50 px-4 py-2.5 cursor-pointer transition-colors"
      onClick={onClick}
    >
      <Folder className="h-5 w-5 shrink-0 text-blue-500" />
      <span className="flex-1 truncate text-sm font-medium">{folder.name}</span>
      <span className="text-xs text-muted-foreground shrink-0 hidden sm:inline">
        {formatRelativeDate(folder.updated_at)}
      </span>
      <DropdownMenu>
        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
          <DropdownMenuItem onClick={onRename}>
            <Pencil className="mr-2 h-4 w-4" />
            Rename
          </DropdownMenuItem>
          <DropdownMenuItem
            className="text-destructive focus:text-destructive"
            onClick={onDelete}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

function FileRow({
  file,
  onClick,
  onRename,
  onDelete,
}: {
  file: FileItem;
  onClick: () => void;
  onRename: () => void;
  onDelete: () => void;
}) {
  return (
    <div
      className="group flex items-center gap-3 rounded-lg border border-transparent hover:border-border hover:bg-accent/50 px-4 py-2.5 cursor-pointer transition-colors"
      onClick={onClick}
    >
      <FileText className="h-5 w-5 shrink-0 text-red-500" />
      <span className="flex-1 truncate text-sm">{file.name}</span>
      <span className="text-xs text-muted-foreground shrink-0 hidden sm:inline">
        {formatFileSize(file.size_bytes)}
      </span>
      <span className="text-xs text-muted-foreground shrink-0 hidden md:inline ml-2">
        {formatRelativeDate(file.updated_at)}
      </span>
      <DropdownMenu>
        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
          <DropdownMenuItem onClick={onRename}>
            <Pencil className="mr-2 h-4 w-4" />
            Rename
          </DropdownMenuItem>
          <DropdownMenuItem
            className="text-destructive focus:text-destructive"
            onClick={onDelete}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
