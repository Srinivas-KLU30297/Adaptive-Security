import { Download } from 'lucide-react';
import { Button } from '../ui/Button';

interface GradCAMViewerProps {
  base64Image: string;
  regions: { region: string; score: number }[];
}

export function GradCAMViewer({ base64Image, regions }: GradCAMViewerProps) {
  return (
    <div className="w-full mt-6">
      <h3 className="text-text-secondary font-display text-sm tracking-wide mb-4 text-center border-b border-border pb-2">
        GRAD-CAM FORENSIC OVERLAY
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center bg-surface-2 p-6 rounded-xl border border-border">
        
        <div className="relative group rounded-lg overflow-hidden border border-primary/30 shadow-[0_0_15px_rgba(0,212,255,0.15)] flex justify-center bg-black/50">
          <img src={base64Image} alt="Grad-CAM analysis" className="max-w-full h-auto object-contain max-h-[400px]" />
          <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
             <a href={base64Image} download="gradcam_forensic.jpg">
               <Button variant="primary" className="gap-2">
                 <Download size={18} /> Download Evidence
               </Button>
             </a>
          </div>
        </div>

        <div className="space-y-4">
          <h4 className="font-ui font-semibold text-text-primary mb-2">Attention Regions</h4>
          {regions.map((region, idx) => (
            <div key={idx} className="bg-surface p-4 rounded-lg border border-border">
              <div className="flex justify-between items-center mb-2">
                <span className="capitalize font-display text-sm tracking-wider">{region.region}</span>
                <span className="font-body text-primary">{(region.score * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full h-1.5 bg-background rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary shadow-[0_0_8px_rgba(0,212,255,0.8)]"
                  style={{ width: `${region.score * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        
      </div>
    </div>
  );
}
