import { useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Database } from 'lucide-react';
import { DataroomCard } from './DataroomCard';
import { CreateDataroomDialog } from './CreateDataroomDialog';
import { api } from '@/api/client';
import { toast } from 'sonner';
import { formatFileSize } from '@/lib/format';
import type { Dataroom, StorageUsage } from '@/types';

interface DataroomListProps {
  onSelect: (dataroomId: string) => void;
  onLogout: () => void;
}

export function DataroomList({ onSelect, onLogout }: DataroomListProps) {
  const [datarooms, setDatarooms] = useState<Dataroom[]>([]);
  const [storageUsage, setStorageUsage] = useState<StorageUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

  const fetchDatarooms = useCallback(async () => {
    try {
      const [res, usage] = await Promise.all([
        api.listDatarooms(),
        api.getStorageUsage(),
      ]);
      setDatarooms(res.datarooms);
      setStorageUsage(usage);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : 'Failed to load data rooms'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDatarooms();
  }, [fetchDatarooms]);

  return (
    <div className="min-h-screen bg-muted/30">
      {/* Header */}
      <div className="border-b bg-background">
        <div className="mx-auto max-w-6xl px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Data Rooms</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Organize folders and PDFs
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={onLogout}>
                Logout
              </Button>
              <Button onClick={() => setCreateOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                New Data Room
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-6xl px-6 py-8">
        {storageUsage && (
          <div className="rounded-xl border bg-card p-4 mb-6">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Overall Storage</h2>
              <span className="text-xs text-muted-foreground">
                {storageUsage.usage_percent}% used
              </span>
            </div>
            <div className="mt-2 h-2 w-full rounded-full bg-muted">
              <div
                className="h-2 rounded-full bg-primary transition-all"
                style={{ width: `${Math.min(storageUsage.usage_percent, 100)}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              {formatFileSize(storageUsage.used_bytes)} used of{' '}
              {formatFileSize(storageUsage.quota_bytes)} total
            </p>
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-xl border bg-card p-6">
                <div className="flex items-start gap-3">
                  <Skeleton className="h-10 w-10 rounded-lg" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-5 w-3/4" />
                    <Skeleton className="h-4 w-full" />
                  </div>
                </div>
                <Skeleton className="mt-4 h-3 w-24" />
              </div>
            ))}
          </div>
        ) : datarooms.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <Database className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mt-4 text-lg font-semibold">No data rooms yet</h3>
            <p className="mt-1 text-sm text-muted-foreground text-center max-w-sm">
              Create a data room to start organizing files.
            </p>
            <Button className="mt-6" onClick={() => setCreateOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Data Room
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {datarooms.map((dr) => (
              <DataroomCard
                key={dr.id}
                dataroom={dr}
                onClick={() => onSelect(dr.id)}
                onRefresh={fetchDatarooms}
              />
            ))}
          </div>
        )}
      </div>

      <CreateDataroomDialog
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={fetchDatarooms}
      />
    </div>
  );
}
