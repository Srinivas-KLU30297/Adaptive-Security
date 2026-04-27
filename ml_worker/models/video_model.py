import time
from .base_model import MockModel
from .deepfake_engine import deepfake_engine

class MockVideoModel(MockModel):
    def predict(self, file_path: str):
        start = time.time()
        self.simulate_delay()
        
        # Utilize the IEEE 2023 Multi-Modal Fusion Algorithm
        result = deepfake_engine.fused_analysis(file_path, media_type="video")
        
        xai_data = {
            "type": "fusion_explainer",
            "top_features": result['xai_top_features'],
            "visual_branch_score": result['visual_probability']
        }
        
        ms = int((time.time() - start) * 1000)
        return {
            "verdict": result['verdict'], 
            "confidence": result['confidence'], 
            "xai_data": xai_data, 
            "processing_time_ms": ms
        }
