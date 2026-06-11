# CyberShield — Multi-Modal AI Agent System for Cyber Threat Detection

A scalable multi-agent AI pipeline that classifies cyber threats across **5 input modalities**: image, video, audio, URL, and email — in a single unified system.

## How it works

Inputs are routed to specialized analysis agents based on their type. Each agent applies modality-specific ML models (vision, audio, NLP) and returns a structured signal. A central reasoning layer then aggregates these cross-modal signals into a final threat verdict with a confidence score.

```
Input (image / video / audio / URL / email)
        ↓
  Routing Layer
        ↓
[Vision Agent] [Audio Agent] [NLP Agent] [URL Agent] [Email Agent]
        ↓              ↓           ↓          ↓            ↓
              Central Reasoning & Aggregation Layer
                        ↓
              Structured Threat Verdict
```

## Key results

- **35% reduction in false positives** through ensemble of 4 Hugging Face transformer models with custom heuristics and algorithmic decision boundaries
- **5 input modalities** handled in a single pipeline
- **Temporal video understanding** via frame-extraction and audio sequence analysis using MFCC + wav2vec2
- Internal model evaluation framework with threshold-based scoring to catch hallucinated verdicts

## Tech stack

| Layer | Tools |
|---|---|
| ML models | Hugging Face Transformers, wav2vec2, MFCC |
| Agent orchestration | LangChain, Python |
| Backend API | FastAPI |
| Databases | MongoDB (aggregation pipelines), Elasticsearch (log analytics) |
| Infrastructure | Docker, AWS EC2/S3, GitHub Actions CI/CD |

## Features

- Multi-agent architecture with modality-specific specialists
- Temporal reasoning over video frames and audio sequences (not single-snapshot analysis)
- Model evaluation framework scoring accuracy across all modalities
- CI/CD pipeline with automated deployment to AWS
- Operational monitoring via Elasticsearch log analytics

## Setup

```bash
git clone https://github.com/Srinivas-KLU30297/Adaptive_Security.git
cd Adaptive_Security
pip install -r requirements.txt
docker-compose up
```

## Author

**Kancharla Jo Srinivas** — [LinkedIn](https://www.linkedin.com/in/kancharla-jo-srinivas-08736a360/) · [GitHub](https://github.com/Srinivas-KLU30297)  
B.Tech CSE, KL University (2023–2027) · CGPA 8.64
