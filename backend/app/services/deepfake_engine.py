import cv2
import numpy as np
from PIL import Image
import torch
from transformers import pipeline
import librosa

class DeepfakeEngine:
    def __init__(self):
        print("Loading Image Detection Ensembles...")
        
        self.deepfake_model = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")
        self.sdxl_model = pipeline("image-classification", model="Organika/sdxl-detector")
        # Substituted unavailable autotrain ID with the public deployed version from the same author
        self.gemini_model = pipeline("image-classification", model="haywoodsloan/ai-image-detector-deploy")
        
        print("Loading Audio Detection Model...")
        self.audio_model = pipeline("audio-classification", model="garystafford/wav2vec2-deepfake-voice-detector")
        
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        print("Models loaded successfully.")

    def resize_image(self, img, max_size=800):
        h, w = img.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)
        return img

    def process_image(self, file_path: str):
        img = cv2.imread(file_path)
        if img is None:
            return {"verdict": "invalid", "error": "Invalid Image: Could not read file", "confidence": 0.0}

        img_resized = self.resize_image(img, max_size=800)
        
        # 1. OpenCV face check
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        face_detected = len(faces) > 0
        
        if not face_detected:
            return {"verdict": "invalid", "error": "No face detected in the image. Please upload a portrait.", "confidence": 0.0}
        
        # Prepare PIL image for HF pipeline
        pil_img = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
        
        reasons = ["Face detected in image"]
        
        # 2A. Run Model 2A (SDXL Detector)
        sdxl_res = self.sdxl_model(pil_img)
        sdxl_top = sdxl_res[0]
        sdxl_label = sdxl_top["label"].lower()
        if "fake" in sdxl_label or "artificial" in sdxl_label or "generated" in sdxl_label:
            sdxl_score = sdxl_top["score"]
        else:
            sdxl_score = 1.0 - sdxl_top["score"]

        # 2B. Run Model 2B (Gemini Detector)
        gemini_res = self.gemini_model(pil_img)
        gemini_top = gemini_res[0]
        gemini_label = gemini_top["label"].lower()
        if "artificial" in gemini_label or "fake" in gemini_label or "generated" in gemini_label:
            gemini_score = gemini_top["score"]
        else:
            gemini_score = 1.0 - gemini_top["score"]
            
        # Heuristic Suppression: 
        # 1. Models frequently false-positive on low-quality webcam faces. We dampen them slightly.
        sdxl_score = sdxl_score * 0.85
        gemini_score = gemini_score * 0.85
            
        ai_generated_score = max(sdxl_score, gemini_score)
        reasons.append(f"AI image detector flagged with {ai_generated_score*100:.0f}% confidence")

        # 3. Run Model 1 (Deepfake Detector) on FULL image
        df_res = self.deepfake_model(pil_img)
        df_top = df_res[0]
        df_label = df_top["label"].lower()
        if "fake" in df_label:
            deepfake_score = df_top["score"]
        else:
            deepfake_score = 1.0 - df_top["score"]
            
        reasons.append(f"Deepfake model flagged with {deepfake_score*100:.0f}% confidence")
        
        # Weighted ensemble
        final_score = (deepfake_score * 0.40) + (ai_generated_score * 0.60)

        # Hard Rule: 
        # - Deepfake and Gemini > 0.80 trigger immediately.
        # - SDXL > 0.80 ONLY triggers if Gemini corroborates it (> 0.40) to prevent false positives.
        if deepfake_score > 0.80 or gemini_score > 0.80 or (sdxl_score > 0.80 and gemini_score > 0.40):
            final_score = max(deepfake_score, sdxl_score, gemini_score)
            verdict = "threat"
            if deepfake_score == final_score:
                threat_type = "deepfake"
                label = "Deepfake Detected"
            else:
                threat_type = "ai_generated"
                label = "AI Generated Image Detected"
        else:
            if final_score > 0.75:
                verdict = "threat"
                if deepfake_score > ai_generated_score:
                    threat_type = "deepfake"
                    label = "Deepfake Detected"
                else:
                    threat_type = "ai_generated"
                    label = "AI Generated Image Detected"
            elif final_score > 0.55:
                verdict = "suspicious"
                threat_type = "deepfake" if deepfake_score > ai_generated_score else "ai_generated"
                label = "Suspicious Image"
            else:
                verdict = "real"
                threat_type = "real"
                label = "System Clear"

        return {
            "verdict": verdict,
            "threat_type": threat_type,
            "label": label,
            "confidence": float(final_score),
            "deepfake_score": float(deepfake_score),
            "sdxl_score": float(sdxl_score),
            "gemini_score": float(gemini_score),
            "ai_generated_score": float(ai_generated_score),
            "face_detected": bool(face_detected),
            "reasons": reasons
        }

    def process_video(self, file_path: str, num_frames=5):
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return {"verdict": "invalid", "error": "Could not open video file", "confidence": 0.0}
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            return {"verdict": "invalid", "error": "Video has no frames", "confidence": 0.0}
            
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        deepfake_scores = []
        ai_generated_scores = []
        sdxl_scores = []
        gemini_scores = []
        faces_detected = 0
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
                
            img_resized = self.resize_image(frame, max_size=800)
            
            # Check face
            gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) > 0:
                faces_detected += 1
                
            pil_img = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
            
            # SDXL
            sdxl_res = self.sdxl_model(pil_img)[0]
            sdxl_score = sdxl_res["score"] if any(x in sdxl_res["label"].lower() for x in ["fake", "artificial", "generated"]) else 1.0 - sdxl_res["score"]
            sdxl_scores.append(sdxl_score * 0.85)
            
            # Gemini
            gemini_res = self.gemini_model(pil_img)[0]
            gemini_score = gemini_res["score"] if any(x in gemini_res["label"].lower() for x in ["artificial", "fake", "generated"]) else 1.0 - gemini_res["score"]
            gemini_scores.append(gemini_score * 0.85)
            
            # Deepfake
            df_res = self.deepfake_model(pil_img)[0]
            df_score = df_res["score"] if "fake" in df_res["label"].lower() else 1.0 - df_res["score"]
            deepfake_scores.append(df_score)
            
            ai_generated_scores.append(max(sdxl_scores[-1], gemini_scores[-1]))
            
        cap.release()
        
        if not deepfake_scores:
            return {"verdict": "invalid", "error": "Could not read frames from video", "confidence": 0.0}
            
        # Aggregate scores (using max to catch any blatant deepfake/AI frames)
        max_deepfake = max(deepfake_scores)
        max_ai_gen = max(ai_generated_scores)
        max_sdxl = max(sdxl_scores)
        max_gemini = max(gemini_scores)
        
        final_score = (max_deepfake * 0.40) + (max_ai_gen * 0.60)
        
        reasons = [f"Analyzed {len(deepfake_scores)} frames from video."]
        if faces_detected > 0:
            reasons.append(f"Faces detected in {faces_detected} frames.")
        else:
            reasons.append("No faces detected in analyzed frames.")
            
        reasons.append(f"Max AI generated score across frames: {max_ai_gen*100:.0f}%")
        reasons.append(f"Max Deepfake score across frames: {max_deepfake*100:.0f}%")
        
        if max_deepfake > 0.80 or max_gemini > 0.80 or (max_sdxl > 0.80 and max_gemini > 0.40):
            final_score = max(max_deepfake, max_sdxl, max_gemini)
            verdict = "threat"
            if max_deepfake == final_score:
                threat_type = "deepfake_video"
                label = "Deepfake Video Detected"
            else:
                threat_type = "ai_generated_video"
                label = "AI Generated Video Detected"
        else:
            if final_score > 0.75:
                verdict = "threat"
                if max_deepfake > max_ai_gen:
                    threat_type = "deepfake_video"
                    label = "Deepfake Video Detected"
                else:
                    threat_type = "ai_generated_video"
                    label = "AI Generated Video Detected"
            elif final_score > 0.55:
                verdict = "suspicious"
                threat_type = "deepfake_video" if max_deepfake > max_ai_gen else "ai_generated_video"
                label = "Suspicious Video"
            else:
                verdict = "real"
                threat_type = "real"
                label = "System Clear"

        return {
            "verdict": verdict,
            "threat_type": threat_type,
            "label": label,
            "confidence": float(final_score),
            "deepfake_score": float(max_deepfake),
            "sdxl_score": float(max_sdxl),
            "gemini_score": float(max_gemini),
            "ai_generated_score": float(max_ai_gen),
            "face_detected": bool(faces_detected > 0),
            "reasons": reasons
        }

    def process_audio(self, file_path: str):
        try:
            # Load audio using librosa
            y, sr = librosa.load(file_path, sr=16000, duration=10.0)
            if len(y) == 0:
                return {"verdict": "invalid", "error": "Audio file is empty or corrupted", "confidence": 0.0}
            
            # Extract features (as described in the PhD proposal)
            # 1. MFCC (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfccs.T, axis=0)
            mfcc_var = np.var(mfccs.T, axis=0)
            
            # 2. Chroma STFT (Short-time Fourier transform)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma.T, axis=0)
            
            # 3. Spectral Contrast
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            contrast_var = np.var(contrast.T, axis=0)

            # Run real Hugging Face transformer model
            # Note: garystafford/wav2vec2-deepfake-voice-detector expects 16kHz
            res = self.audio_model({"array": y, "sampling_rate": sr})
            
            fake_score = 0.0
            real_score = 0.0
            
            for item in res:
                label = item['label'].lower()
                if 'fake' in label or 'spoof' in label:
                    fake_score = item['score']
                elif 'real' in label or 'bonafide' in label or 'bona-fide' in label or 'original' in label:
                    real_score = item['score']
            
            if fake_score == 0.0 and real_score > 0.0:
                fake_score = 1.0 - real_score
            elif fake_score == 0.0:
                fake_score = res[0]['score'] if res[0]['label'].lower() != 'real' and 'bona' not in res[0]['label'].lower() and 'original' not in res[0]['label'].lower() else 1.0 - res[0]['score']

            rf_confidence = fake_score
            
            reasons = [
                f"Processed audio through garystafford wav2vec2-deepfake model.",
                f"Model analysis completed successfully."
            ]
            
            if rf_confidence > 0.70:
                verdict = "threat"
                threat_type = "deepfake_audio"
                label = "Deepfake Audio Detected"
                reasons.append(f"Transformer neural network flagged audio as synthetic with {rf_confidence*100:.1f}% confidence.")
            elif rf_confidence > 0.45:
                verdict = "suspicious"
                threat_type = "deepfake_audio"
                label = "Suspicious Audio"
                reasons.append(f"Detected minor anomalies in voice generation ({rf_confidence*100:.1f}% confidence).")
            else:
                verdict = "real"
                threat_type = "real"
                label = "System Clear"
                reasons.append("Neural analysis confirms audio is consistent with real human voice.")

            return {
                "verdict": verdict,
                "threat_type": threat_type,
                "label": label,
                "confidence": float(rf_confidence),
                "deepfake_score": float(rf_confidence),
                "sdxl_score": 0.0,
                "gemini_score": 0.0,
                "ai_generated_score": float(rf_confidence),
                "face_detected": False,
                "reasons": reasons
            }
        except Exception as e:
            return {"verdict": "invalid", "error": f"Failed to process audio: {str(e)}", "confidence": 0.0}

    def fused_analysis(self, file_path: str, media_type="image"):
        if media_type == "image":
            return self.process_image(file_path)
        elif media_type == "video":
            return self.process_video(file_path)
        elif media_type == "audio":
            return self.process_audio(file_path)
        return {"verdict": "invalid", "error": f"Unsupported media type: {media_type}", "confidence": 0.0}

deepfake_engine = DeepfakeEngine()
