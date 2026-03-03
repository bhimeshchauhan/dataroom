import { useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { ContentPanel } from './ContentPanel';
import { PdfViewerModal } from '@/components/files/PdfViewerModal';
import { api } from '@/api/client';
import { toast } from 'sonner';
import type { Dataroom, ContentsResponse, TreeNode } from '@/types';

interface DataroomDetailProps {
  dataroomId: string;
  folderId: string | null;
  onBack: () => void;
  onNavigate: (folderId: string | null) => void;
}

export function DataroomDetail({
  dataroomId,
  folderId,
  onBack,
  onNavigate,
}: DataroomDetailProps) {
  const [dataroom, setDataroom] = useState<Dataroom | null>(null);
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [contents, setContents] = useState<ContentsResponse | null>(null);
  const [loadingDataroom, setLoadingDataroom] = useState(true);
  const [loadingContents, setLoadingContents] = useState(true);
  const [viewingFile, setViewingFile] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [page, setPage] = useState(1);

  // Reset page when navigating to a different folder
  useEffect(() => {
    setPage(1);
  }, [folderId]);

  // Fetch dataroom info
  useEffect(() => {
    let cancelled = false;
    setLoadingDataroom(true);
    api
      .getDataroom(dataroomId)
      .then((dr) => {
        if (!cancelled) setDataroom(dr);
      })
      .catch((err) => {
        if (!cancelled)
          toast.error(
            err instanceof Error ? err.message : 'Failed to load data room'
          );
      })
      .finally(() => {
        if (!cancelled) setLoadingDataroom(false);
      });
    return () => {
      cancelled = true;
    };
  }, [dataroomId]);

  // Fetch tree
  const fetchTree = useCallback(async () => {
    try {
      const res = await api.getTree(dataroomId);
      setTree(res.tree);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : 'Failed to load folder tree'
      );
    }
  }, [dataroomId]);

  useEffect(() => {
    fetchTree();
  }, [fetchTree]);

  // Fetch contents
  const fetchContents = useCallback(async () => {
    setLoadingContents(true);
    try {
      let res: ContentsResponse;
      if (folderId) {
        res = await api.getFolderContents(folderId, 'name', 'asc', page);
      } else {
        res = await api.getDataroomContents(dataroomId, 'name', 'asc', page);
      }
      setContents(res);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : 'Failed to load contents'
      );
    } finally {
      setLoadingContents(false);
    }
  }, [dataroomId, folderId, page]);

  useEffect(() => {
    fetchContents();
  }, [fetchContents]);

  const handleRefresh = useCallback(() => {
    fetchContents();
    fetchTree();
  }, [fetchContents, fetchTree]);

  if (loadingDataroom && !dataroom) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Top header */}
      <div className="flex items-center gap-3 border-b bg-background px-4 py-3 shrink-0">
        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="min-w-0 flex-1">
          <h1 className="text-base font-semibold truncate">
            {dataroom?.name ?? 'Loading...'}
          </h1>
          {dataroom?.description && (
            <p className="text-xs text-muted-foreground truncate">
              {dataroom.description}
            </p>
          )}
        </div>
        {/* Mobile sidebar toggle */}
        <Button
          variant="outline"
          size="sm"
          className="sm:hidden"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? 'Hide folders' : 'Show folders'}
        </Button>
      </div>

      {/* Main area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div
          className={`${sidebarOpen ? 'block' : 'hidden'} sm:block shrink-0`}
        >
          <Sidebar
            tree={tree}
            currentFolderId={folderId}
            onSelectFolder={onNavigate}
            dataroomName={dataroom?.name ?? 'Data Room'}
          />
        </div>

        {/* Content */}
        <ContentPanel
          contents={contents}
          dataroomId={dataroomId}
          folderId={folderId}
          onNavigate={onNavigate}
          onViewFile={(fileId, fileName) =>
            setViewingFile({ id: fileId, name: fileName })
          }
          onRefresh={handleRefresh}
          loading={loadingContents}
          page={page}
          onPageChange={setPage}
        />
      </div>

      {/* PDF Viewer Modal */}
      {viewingFile && (
        <PdfViewerModal
          fileId={viewingFile.id}
          fileName={viewingFile.name}
          onClose={() => setViewingFile(null)}
        />
      )}
    </div>
  );
}
