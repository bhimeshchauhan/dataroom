import { useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Database } from 'lucide-react';
import { DataroomCard } from './DataroomCard';
import { CreateDataroomDialog } from './CreateDataroomDialog';
import { api } from '@/api/client';
import { toast } from 'sonner';
import type { Dataroom } from '@/types';

interface DataroomListProps {
  onSelect: (dataroomId: string) => void;
}

export function DataroomList({ onSelect }: DataroomListProps) {
  const [datarooms, setDatarooms] = useState<Dataroom[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

  const fetchDatarooms = useCallback(async () => {
    try {
      const res = await api.listDatarooms();
      setDatarooms(res.datarooms);
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
                Manage your secure document rooms
              </p>
            </div>
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Data Room
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-6xl px-6 py-8">
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
              Create your first data room to get started organizing and sharing
              your documents.
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
