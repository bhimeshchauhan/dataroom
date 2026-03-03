import { useState, useEffect, useCallback, type FormEvent } from 'react';
import { Toaster } from '@/components/ui/sonner';
import { DataroomList } from '@/components/datarooms/DataroomList';
import { DataroomDetail } from '@/components/layout/DataroomDetail';
import { AUTH_EXPIRED_EVENT, api } from '@/api/client';
import { toast } from 'sonner';

type View = 'list' | 'detail';
type AuthMode = 'login' | 'register';

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
  const [authLoading, setAuthLoading] = useState(true);
  const [isAuthed, setIsAuthed] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authSubmitting, setAuthSubmitting] = useState(false);
  const [currentView, setCurrentView] = useState<View>(initialHash.view);
  const [currentDataroomId, setCurrentDataroomId] = useState<string | null>(
    initialHash.dataroomId
  );
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(
    initialHash.folderId
  );

  useEffect(() => {
    const bootstrapAuth = async () => {
      const token = api.getToken();
      if (!token) {
        setAuthLoading(false);
        return;
      }
      try {
        await api.me();
        setIsAuthed(true);
      } catch {
        api.clearToken();
      } finally {
        setAuthLoading(false);
      }
    };
    bootstrapAuth();
  }, []);

  useEffect(() => {
    const handleAuthExpired = () => {
      setIsAuthed(false);
      setCurrentView('list');
      setCurrentDataroomId(null);
      setCurrentFolderId(null);
      window.location.hash = '#/';
      toast.error('Session expired. Please sign in again.');
    };
    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);
  }, []);

  // Listen for hash changes (browser back/forward)
  useEffect(() => {
    if (!isAuthed) return;
    const handleHashChange = () => {
      const { view, dataroomId, folderId } = parseHash();
      setCurrentView(view);
      setCurrentDataroomId(dataroomId);
      setCurrentFolderId(folderId);
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [isAuthed]);

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

  const handleLogout = useCallback(() => {
    api.clearToken();
    setIsAuthed(false);
    setCurrentView('list');
    setCurrentDataroomId(null);
    setCurrentFolderId(null);
    window.location.hash = '#/';
    toast.success('Logged out');
  }, []);

  const handleAuthSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      setAuthSubmitting(true);
      try {
        const trimmedEmail = email.trim().toLowerCase();
        if (authMode === 'register') {
          await api.register(trimmedEmail, password);
          setAuthMode('login');
          setPassword('');
          toast.success('Account created. Please sign in.');
        } else {
          const res = await api.login(trimmedEmail, password);
          api.setToken(res.token);
          setIsAuthed(true);
          toast.success('Signed in');
        }
      } catch (err) {
        toast.error(err instanceof Error ? err.message : 'Authentication failed');
      } finally {
        setAuthSubmitting(false);
      }
    },
    [authMode, email, password]
  );

  if (authLoading) {
    return <div className="p-8 text-sm text-muted-foreground">Loading...</div>;
  }

  if (!isAuthed) {
    return (
      <>
        <div className="min-h-screen bg-muted/30 flex items-center justify-center p-6">
          <form
            className="w-full max-w-sm rounded-xl border bg-card p-6 space-y-4"
            onSubmit={handleAuthSubmit}
          >
            <div>
              <h1 className="text-xl font-semibold">Data Room Sign In</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Use your email and password to continue.
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <input
                type="email"
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Password</label>
              <input
                type="password"
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </div>
            <button
              type="submit"
              className="w-full rounded-md bg-primary text-primary-foreground py-2 text-sm font-medium disabled:opacity-60"
              disabled={authSubmitting}
            >
              {authSubmitting
                ? 'Please wait...'
                : authMode === 'register'
                ? 'Create account'
                : 'Sign in'}
            </button>
            <button
              type="button"
              className="w-full text-sm text-muted-foreground hover:text-foreground"
              onClick={() =>
                setAuthMode((prev) => (prev === 'login' ? 'register' : 'login'))
              }
            >
              {authMode === 'login'
                ? "Don't have an account? Register"
                : 'Already have an account? Sign in'}
            </button>
          </form>
        </div>
        <Toaster richColors position="bottom-right" />
      </>
    );
  }

  return (
    <>
      {currentView === 'list' ? (
        <DataroomList onSelect={handleSelectDataroom} onLogout={handleLogout} />
      ) : currentDataroomId ? (
        <DataroomDetail
          dataroomId={currentDataroomId}
          folderId={currentFolderId}
          onBack={handleBack}
          onNavigate={handleNavigateFolder}
          onLogout={handleLogout}
        />
      ) : null}
      <Toaster richColors position="bottom-right" />
    </>
  );
}
