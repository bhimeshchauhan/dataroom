import { useEffect, useCallback, useState } from 'react';
import { Button } from '@/components/ui/button';
import { X, ExternalLink, Loader2 } from 'lucide-react';
import { api } from '@/api/client';

interface PdfViewerModalProps {
  fileId: string;
  fileName: string;
  onClose: () => void;
}

export function PdfViewerModal({
  fileId,
  fileName,
  onClose,
}: PdfViewerModalProps) {
  const [loading, setLoading] = useState(true);
  const fileUrl = api.getFileContentUrl(fileId);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [handleKeyDown]);

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex flex-col">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-black/90 shrink-0">
        <h3 className="text-sm font-medium text-white truncate max-w-md">
          {fileName}
        </h3>
        <div className="flex items-center gap-2">
          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center h-8 w-8 rounded-md text-white hover:bg-white/10 transition-colors"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-white hover:bg-white/10"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* PDF via native browser renderer */}
      <div className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-white/60" />
          </div>
        )}
        <iframe
          src={fileUrl}
          title={fileName}
          className="w-full h-full border-0"
          onLoad={() => setLoading(false)}
        />
      </div>
    </div>
  );
}
