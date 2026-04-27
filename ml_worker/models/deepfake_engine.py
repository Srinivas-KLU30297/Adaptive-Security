import os
import cv2
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

class DeepfakeEngine:
    def __init__(self):
        print("Loading CommunityForensics ViT deepfake detection model...")
        # #1 most downloaded deepfake model on HuggingFace
        # Trained on 2.7M images from 4,803 AI generators (Stable Diffusion, MidJourney, DALL-E, etc.)
        # Published paper: arXiv:2411.04125 (University of Michigan)
        model_name = "buildborderless/CommunityForensics-DeepfakeDet-ViT"
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        self.model.eval()
        
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        print("Model loaded successfully.")

    def process_image(self, file_path: str):
        img = cv2.imread(file_path)
        if img is None:
            return {"verdict": "invalid", "error": "Invalid Image: Could not read file", "confidence": 0.0}
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return {"verdict": "invalid", "error": "Invalid Image: No Face Detected", "confidence": 0.0}

        # Run inference on the full image for best context
        # CommunityForensics ViT requires 384x384 input
        full_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(full_rgb).resize((384, 384), Image.LANCZOS)
        
        inputs = self.processor(images=pil_img, return_tensors="pt")
        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        probs = torch.softmax(logits, dim=-1)[0]
        
        # Get label mapping from model config
        id2label = self.model.config.id2label
        results = [{"label": id2label[i], "score": float(probs[i])} for i in range(len(probs))]
        results.sort(key=lambda x: x["score"], reverse=True)
        top = results[0]
        
        label = top["label"].lower()
        score = top["score"]
        
        # CommunityForensics labels: "real" or "fake"
        is_fake = "fake" in label or "ai" in label or "generated" in label
        verdict = "deepfake" if is_fake else "real"
        
        return {
            "verdict": verdict,
            "confidence": score,
            "label": label,
            "all_scores": results
        }

    def fused_analysis(self, file_path: str, media_type="video"):
        if media_type == "image":
            return self.process_image(file_path)
        return {"verdict": "invalid", "error": f"Unsupported media type: {media_type}", "confidence": 0.0}

deepfake_engine = DeepfakeEngine()
