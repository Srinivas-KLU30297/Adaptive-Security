import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud } from 'lucide-react';
import { clsx } from 'clsx';

interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
  accept?: Record<string, string[]>;
  maxSizeMB?: number;
  label?: string;
}

export function FileDropzone({ onFileSelect, accept, maxSizeMB = 100, label = "Drag & Drop File Here" }: FileDropzoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: false
  });

  return (
    <div 
      {...getRootProps()} 
      className={clsx(
        "border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all duration-200",
        isDragActive ? "border-primary bg-primary/5" : "border-border bg-surface hover:border-primary/50",
        isDragReject && "border-danger bg-danger/5"
      )}
    >
      <input {...getInputProps()} />
      <UploadCloud 
        size={48} 
        className={clsx("mb-4 transition-colors", isDragActive ? "text-primary flex-shrink-0 drop-shadow-[0_0_8px_rgba(0,212,255,0.5)]" : "text-text-muted")} 
      />
      <p className="text-lg font-ui font-medium text-text-primary text-center">
        {isDragActive ? "Drop it to scan!" : label}
      </p>
      <p className="text-sm mt-2 text-text-muted text-center font-body">
        Max file size: {maxSizeMB}MB
      </p>
    </div>
  );
}
