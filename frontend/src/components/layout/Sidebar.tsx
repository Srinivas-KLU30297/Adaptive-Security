import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { LayoutDashboard, Shield, FolderSearch, Settings, LogOut } from 'lucide-react';
import clsx from 'clsx';

export function Sidebar() {
  const { user, logout } = useAuthStore();
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Email Scanner', path: '/analyze/email', icon: Shield },
    { name: 'URL Scanner', path: '/analyze/url', icon: Shield },
    { name: 'Image Scanner', path: '/analyze/image', icon: Shield },
    { name: 'Video Scanner', path: '/analyze/video', icon: Shield },
    { name: 'Audio Scanner', path: '/analyze/audio', icon: Shield },
    { name: 'Case History', path: '/cases', icon: FolderSearch },
  ];

  if (user?.role === 'admin') {
    navItems.push({ name: 'Admin', path: '/admin', icon: Settings });
  }

  return (
    <div className="w-60 glass border-r-0 border-white/5 h-screen flex flex-col hidden md:flex shadow-none relative animate-in slide-in-from-left duration-500">
      <div className="p-6 relative z-10">
        <h1 className="font-display font-bold text-xl text-red-600 drop-shadow-[0_0_12px_rgba(220,38,38,0.6)] uppercase tracking-wider">
          {'>'} CyberShield
        </h1>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2 relative z-10">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname.includes(item.path);
          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded text-sm uppercase tracking-widest transition-all duration-300 font-display",
                isActive 
                  ? "bg-red-600/10 text-red-500 border-l-[3px] border-red-600 shadow-[inset_10px_0_15px_-10px_rgba(220,38,38,0.5)]" 
                  : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50"
              )}
            >
              <Icon size={20} />
              <span className="font-ui font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-3 mb-4 px-2">
          <div className="w-10 h-10 rounded-full bg-surface-2 border border-primary/30 flex items-center justify-center text-primary font-bold">
            {user?.email?.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-text-primary truncate">{user?.email}</p>
            <p className="text-xs text-primary capitalize">{user?.role}</p>
          </div>
        </div>
        <button 
          onClick={logout}
          className="w-full flex items-center gap-2 px-4 py-2 text-text-muted hover:text-danger hover:bg-danger/10 rounded-lg transition-colors"
        >
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}
