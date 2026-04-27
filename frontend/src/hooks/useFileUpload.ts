import { useState } from 'react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

export function useFileUpload(endpoint: string) {
  const [isUploading, setIsUploading] = useState(false);
  const [caseId, setCaseId] = useState<string | null>(null);

  const upload = async (file: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCaseId(res.data.case_id);
      toast.success("File uploaded successfully. Analyzing...");
      return res.data.case_id;
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Upload failed");
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  return { upload, isUploading, caseId };
}
