import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Eye, EyeOff, Cpu, ChevronRight } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { api } from '../services/api';
import toast from 'react-hot-toast';

interface AuthPageProps {
  defaultMode?: 'login' | 'signup';
}

export function AuthPage({ defaultMode = 'login' }: AuthPageProps) {
  const [mode, setMode] = useState<'login' | 'signup'>(defaultMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.pathname === '/register') setMode('signup');
    else setMode('login');
  }, [location]);

  // Password Strength Calculation
  const calculateStrength = (pwd: string) => {
    let score = 0;
    if (pwd.length > 8) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    return score;
  };

  const strength = calculateStrength(password);
  
  const getStrengthBarConfig = () => {
    if (password.length === 0) return { width: '0%', color: 'bg-transparent' };
    switch (strength) {
      case 0:
      case 1: return { width: '25%', color: 'bg-red-600' };
      case 2: return { width: '50%', color: 'bg-orange-500' };
      case 3: return { width: '75%', color: 'bg-yellow-400' };
      case 4: return { width: '100%', color: 'bg-emerald-500' };
      default: return { width: '0%', color: 'bg-transparent' };
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Artificial delay for terminal effect
    await new Promise(resolve => setTimeout(resolve, 800));

    try {
      if (mode === 'signup') {
         const res = await api.post('/auth/register', { email, password, full_name: fullName });
         login(res.data.user, res.data.access_token, res.data.refresh_token);
         toast.success('Registration Complete. Access Granted.', {
           style: { background: '#09090b', border: '1px solid #18181b', color: '#10b981' }
         });
         navigate('/dashboard');
      } else {
         const res = await api.post('/auth/login', { email, password });
         login(res.data.user, res.data.access_token, res.data.refresh_token);
         toast.success('Access Granted.', {
           style: { background: '#09090b', border: '1px solid #18181b', color: '#10b981' }
         });
         navigate('/dashboard');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Authentication Failed', {
         style: { background: '#09090b', border: '1px solid #dc2626', color: '#dc2626' }
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid-bg flex flex-col items-center justify-center relative overflow-hidden">
      {/* Orb Backgrounds */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-red-600/10 rounded-full blur-3xl animate-pulse pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-red-600/5 rounded-full blur-3xl animate-pulse pointer-events-none" style={{ animationDelay: '2s' }} />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="z-10 w-full max-w-md p-8 glass rounded-md relative"
      >
        <div className="flex flex-col items-center mb-8">
          <Shield className="text-red-600 mb-4 shrink-0 shadow-glow-red rounded-full" size={48} />
          <h1 className="text-2xl font-display font-bold text-zinc-50 tracking-widest uppercase shadow-glow-red-text">
            {mode === 'login' ? 'Authentication' : 'New Operative'}
          </h1>
          <p className="text-zinc-500 mt-2 text-xs tracking-widest uppercase">
            {mode === 'login' ? 'Enter Credentials' : 'Request Security Clearance'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {mode === 'signup' && (
            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} className="overflow-hidden">
              <label className="block text-xs uppercase tracking-wider text-zinc-400 mb-1">Designation</label>
              <input 
                type="text" 
                required
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded px-4 py-3 text-zinc-50 focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                placeholder="Agent Name"
              />
            </motion.div>
          )}

          <div>
            <label className="block text-xs uppercase tracking-wider text-zinc-400 mb-1">Operative Email</label>
            <input 
              type="email" 
              required
              className="w-full bg-zinc-900/50 border border-zinc-800 rounded px-4 py-3 text-zinc-50 focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="sysadmin@cybershield.ai"
            />
          </div>

          <div className="relative">
            <label className="block text-xs uppercase tracking-wider text-zinc-400 mb-1">Authorization Key</label>
            <div className="relative">
              <input 
                type={showPassword ? "text" : "password"} 
                required
                className="w-full bg-zinc-900/50 border border-zinc-800 rounded px-4 py-3 pr-10 text-zinc-50 focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 transition-colors"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              <button 
                type="button" 
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            
            {/* Password Strength Meter */}
            {mode === 'signup' && (
              <div className="mt-2 h-1 w-full bg-zinc-800 rounded overflow-hidden">
                <motion.div 
                  className={`h-full ${getStrengthBarConfig().color}`}
                  initial={{ width: 0 }}
                  animate={{ width: getStrengthBarConfig().width }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            )}
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full h-12 mt-6 bg-red-600 text-zinc-50 uppercase tracking-widest font-bold rounded shadow-glow-red hover:bg-red-500 transition-colors flex items-center justify-center disabled:opacity-80 border border-red-400/20"
          >
            {isLoading ? (
              <Cpu className="animate-spin text-zinc-50" size={24} />
            ) : (
              <span className="flex items-center gap-2">
                {mode === 'login' ? 'Initialize Session' : 'Establish Link'} <ChevronRight size={18} />
              </span>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-xs tracking-wider text-zinc-500">
          {mode === 'login' ? (
            <p>NO CLEARANCE? <Link to="/register" className="text-red-500 hover:text-red-400 hover:underline">REQUEST ACCESS</Link></p>
          ) : (
            <p>ACTIVE OPERATIVE? <Link to="/login" className="text-red-500 hover:text-red-400 hover:underline">AUTHENTICATE</Link></p>
          )}
        </div>
      </motion.div>
    </div>
  );
}
