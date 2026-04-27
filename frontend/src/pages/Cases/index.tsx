import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import { CaseListResponse } from '../../types/case';
import { format } from 'date-fns';
import { Search, FileText } from 'lucide-react';
import { RiskBadge } from '../../components/analysis/RiskBadge';
import { Button } from '../../components/ui/Button';

export function Cases() {
  const [page, setPage] = useState(1);
  const size = 15;

  const { data, isLoading } = useQuery<CaseListResponse>({
    queryKey: ['cases', page],
    queryFn: async () => {
      const res = await api.get(`/cases/?page=${page}&size=${size}`);
      return res.data;
    }
  });

  const handleDownloadReport = async (caseId: string) => {
    try {
      const response = await api.get(`/cases/${caseId}/report`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${caseId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err) {
      console.error('Failed to download report', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-display font-bold text-text-primary">Case History</h1>
          <p className="text-text-muted font-body mt-1">Review past intelligence reports and forensic data.</p>
        </div>
        <div className="bg-primary/20 text-primary font-body px-4 py-2 rounded-lg border border-primary/30 shadow-[0_0_8px_rgba(0,212,255,0.2)]">
          Total Records: {data?.total || 0}
        </div>
      </div>

      <div className="glass rounded border-white/5 overflow-hidden">
        <div className="p-4 border-b border-white/5 flex flex-col sm:flex-row items-center gap-4">
          <div className="relative flex-1 max-w-md w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
            <input 
              type="text" 
              placeholder="QUERY ARCHIVE REPOSITORY..." 
              className="w-full bg-[#09090b]/50 border border-zinc-800 rounded pl-10 pr-4 py-2 text-sm focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none text-zinc-50 font-display tracking-widest uppercase transition-colors"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-zinc-400">
            <thead className="bg-[#18181b]/50 text-red-600 font-display border-b border-white/5">
              <tr>
                <th className="px-6 py-4 font-medium tracking-wider">Date</th>
                <th className="px-6 py-4 font-medium tracking-wider">Case ID</th>
                <th className="px-6 py-4 font-medium tracking-wider">Type</th>
                <th className="px-6 py-4 font-medium tracking-wider">Verdict</th>
                <th className="px-6 py-4 font-medium tracking-wider">Risk Level</th>
                <th className="px-6 py-4 font-medium tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="font-display divide-y divide-white/5">
              {isLoading ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-red-600 animate-pulse tracking-widest font-bold">DECRYPTING ARCHIVES...</td></tr>
              ) : data?.items.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-zinc-500">NO RECORDS FOUND.</td></tr>
              ) : (
                data?.items.map((c) => (
                  <tr key={c.id} className="hover:bg-red-600/5 transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap group-hover:text-zinc-300">{format(new Date(c.created_at), 'yyyy-MM-dd HH:mm')}</td>
                    <td className="px-6 py-4 tracking-tighter">{c.id.split('-')[0]}...</td>
                    <td className="px-6 py-4 uppercase text-text-primary">{c.case_type}</td>
                    <td className="px-6 py-4 uppercase font-bold">
                       <span className={c.verdict === 'phishing' || c.verdict === 'deepfake' || c.verdict === 'deepfake_video' || c.verdict === 'deepfake_audio' || c.verdict === 'ai_generated' || c.verdict === 'ai_generated_video' ? 'text-danger' : 
                                        c.verdict === 'suspicious' ? 'text-warning' : 'text-success'}>
                         {c.verdict || 'PENDING'}
                       </span>
                    </td>
                    <td className="px-6 py-4">
                      <RiskBadge level={c.risk_level || 'low'} />
                    </td>
                    <td className="px-6 py-4 text-right">
                       <Button size="sm" variant="ghost" onClick={() => handleDownloadReport(c.id)}>
                         <FileText size={16} />
                       </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
