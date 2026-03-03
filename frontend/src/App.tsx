import { useState, useEffect, useCallback } from 'react';
import { Toaster } from '@/components/ui/sonner';
import { DataroomList } from '@/components/datarooms/DataroomList';
import { DataroomDetail } from '@/components/layout/DataroomDetail';

type View = 'list' | 'detail';

function parseHash(): {
  view: View;
  dataroomId: string | null;
  folderId: string | null;
} {
  const hash = window.location.hash;

  // Match #/dataroom/<id>/folder/<folderId>
  const folderMatch = hash.match(
    /^#\/dataroom\/([a-f0-9-]+)\/folder\/([a-f0-9-]+)$/
  );
  if (folderMatch) {
    return {
      view: 'detail',
      dataroomId: folderMatch[1],
      folderId: folderMatch[2],
    };
  }

  // Match #/dataroom/<id>
  const dataroomMatch = hash.match(/^#\/dataroom\/([a-f0-9-]+)$/);
  if (dataroomMatch) {
    return {
      view: 'detail',
      dataroomId: dataroomMatch[1],
      folderId: null,
    };
  }

  return { view: 'list', dataroomId: null, folderId: null };
}

function buildHash(
  dataroomId: string | null,
  folderId: string | null
): string {
  if (!dataroomId) return '#/';
  if (folderId) return `#/dataroom/${dataroomId}/folder/${folderId}`;
  return `#/dataroom/${dataroomId}`;
}

export default function App() {
  const initialHash = parseHash();
  const [currentView, setCurrentView] = useState<View>(initialHash.view);
  const [currentDataroomId, setCurrentDataroomId] = useState<string | null>(
    initialHash.dataroomId
  );
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(
    initialHash.folderId
  );

  // Listen for hash changes (browser back/forward)
  useEffect(() => {
    const handleHashChange = () => {
      const { view, dataroomId, folderId } = parseHash();
      setCurrentView(view);
      setCurrentDataroomId(dataroomId);
      setCurrentFolderId(folderId);
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // Update hash when state changes
  const navigate = useCallback(
    (dataroomId: string | null, folderId: string | null) => {
      setCurrentDataroomId(dataroomId);
      setCurrentFolderId(folderId);
      if (dataroomId) {
        setCurrentView('detail');
      } else {
        setCurrentView('list');
      }
      window.location.hash = buildHash(dataroomId, folderId);
    },
    []
  );

  const handleSelectDataroom = useCallback(
    (dataroomId: string) => {
      navigate(dataroomId, null);
    },
    [navigate]
  );

  const handleBack = useCallback(() => {
    navigate(null, null);
  }, [navigate]);

  const handleNavigateFolder = useCallback(
    (folderId: string | null) => {
      if (currentDataroomId) {
        navigate(currentDataroomId, folderId);
      }
    },
    [navigate, currentDataroomId]
  );

  return (
    <>
      {currentView === 'list' ? (
        <DataroomList onSelect={handleSelectDataroom} />
      ) : currentDataroomId ? (
        <DataroomDetail
          dataroomId={currentDataroomId}
          folderId={currentFolderId}
          onBack={handleBack}
          onNavigate={handleNavigateFolder}
        />
      ) : null}
      <Toaster richColors position="bottom-right" />
    </>
  );
}
