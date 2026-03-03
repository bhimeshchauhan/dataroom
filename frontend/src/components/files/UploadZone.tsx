import { useState, useRef, useCallback } from 'react';
import { Upload } from 'lucide-react';
import { api } from '@/api/client';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface UploadZoneProps {
  dataroomId: string;
  folderId: string | null;
  onUploaded: () => void;
}

export function UploadZone({ dataroomId, folderId, onUploaded }: UploadZoneProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadFileName, setUploadFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      const pdfFiles = Array.from(files).filter(
        (f) =>
          f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf')
      );

      if (pdfFiles.length === 0) {
        toast.error('Only PDF files are accepted');
        return;
      }

      setUploading(true);
      for (const file of pdfFiles) {
        setUploadFileName(file.name);
        try {
          await api.uploadFile(dataroomId, file, folderId);
          toast.success(`Uploaded ${file.name}`);
        } catch (err) {
          toast.error(
            `Failed to upload ${file.name}: ${err instanceof Error ? err.message : 'Unknown error'}`
          );
        }
      }
      setUploading(false);
      setUploadFileName(null);
      onUploaded();
    },
    [dataroomId, folderId, onUploaded]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
      // Reset input so the same file can be uploaded again
      e.target.value = '';
    }
  };

  return (
    <div
      className={cn(
        'mt-6 flex flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-10 transition-colors cursor-pointer',
        dragging
          ? 'border-primary bg-primary/5'
          : 'border-muted-foreground/25 hover:border-muted-foreground/40 hover:bg-muted/50',
        uploading && 'pointer-events-none opacity-70'
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        multiple
        className="hidden"
        onChange={handleChange}
      />
      <Upload
        className={cn(
          'h-8 w-8 mb-3',
          dragging ? 'text-primary' : 'text-muted-foreground'
        )}
      />
      {uploading ? (
        <p className="text-sm text-muted-foreground">
          Uploading {uploadFileName}...
        </p>
      ) : (
        <>
          <p className="text-sm font-medium">
            {dragging ? 'Drop PDF here' : 'Drop PDF files here or click to browse'}
          </p>
          <p className="text-xs text-muted-foreground mt-1">PDF files only</p>
        </>
      )}
    </div>
  );
}
