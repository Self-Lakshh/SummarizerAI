<div align="center">

# 🧠 SummarizerAI

### AI-Powered Document Intelligence Platform

Upload any PDF or PowerPoint — get instant summaries, chat with your document, and generate flashcards using state-of-the-art deep learning.

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=for-the-badge&logo=openai&logoColor=white)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Document Upload** | Drag-and-drop PDF & PPT/PPTX with batch support and real-time progress |
| 🧾 **Persona Summaries** | Student · Teacher · Expert adaptive summaries with side-by-side comparison |
| 💬 **RAG Chat** | Ask questions and get cited answers grounded in your document |
| 🃏 **Flashcards** | AI-generated Q&A study cards with difficulty levels and CSV/JSON export |
| 📚 **Document Library** | Browse, search, filter, and manage all your uploaded documents |
| 🔍 **Source Citations** | Every chat response shows the exact passage it came from |

---

## 📁 Project Structure

```
SummarizerAI/
├── backend/                    # FastAPI + ML Pipeline
│   ├── app/
│   │   ├── core/               # Config & structured logging
│   │   ├── models/             # Pydantic v2 schemas
│   │   ├── routers/            # API endpoints (upload, summarize, chat, flashcards)
│   │   └── services/           # Business logic & ML integration
│   ├── ml/                     # 7-module deep learning pipeline
│   │   ├── layout_ocr.py       # PDF/PPT extraction + Tesseract OCR
│   │   ├── chunking.py         # Semantic text segmentation
│   │   ├── embeddings.py       # Sentence-BERT (all-mpnet-base-v2)
│   │   ├── faiss_store.py      # FAISS vector index management
│   │   ├── rag_pipeline.py     # Retrieval-Augmented Generation
│   │   ├── persona_summary.py  # Student / Teacher / Expert summaries
│   │   └── flashcards_gen.py   # AI flashcard generation
│   ├── tests/                  # 27 unit + integration tests
│   └── requirements.txt
│
├── frontend/                   # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/         # Layout, shadcn/ui components
│   │   ├── pages/              # Home · Upload · Library · Summarize · Chat · Flashcards
│   │   ├── services/           # Typed API client (16 endpoints)
│   │   └── store/              # Zustand global state
│   └── package.json
│
├── docker-compose.yml          # Single-command full-stack launch
└── README.md
```

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)

> Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
# 1. Clone the repo
git clone https://github.com/Self-Lakshh/SummarizerAI.git
cd SummarizerAI

# 2. Set your OpenAI key
echo "OPENAI_API_KEY=sk-..." > backend/.env

# 3. Launch everything
docker compose up --build
```

| Service | URL |
|---|---|
| 🖥️ Frontend | http://localhost:3000 |
| ⚡ Backend API | http://localhost:8000 |
| 📖 API Docs (Swagger) | http://localhost:8000/docs |

---

### Option 2 — Manual (Development)

**Backend**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# Copy and fill in your environment variables
cp .env.example .env   # then add OPENAI_API_KEY

python -m nltk.downloader punkt
uvicorn app.main:app --reload --port 8000
```

**Frontend** *(separate terminal)*
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

---

## 🛠️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic_v2-E92063?logo=pydantic&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-grey?logo=gunicorn&logoColor=white)

### Machine Learning
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/🤗_Transformers-FFD21E?logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI_API-412991?logo=openai&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-0467DF?logo=meta&logoColor=white)

### Frontend
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)
![Zustand](https://img.shields.io/badge/Zustand-433E38?logo=react&logoColor=white)
![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-000000?logo=shadcnui&logoColor=white)

### DevOps
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)

---

## 📡 API Reference

### Upload
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/upload/` | Upload a single document |
| `POST` | `/api/v1/upload/batch` | Upload multiple documents |
| `GET` | `/api/v1/upload/status/{id}` | Get processing status |
| `GET` | `/api/v1/upload/list` | List all uploaded documents |
| `DELETE` | `/api/v1/upload/{id}` | Delete a document |

### Summarize
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/summarize/` | Generate persona summary |
| `GET` | `/api/v1/summarize/personas` | List available personas |
| `POST` | `/api/v1/summarize/compare` | Compare all personas at once |

### Chat
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat/` | Ask a question (RAG) |
| `POST` | `/api/v1/chat/multi-turn` | Multi-turn conversation |
| `GET` | `/api/v1/chat/history/{id}` | Retrieve chat history |
| `DELETE` | `/api/v1/chat/history/{id}` | Clear chat history |

### Flashcards
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/flashcards/` | Generate AI flashcards |
| `GET` | `/api/v1/flashcards/preview/{id}` | Preview topics |
| `POST` | `/api/v1/flashcards/custom` | Add a custom card |
| `GET` | `/api/v1/flashcards/export/{id}` | Export JSON or CSV |

> Full interactive docs available at **http://localhost:8000/docs** when running.

---

## ⚙️ Configuration

### Backend — `backend/.env`
```env
# Required
OPENAI_API_KEY=sk-...

# Optional overrides
LLM_MODEL=gpt-3.5-turbo
EMBEDDINGS_MODEL=sentence-transformers/all-mpnet-base-v2
UPLOAD_DIR=uploads
FAISS_INDEX_DIR=faiss_indices
LOG_LEVEL=INFO
```

### Frontend
The Vite dev server proxies `/api/v1/` → `http://localhost:8000` automatically via `vite.config.ts`.
In Docker, Nginx handles the same proxy routing.

---

## 🧪 Testing

```bash
cd backend

# Run full test suite
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

**Current status: 27 tests · 0 failures**

---

## 🗺️ Roadmap

### Phase 1 — Foundation ✅
- [x] FastAPI backend with 4 router groups (upload, summarize, chat, flashcards)
- [x] 7-module ML pipeline (OCR → chunking → embeddings → FAISS → RAG → summaries → flashcards)
- [x] React frontend with all core pages
- [x] Pydantic v2 schemas for all request/response payloads
- [x] Document JSON persistence layer

### Phase 2 — Quality & Production ✅
- [x] 27 unit + integration backend tests
- [x] Document Library page (search, filter, delete)
- [x] Source citations in Chat (passage-level context viewer)
- [x] Interactive Study Mode for Flashcards (flip, track progress, mark learned)
- [x] Docker Compose full-stack containerisation (Nginx, FastAPI, React)
- [x] Pydantic v2 migration (`model_config = SettingsConfigDict`)
- [x] Frontend production build — 1543 modules, 0 TypeScript errors

### Phase 3 — Scale & Polish 🔜
- [ ] Async background task processing (Celery / FastAPI BackgroundTasks)
- [ ] Rate limiting middleware (slowapi)
- [ ] PostgreSQL document metadata store
- [ ] Streaming chat responses (Server-Sent Events)
- [ ] Study dashboard with mastery analytics
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Cloud deployment guides (Render + Vercel / AWS ECS)

---

## 📄 License

[MIT](LICENSE) — © 2025 SummarizerAI

---

<div align="center">

Built with ❤️ using&nbsp;
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)&nbsp;
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)&nbsp;
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)&nbsp;
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)

</div>
