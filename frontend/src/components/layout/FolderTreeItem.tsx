import { useState } from 'react';
import { ChevronRight, Folder } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TreeNode } from '@/types';

interface FolderTreeItemProps {
  node: TreeNode;
  depth: number;
  currentFolderId: string | null;
  onSelectFolder: (folderId: string) => void;
}

export function FolderTreeItem({
  node,
  depth,
  currentFolderId,
  onSelectFolder,
}: FolderTreeItemProps) {
  const [expanded, setExpanded] = useState(true);
  const isSelected = currentFolderId === node.id;
  const hasChildren = node.children.length > 0;

  return (
    <div>
      <div
        role="treeitem"
        tabIndex={0}
        aria-selected={isSelected}
        aria-expanded={hasChildren ? expanded : undefined}
        className={cn(
          'flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-sm hover:bg-accent transition-colors text-left cursor-pointer select-none',
          isSelected && 'bg-accent font-medium text-accent-foreground'
        )}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={(e) => {
          if ((e.target as HTMLElement).closest('button')) return;
          onSelectFolder(node.id);
        }}
        onKeyDown={(e) => {
          if ((e.target as HTMLElement).closest('button')) return;
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSelectFolder(node.id);
          }
        }}
      >
        {hasChildren ? (
          <button
            type="button"
            tabIndex={0}
            aria-label={expanded ? 'Collapse folder' : 'Expand folder'}
            className="shrink-0 p-0.5 rounded hover:bg-muted-foreground/10"
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
          >
            <ChevronRight
              className={cn(
                'h-3.5 w-3.5 text-muted-foreground transition-transform',
                expanded && 'rotate-90'
              )}
            />
          </button>
        ) : (
          <span className="w-4.5 shrink-0" />
        )}
        <Folder className="h-4 w-4 shrink-0 text-muted-foreground" />
        <span className="truncate">{node.name}</span>
      </div>

      {expanded && hasChildren && (
        <div role="group">
          {node.children.map((child) => (
            <FolderTreeItem
              key={child.id}
              node={child}
              depth={depth + 1}
              currentFolderId={currentFolderId}
              onSelectFolder={onSelectFolder}
            />
          ))}
        </div>
      )}
    </div>
  );
}
