import { useState, useEffect } from 'react';
import { Button } from '../../components/ui/Button';
import { AnalysisStepper } from '../../components/analysis/AnalysisStepper';
import { SHAPChart } from '../../components/analysis/SHAPChart';
import { RiskBadge } from '../../components/analysis/RiskBadge';
import { useCaseWebSocket } from '../../hooks/useCaseWebSocket';
import { api } from '../../services/api';
import toast from 'react-hot-toast';
import { ShieldCheck, ShieldAlert, Check, Copy, UploadCloud, Info } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

export function EmailAnalysis({ defaultMode = 'email' }: { defaultMode?: 'email' | 'url' | 'media' | 'image' | 'video' | 'audio' }) {
  const [text, setText] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [caseId, setCaseId] = useState<string | null>(null);
  const [verdict, setVerdict] = useState<'phishing' | 'ai_generated' | 'real' | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [analysisMode, setAnalysisMode] = useState<'email' | 'url' | 'media' | 'image' | 'video' | 'audio'>(defaultMode);
  const [mediaFile, setMediaFile] = useState<File | null>(null);

  // Auto-update internal mode if route changes
  useEffect(() => {
    setAnalysisMode(defaultMode);
    handleReset();
  }, [defaultMode]);
  
  const { status, progress, latestEvent, completeWithData, reset } = useCaseWebSocket(caseId || undefined);

  const handleDownloadReport = async () => {
    if (!caseId) return;
    try {
      toast.loading('Preparing report...', { id: 'report' });
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
      toast.success('Report downloaded', { id: 'report' });
    } catch (err) {
      console.error('Failed to download report', err);
      toast.error('Failed to download report', { id: 'report' });
    }
  };

  const handleEmailReport = async () => {
    if (!caseId) return;
    try {
      toast.loading('Dispatching secure email...', { id: 'email_report' });
      const res = await api.post(`/cases/${caseId}/email_report`);
      if (res.data.status === 'success') {
         toast.success(res.data.message, { id: 'email_report', duration: 4000 });
      } else {
         toast.success('Email mocked locally (SMTP not set)', { id: 'email_report', duration: 4000 });
      }
    } catch (err) {
      console.error('Failed to email report', err);
      toast.error('Failed to email report', { id: 'email_report' });
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: analysisMode === 'video' ? { 'video/*': [] } : analysisMode === 'image' ? { 'image/*': [] } : analysisMode === 'audio' ? { 'audio/*': [] } : { 'image/*': [], 'video/*': [], 'audio/*': [] },
    maxFiles: 1,
    onDrop: acceptedFiles => {
      if (acceptedFiles.length > 0) setMediaFile(acceptedFiles[0]);
    }
  });

  const handleSubmit = async () => {
    if ((analysisMode === 'email' && !text) || (analysisMode === 'url' && !urlInput) || (['media', 'image', 'video', 'audio'].includes(analysisMode) && !mediaFile)) {
      toast.error('INPUT REQUIRED FOR ANALYSIS');
      return;
    }
    setIsSubmitting(true);
    setVerdict(null);
    try {
      const endpoint = analysisMode === 'email' ? '/analyze/email' : analysisMode === 'url' ? '/analyze/url' : '/analyze/media';
      let payload;
      let headers = {};
      
      if (['media', 'image', 'video', 'audio'].includes(analysisMode) && mediaFile) {
        payload = new FormData();
        payload.append('file', mediaFile);
        headers = { 'Content-Type': 'multipart/form-data' };
      } else {
        payload = analysisMode === 'email' ? { text: text } : { url: urlInput };
      }
      
      const res = await api.post(endpoint, payload, { headers });
      
      setAnalysisData(res.data);
      setCaseId(res.data.case_id);
      
      // Set verdict from real result, then animate the stepper
      const v = (res.data.threat_type === 'deepfake' || res.data.threat_type === 'deepfake_video') ? 'phishing'
              : (res.data.threat_type === 'ai_generated' || res.data.threat_type === 'ai_generated_video') ? 'ai_generated'
              : res.data.verdict === 'threat' ? 'phishing'
              : res.data.verdict === 'suspicious' ? 'phishing'
              : 'real';
      setVerdict(v);
      completeWithData(res.data);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        toast.error(detail[0]?.msg || "Invalid input provided.");
      } else {
        toast.error(detail || "Failed to submit");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setCaseId(null);
    setVerdict(null);
    setAnalysisData(null);
    setText('');
    setUrlInput('');
    setMediaFile(null);
    reset();
  };

  const isCompleted = status === 'completed';
  
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-display font-bold text-zinc-50 uppercase tracking-widest text-shadow-glow">Neural Threat Scanner</h1>
        <p className="text-zinc-500 font-display mt-1 text-xs tracking-widest uppercase">Select an input vector for contextual AI and Deepfake inspection.</p>
      </div>

      {!caseId ? (
        <div className="glass rounded border-white/5 p-6 relative">

          <div className="relative z-10">
          {analysisMode === 'email' && (
            <textarea
              className="w-full h-64 bg-[#09090b]/50 border border-zinc-800 rounded p-4 font-display text-zinc-50 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-all resize-none shadow-[inset_0_0_20px_rgba(0,0,0,0.5)]"
              placeholder="> PASTE RAW EMAIL CONTENT (OR PASTE A GENUINE EMAIL) FOR SCANNING..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          )}

          {analysisMode === 'url' && (
            <input
              type="text"
              className="w-full bg-[#09090b]/50 border border-zinc-800 rounded p-4 font-display text-zinc-50 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-all shadow-[inset_0_0_20px_rgba(0,0,0,0.5)]"
              placeholder="> ENTER URL (e.g., http://bit.ly/secure-login or https://github.com)"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
            />
          )}

          {['media', 'image', 'video', 'audio'].includes(analysisMode) && (
            <div 
              {...getRootProps()} 
              className={`w-full h-64 border-2 border-dashed rounded flex flex-col items-center justify-center p-6 text-center cursor-pointer transition-all duration-300 ${isDragActive ? 'border-red-600 bg-red-600/5' : 'border-zinc-800 bg-zinc-900/30 hover:border-zinc-600 hover:bg-zinc-900/50'} ${mediaFile ? 'border-emerald-500 bg-emerald-500/5' : ''}`}
            >
              <input {...getInputProps()} />
              <UploadCloud className={`mb-4 w-12 h-12 ${mediaFile ? 'text-emerald-500' : 'text-zinc-600'}`} />
              <p className="font-display tracking-widest text-sm text-zinc-400">
                {mediaFile ? (
                  <span className="text-emerald-500 font-bold uppercase">{'>'} SELECTED: {mediaFile.name} ({(mediaFile.size / 1024 / 1024).toFixed(2)} MB)</span>
                ) : isDragActive ? (
                  <span className="text-red-500">DROP TO UPLOAD...</span>
                ) : (
                  <span>DRAG & DROP {analysisMode === 'video' ? 'VIDEO' : analysisMode === 'image' ? 'IMAGE' : analysisMode === 'audio' ? 'AUDIO' : 'IMAGE/VIDEO/AUDIO'} HERE <br/><span className="text-xs text-zinc-600 mt-2 block">OR CLICK TO BROWSE</span></span>
                )}
              </p>
            </div>
          )}
          </div>

          <div className="flex justify-end mt-4">
            <Button size="lg" onClick={handleSubmit} isLoading={isSubmitting} className="font-display tracking-widest uppercase">
              INITIATE NEURAL SCAN
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <AnalysisStepper status={status} progress={progress} />
          
          {isCompleted && (
            <div className="animate-in fade-in zoom-in duration-500">
              <div className={`p-6 rounded border flex flex-col md:flex-row justify-between items-center gap-4 ${
                verdict === 'phishing' 
                ? 'bg-red-600/10 border-red-600/50 shadow-glow-red'
                : verdict === 'ai_generated'
                ? 'bg-orange-500/10 border-orange-500/50 shadow-[0_0_15px_rgba(249,115,22,0.3)]'
                : 'bg-emerald-500/10 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
              }`}>
                <div className="flex items-center gap-4">
                  {verdict === 'phishing' 
                    ? <ShieldAlert size={40} className="text-red-600 drop-shadow-[0_0_8px_rgba(220,38,38,0.8)]" />
                    : verdict === 'ai_generated'
                    ? <ShieldAlert size={40} className="text-orange-500 drop-shadow-[0_0_8px_rgba(249,115,22,0.8)]" />
                    : <ShieldCheck size={40} className="text-emerald-500 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" />}
                  <div>
                    <h2 className="text-2xl font-display font-bold uppercase tracking-wider text-zinc-50">
                      {verdict === 'phishing' 
                        ? (['media', 'image', 'video', 'audio'].includes(analysisMode) ? 'CRITICAL THREAT — DEEPFAKE DETECTED' : 'CRITICAL THREAT — PHISHING DETECTED')
                       : verdict === 'ai_generated' ? `WARNING — AI GENERATED ${analysisMode === 'video' ? 'VIDEO' : analysisMode === 'audio' ? 'AUDIO' : 'IMAGE'}`
                       : 'SYSTEM CLEAR'}
                    </h2>
                    <p className="font-display text-zinc-400">Confidence: {(analysisData?.confidence ? analysisData.confidence * 100 : 99.9).toFixed(2)}%</p>
                    {analysisData?.reason && (
                      <p className="font-display text-xs mt-1 text-zinc-500">{analysisData.reason}</p>
                    )}
                    {analysisData?.reasons && Array.isArray(analysisData.reasons) && (
                      <div className="mt-2 space-y-1">
                          {analysisData.reasons.map((r: string, i: number) => (
                              <p key={i} className="font-display text-xs text-zinc-500">• {r}</p>
                          ))}
                      </div>
                    )}
                    {analysisData?.deepfake_score !== undefined && (
                      <div className="flex gap-3 mt-2 flex-wrap">
                        <span className="text-xs font-display bg-zinc-900 border border-zinc-700 px-2 py-1 rounded text-zinc-400">Face: {analysisData.face_detected ? 'YES' : 'NO'}</span>
                        <span className="text-xs font-display bg-zinc-900 border border-zinc-700 px-2 py-1 rounded text-zinc-400">Deepfake: {(analysisData.deepfake_score * 100).toFixed(0)}%</span>
                        {analysisData.sdxl_score !== undefined && (
                          <span className="text-xs font-display bg-zinc-900 border border-zinc-700 px-2 py-1 rounded text-zinc-400">SDXL: {(analysisData.sdxl_score * 100).toFixed(0)}%</span>
                        )}
                        {analysisData.gemini_score !== undefined && (
                          <span className="text-xs font-display bg-zinc-900 border border-zinc-700 px-2 py-1 rounded text-zinc-400">Gemini: {(analysisData.gemini_score * 100).toFixed(0)}%</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                   <RiskBadge level={verdict === 'phishing' ? 'high' : verdict === 'ai_generated' ? 'medium' : 'low'} />
                   <div className="flex flex-col gap-2 w-full mt-2">
                     <Button variant={verdict === 'phishing' ? 'danger' : 'primary'} size="sm" className="w-full" onClick={handleDownloadReport}>
                       Download Report
                     </Button>
                     <Button size="sm" className="w-full bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700 font-display tracking-widest uppercase" onClick={handleEmailReport}>
                       Email Report
                     </Button>
                   </div>
                </div>
              </div>

              {/* XAI Chart */}
              {analysisData?.xai_data?.top_features && (
                <div className="mt-8 glass rounded border-white/5 p-6">
                  <h3 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} SHAP FEATURE ATTRIBUTION</h3>
                  <SHAPChart data={analysisData.xai_data.top_features} />
                </div>
              )}

              {/* Threat Intelligence Dossier */}
              {analysisData?.xai_data?.education && (
                 <div className="mt-8 bg-zinc-950 border border-zinc-800 p-6 shadow-[inset_0_0_20px_rgba(0,0,0,0.8)] relative overflow-hidden">
                    {/* Decorative Top Line */}
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-zinc-500 to-transparent opacity-50" />
                    
                    <h3 className="text-sm font-display font-bold text-zinc-300 mb-6 tracking-widest uppercase flex items-center gap-2">
                      <Info size={16} className={verdict === 'phishing' ? 'text-red-500' : 'text-emerald-500'} />
                      <span className={verdict === 'phishing' ? 'text-red-500 font-bold' : 'text-emerald-500 font-bold'}> {'>'} THREAT INTELLIGENCE DOSSIER </span>
                    </h3>
                    
                    <div className="space-y-6">
                      <div>
                        <h4 className="text-xs font-display tracking-widest text-zinc-500 uppercase mb-2">Neural Engine Analysis</h4>
                        <p className="font-body text-zinc-300 leading-relaxed border-l-2 border-zinc-700 pl-4">
                          {analysisData.xai_data.education.why}
                        </p>
                      </div>
                      
                      <div>
                        <h4 className="text-xs font-display tracking-widest text-zinc-500 uppercase mb-2">Operative Mitigation Protocol</h4>
                        <p className="font-body text-zinc-300 leading-relaxed border-l-2 border-zinc-700 pl-4">
                           {analysisData.xai_data.education.how_to_spot}
                        </p>
                      </div>
                    </div>
                 </div>
              )}

              <div className="mt-8 flex justify-between items-center">
                 <button 
                   onClick={handleReset}
                   className="text-zinc-500 hover:text-red-500 font-display tracking-widest border border-zinc-800 hover:border-red-600/50 bg-zinc-900/50 px-6 py-2 rounded transition-all flex items-center gap-2 uppercase text-sm"
                 >
                   <span>&lt;</span> NEW SCAN
                 </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
