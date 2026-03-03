import { ChevronRight } from 'lucide-react';
import type { Breadcrumb } from '@/types';

interface BreadcrumbsProps {
  breadcrumbs: Breadcrumb[];
  onNavigate: (folderId: string | null) => void;
}

export function Breadcrumbs({ breadcrumbs, onNavigate }: BreadcrumbsProps) {
  if (breadcrumbs.length === 0) return null;

  return (
    <nav className="flex items-center gap-1 text-sm text-muted-foreground">
      {breadcrumbs.map((crumb, index) => {
        const isLast = index === breadcrumbs.length - 1;
        return (
          <span key={crumb.id ?? 'root'} className="flex items-center gap-1">
            {index > 0 && (
              <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50" />
            )}
            {isLast ? (
              <span className="font-medium text-foreground">{crumb.name}</span>
            ) : (
              <button
                className="hover:text-foreground transition-colors hover:underline"
                onClick={() => onNavigate(crumb.id)}
              >
                {crumb.name}
              </button>
            )}
          </span>
        );
      })}
    </nav>
  );
}
