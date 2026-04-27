import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Activity, ShieldAlert, Eye, PercentSquare } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const res = await api.get('/dashboard/stats');
      return res.data;
    }
  });

  if (isLoading) return <div className="text-primary font-body animate-pulse">Fetching intelligence data...</div>;

  const summaryCards = [
    { title: "Total Scans", value: stats?.total_scans, icon: Activity, color: "text-primary", bg: "bg-primary/10" },
    { title: "Phishing Detected", value: stats?.phishing_detected, icon: ShieldAlert, color: "text-danger", bg: "bg-danger/10" },
    { title: "Deepfakes Found", value: stats?.deepfakes_detected, icon: Eye, color: "text-secondary", bg: "bg-secondary/10" },
    { title: "Avg Confidence", value: `${(stats?.avg_confidence * 100).toFixed(1)}%`, icon: PercentSquare, color: "text-success", bg: "bg-success/10" },
  ];

  const pieColors = ['#ef4444', '#10b981', '#f59e0b']; // danger, success, warning
  const chartData = stats?.weekly_scan_volume || [];
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-display font-bold text-text-primary">System Intelligence</h1>
        <p className="text-text-muted font-body mt-1">Real-time threat analytics and scan volumes.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="glass rounded border-white/5 p-6 hover:shadow-glow-red transition-all duration-300 relative group overflow-hidden">
              <div className="absolute inset-0 bg-red-600/0 group-hover:bg-red-600/5 transition-colors pointer-events-none" />
              <div className="flex justify-between items-start relative z-10">
                <div>
                  <p className="text-zinc-500 text-xs font-bold uppercase tracking-widest">{card.title}</p>
                  <h3 className="text-3xl font-display font-bold text-zinc-50 mt-2">{card.value}</h3>
                </div>
                <div className={`p-3 rounded-sm border border-white/5 ${card.bg}`}>
                  <Icon className={card.color} size={24} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass border-white/5 rounded p-6">
          <h3 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} VOLUME OVER TIME</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#dc2626" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#dc2626" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#52525b" tick={{fill: '#a1a1aa', fontSize: 12, fontFamily: 'JetBrains Mono'}} />
                <YAxis stroke="#52525b" tick={{fill: '#a1a1aa', fontSize: 12, fontFamily: 'JetBrains Mono'}} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(9, 9, 11, 0.9)', borderColor: 'rgba(220, 38, 38, 0.4)', borderRadius: '4px', backdropFilter: 'blur(8px)', color: '#fafafa' }} itemStyle={{ color: '#dc2626', fontFamily: 'JetBrains Mono' }} />
                <Area type="monotone" dataKey="count" stroke="#dc2626" strokeWidth={2} fillOpacity={1} fill="url(#colorCount)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass border-white/5 rounded p-6">
          <h3 className="text-sm font-display font-bold text-zinc-400 mb-6 tracking-widest uppercase">{'>'} VERDICT DISTRIBUTION</h3>
          <div className="h-[300px] w-full flex items-center justify-center">
             <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.verdict_distribution || []}
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="verdict"
                >
                  {(stats?.verdict_distribution || []).map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#1e3a5f', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
