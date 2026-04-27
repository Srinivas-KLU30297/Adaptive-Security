import random
import time
import base64
from io import BytesIO
from PIL import Image, ImageDraw
from .base_model import MockModel

class MockImageModel(MockModel):
    def predict(self, file_path: str):
        start = time.time()
        self.simulate_delay()
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                # Simple fake stats
                pixel_variance = random.uniform(30, 60)
        except Exception:
            width, height = 800, 600
            pixel_variance = random.uniform(30, 60)
            
        verdict = "deepfake" if pixel_variance > 45 else "real"
        confidence = 0.8 + random.uniform(0, 0.15)
        
        # Fake Grad-CAM heatmap base64
        heatmap = Image.new('RGB', (224, 224), color=(0, 0, 100))
        d = ImageDraw.Draw(heatmap)
        d.ellipse([50, 50, 150, 150], fill=(255, 0, 0)) # Fake hotspot
        
        buffered = BytesIO()
        heatmap.save(buffered, format="JPEG")
        b64_str = base64.b64encode(buffered.getvalue()).decode()
        
        xai_data = {
            "type": "gradcam",
            "heatmap_base64": f"data:image/jpeg;base64,{b64_str}",
            "image_stats": {"width": width, "height": height, "pixel_variance": pixel_variance},
            "attention_regions": [
                {"region": "eyes", "score": 0.8},
                {"region": "mouth", "score": 0.4}
            ]
        }
        
        ms = int((time.time() - start) * 1000)
        return {"verdict": verdict, "confidence": confidence, "xai_data": xai_data, "processing_time_ms": ms}
