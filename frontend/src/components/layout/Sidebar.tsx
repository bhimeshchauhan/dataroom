import { ScrollArea } from '@/components/ui/scroll-area';
import { FolderTreeItem } from './FolderTreeItem';
import { cn } from '@/lib/utils';
import { FolderRoot } from 'lucide-react';
import type { TreeNode } from '@/types';

interface SidebarProps {
  tree: TreeNode[];
  currentFolderId: string | null;
  onSelectFolder: (folderId: string | null) => void;
  dataroomName: string;
}

export function Sidebar({
  tree,
  currentFolderId,
  onSelectFolder,
  dataroomName,
}: SidebarProps) {
  return (
    <div className="flex h-full w-[260px] shrink-0 flex-col border-r bg-sidebar">
      <div className="px-3 py-3 border-b">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground px-2">
          Folders
        </p>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-2">
          {/* Root item */}
          <button
            className={cn(
              'flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-sm hover:bg-accent transition-colors text-left',
              currentFolderId === null &&
                'bg-accent font-medium text-accent-foreground'
            )}
            onClick={() => onSelectFolder(null)}
          >
            <span className="w-4.5 shrink-0" />
            <FolderRoot className="h-4 w-4 shrink-0 text-muted-foreground" />
            <span className="truncate">{dataroomName}</span>
          </button>

          {/* Tree nodes */}
          {tree.map((node) => (
            <FolderTreeItem
              key={node.id}
              node={node}
              depth={1}
              currentFolderId={currentFolderId}
              onSelectFolder={(id) => onSelectFolder(id)}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
