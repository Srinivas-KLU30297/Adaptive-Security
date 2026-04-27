import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function SHAPChart({ data }: { data: any[] }) {
  if (!data || data.length === 0) return null;
  
  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface-2/80 backdrop-blur-md border border-primary/40 p-3 rounded-lg shadow-[0_0_15px_rgba(255,0,60,0.2)]">
          <p className="text-text-primary font-ui font-medium tracking-wide">Vactor: {payload[0].payload.feature || payload[0].payload.token}</p>
          <p className="text-primary font-display font-bold">Resonance: {payload[0].value.toFixed(4)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-[400px] mt-4">
      <h3 className="text-text-secondary font-display text-sm tracking-wide mb-4 text-center border-b border-border pb-2">
        FEATURE ATTRIBUTION (SHAP)
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <XAxis type="number" stroke="#f472b6" tick={{fill: '#fbcfe8', fontSize: 12}} />
          <YAxis dataKey={data[0]?.feature ? "feature" : "token"} type="category" stroke="#f472b6" tick={{fill: '#fdf2f8', fontSize: 14}} width={120} />
          <Tooltip content={<CustomTooltip />} cursor={{fill: 'rgba(255, 0, 60, 0.1)'}} />
          <Bar dataKey={data[0]?.contribution !== undefined ? "contribution" : "shap_value"} barSize={20} radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => {
              const val = entry.contribution || entry.shap_value;
              return <Cell key={`cell-${index}`} fill={val >= 0 ? '#ff003c' : '#10b981'} style={{ filter: `drop-shadow(0px 0px 8px ${val >= 0 ? '#ff003c' : '#10b981'})` }} />;
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
