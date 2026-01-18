# SummarizerAI - Complete Monorepo

AI-powered document understanding with deep learning. Complete full-stack application in one repository.

## 📁 Project Structure

```
/
├── backend/              # Backend API + ML Pipeline
│   ├── app/             # FastAPI application
│   │   ├── core/        # Configuration & logging
│   │   ├── models/      # Pydantic schemas
│   │   ├── routers/     # API endpoints (upload, summarize, chat, flashcards)
│   │   └── services/    # Business logic
│   ├── ml/              # ML Pipeline (7 modules)
│   │   ├── layout_ocr.py       # Document processing with OCR
│   │   ├── chunking.py         # Semantic text segmentation
│   │   ├── embeddings.py       # Sentence-BERT embeddings
│   │   ├── faiss_store.py      # FAISS vector search
│   │   ├── rag_pipeline.py     # RAG Q&A system
│   │   ├── persona_summary.py  # Persona-aware summarization
│   │   └── flashcards_gen.py   # AI flashcard generation
│   ├── tests/           # Backend tests
│   └── requirements.txt # Python dependencies
│
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── components/  # UI components (Layout + shadcn/ui)
│   │   ├── pages/       # 5 pages (Home, Upload, Summarize, Chat, Flashcards)
│   │   ├── services/    # API client (16 endpoints)
│   │   └── store/       # Zustand state management
│   └── package.json     # Node dependencies
│
├── run_backend.ps1      # One-click backend launcher
├── run_frontend.ps1     # One-click frontend launcher
└── run_all.ps1          # Launch both servers
```

## 🚀 Quick Start (30 Seconds)

### One Command Launch
```powershell
.\run_all.ps1
```
✅ **Backend**: http://localhost:8000 (API Docs: /docs)  
✅ **Frontend**: http://localhost:3000

### Manual Launch

**Terminal 1 - Backend:**
```powershell
.\run_backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\run_frontend.ps1
```

## 🛠️ Setup (First Time Only)

### Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env file
Copy-Item .env.example .env
# Add your OPENAI_API_KEY to .env

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

### Frontend Setup
```powershell
cd frontend
npm install --legacy-peer-deps

# Frontend uses backend at http://localhost:8000 (configured in vite.config.ts)
```

## 🎯 Features

### Backend (FastAPI + Python)
- **Upload API** - PDF and PowerPoint processing with batch support
- **Summarization** - Persona-aware (Student/Teacher/Expert) summaries
- **Chat API** - RAG-powered document Q&A with conversation history
- **Flashcards** - AI-generated study cards with difficulty levels

### ML Pipeline (PyTorch + Transformers)
- **OCR** - Layout-aware document processing (Tesseract + pdfplumber)
- **Embeddings** - Sentence-BERT semantic vectors (all-mpnet-base-v2)
- **FAISS** - Fast similarity search for document retrieval
- **RAG** - Retrieval-Augmented Generation for accurate Q&A
- **Summarization** - LLM-based adaptive summaries with personas

### Frontend (React + TypeScript)
- **Upload Page** - Drag & drop interface with react-dropzone
- **Summarize** - Multi-persona summaries with comparison
- **Chat** - Interactive document Q&A with history
- **Flashcards** - Generate, view, and export study cards
- **State Management** - Zustand for global state
- **UI Components** - shadcn/ui + Tailwind CSS

## 📚 Tech Stack

### Backend
- FastAPI 0.109.0
- Python 3.10+
- Pydantic 2.5.3
- Uvicorn

### ML/DL
- PyTorch 2.1.2
- Transformers 4.36.2
- Sentence-Transformers 2.2.2
- FAISS 1.7.4
- OpenAI API
- pdfplumber, pytesseract

### Frontend
- React 18.2
- TypeScript 5.9
- Vite 7.2
- Tailwind CSS 3.4
- shadcn/ui
- React Router 6
- Zustand 4.4
- Axios 1.6

## 🧪 Testing

### Backend Tests
```powershell
cd backend
pytest tests/
```

### API Testing
```powershell
# Start backend first
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs for interactive API testing
```

### Full Integration Test
1. Start both servers: `.\run_all.ps1`
2. Open: http://localhost:3000
3. Upload a PDF
4. Test summarization, chat, and flashcards

## 📖 API Endpoints

### Upload (4 endpoints)
- `POST /upload/` - Upload document
- `POST /upload/batch` - Upload multiple documents
- `GET /upload/status/{id}` - Get upload status
- `DELETE /upload/{id}` - Delete document

### Summarize (3 endpoints)
- `POST /summarize/` - Generate summary for specific persona
- `GET /summarize/personas` - Get available persona information
- `POST /summarize/compare` - Compare all personas simultaneously

### Chat (5 endpoints)
- `POST /chat/` - Chat with document
- `POST /chat/multi-turn` - Multi-turn conversation
- `GET /chat/history/{id}` - Get chat history
- `DELETE /chat/history/{id}` - Clear history
- `GET /chat/context/{id}` - Get conversation context

### Flashcards (4 endpoints)
- `POST /flashcards/` - Generate flashcards
- `GET /flashcards/preview/{id}` - Preview topics
- `POST /flashcards/custom` - Create custom card
- `GET /flashcards/export/{id}` - Export flashcards (JSON/CSV)

## 🔧 Configuration

### Backend (.env)
```env
OPENAI_API_KEY=sk-...
EMBEDDINGS_MODEL=all-mpnet-base-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
RETRIEVAL_TOP_K=5
```

### Frontend
Frontend automatically connects to backend at http://localhost:8000 (configured in vite.config.ts proxy)

## 🌐 Deployment

### Recommended
- **Backend**: Render.com (Python)
- **Frontend**: Vercel (React)

### Docker (Coming Soon)
```bash
docker-compose up
```

## 📝 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Fast 3-step setup guide
- [LOCAL_TESTING.md](LOCAL_TESTING.md) - Complete testing guide
- [TEST_BACKEND.md](TEST_BACKEND.md) - Backend API testing with PowerShell
- [API_TESTING.md](API_TESTING.md) - Full API documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

## 🤝 Architecture

This is a complete AI document understanding platform built with:
- **Deep learning** for document processing (PyTorch, Transformers)
- **RAG** for accurate Q&A (FAISS, Sentence-BERT)
- **Persona-aware summarization** (Student/Teacher/Expert)
- **Modern React frontend** with TypeScript and Tailwind CSS

## 📄 License

See LICENSE file

---

**Built with ❤️ using FastAPI, PyTorch, React, and TypeScript**
