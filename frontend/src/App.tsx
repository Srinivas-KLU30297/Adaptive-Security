import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { Layout } from './components/layout/Layout';
// Using placeholders for lazy loading or import direct
import { Dashboard } from './pages/Dashboard';
import { AuthPage } from './pages/AuthPage';
import { EmailAnalysis } from './pages/Analysis/EmailAnalysis';
import { Cases } from './pages/Cases';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster position="top-right" toastOptions={{ duration: 4000, style: { background: '#09090b', color: '#fff', border: '1px solid #27272a' } }} />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AuthPage defaultMode="login" />} />
          <Route path="/register" element={<AuthPage defaultMode="signup" />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="analyze/email" element={<div className="p-6 h-full flex flex-col"><h2 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} NEURAL THREAT ANALYSIS MODULE</h2><EmailAnalysis defaultMode="email" /></div>} />
            <Route path="analyze/url" element={<div className="p-6 h-full flex flex-col"><h2 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} URL THREAT ANALYSIS MODULE</h2><EmailAnalysis defaultMode="url" /></div>} />
            <Route path="analyze/image" element={<div className="p-6 h-full flex flex-col"><h2 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} IMAGE FORENSICS MODULE</h2><EmailAnalysis defaultMode="image" /></div>} />
            <Route path="analyze/video" element={<div className="p-6 h-full flex flex-col"><h2 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} VIDEO FORENSICS MODULE</h2><EmailAnalysis defaultMode="video" /></div>} />
            <Route path="analyze/audio" element={<div className="p-6 h-full flex flex-col"><h2 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} AUDIO FORENSICS MODULE</h2><EmailAnalysis defaultMode="audio" /></div>} />
            <Route path="cases" element={<div className="p-6 h-full flex flex-col"><h2 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} ARCHIVED CASE INTELLIGENCE</h2><Cases /></div>} />
            <Route path="*" element={<div className="text-center mt-20"><h2 className="text-3xl tracking-widest font-bold font-display text-red-600 drop-shadow-[0_0_12px_rgba(220,38,38,0.8)]">404 - MODULE NOT FOUND</h2></div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
