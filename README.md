# McDonald's Nutrition Chatbot

Aplikasi chatbot untuk informasi nutrisi menu McDonald's Indonesia menggunakan RAG (Retrieval Augmented Generation) dan model LLM bahasa Indonesia.

## 🏗️ System Architecture

┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Frontend)                 │
│                     Next.js + TypeScript                     │
│                                                            │
│   • ChatInterface.tsx - Main chat component                │
│   • ChatMessage.tsx - Message display component            │
│   • ChatInput.tsx - Input handling component               │
│   • Tailwind CSS - Styling & McDonald's branding           │
│   • ShadCN UI - Pre-built UI components                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│            API COMMUNICATION & DATA FLOW                     │
│                 HTTP/JSON Protocol                          │
│                                                            │
│   • Frontend → Backend: POST /api/chat                     │
│   • Request: { message: string, session_id?: string }      │
│   • Response: { response: string, relevant_items: array }  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND PROCESSING                         │
│                  FastAPI + RAG System                       │
│                                                            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │        STEP 1: EMBEDDING MODEL (Retrieval)          │   │
│   │  • Model: paraphrase-multilingual-mpnet-base-v2     │   │
│   │  • Function: Convert text to semantic embeddings    │   │
│   │  • Output: 768-dimensional vector                    │   │
│   └─────────────────────────────────────────────────────┘   │
│                              ↓                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │      STEP 2: VECTOR SEARCH & RETRIEVAL              │   │
│   │  • In-Memory Vector Database                        │   │
│   │  • Cosine Similarity Calculation                    │   │
│   │  • Name Boosting (25% if menu name in query)       │   │
│   │  • Threshold Filtering (similarity > 0.25)         │   │
│   │  • Top-3 Most Relevant Items Retrieved             │   │
│   └─────────────────────────────────────────────────────┘   │
│                              ↓                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │      STEP 3: LLM GENERATION (Gemini)                │   │
│   │  • Model: gemini-2.0-flash-exp                      │   │
│   │  • Temperature: 0.85 (creative responses)          │   │
│   │  • Top-p: 0.90 (diverse outputs)                   │   │
│   │  • Top-k: 50 (exploration)                         │   │
│   │  • Max tokens: 300 (concise responses)             │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                 CONVERSATION MEMORY                          │
│              Session-based Context Management               │
│                                                            │
│   • Session ID tracking per user                           │
│   • Conversation history (max 10 exchanges)               │
│   • Context injection for follow-up queries                │
│   • Automatic cleanup of old sessions (>1 hour)          │
└─────────────────────────────────────────────────────────────┘

## 🚀 Tech Stack

### Frontend
- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **ShadCN UI** - UI components
- **Lucide React** - Icons

### Backend
- **FastAPI** - Python web framework
- **Sentence Transformers** - Embedding model
- **Google Gemini** - LLM (gemini-2.0-flash-exp)
- **PyTorch** - Deep learning
- **RAG Architecture** - Retrieval Augmented Generation

## 📁 Struktur Direktori

```
nutrition-mcd/
├── app/                          # Next.js app directory
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page (Chatbot)
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   ├── ChatMessage.tsx      # Message component
│   │   └── ChatInput.tsx        # Input component
│   └── ui/                      # ShadCN UI components
│       ├── button.tsx
│       ├── input.tsx
│       ├── avatar.tsx
│       └── scroll-area.tsx
├── lib/
│   └── utils.ts                 # Utility functions
├── backend/
│   ├── main.py                  # FastAPI server
│   ├── requirements.txt         # Python dependencies
│   ├── README.md               # Backend documentation
│   └── knowledge_json/
│       └── mcd_nutrition_cleaned.json  # Nutrition data
├── public/                      # Static files
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md
```

## 🎯 Fitur

- ✅ Chat interface mirip ChatGPT
- ✅ RAG untuk retrieval informasi nutrisi akurat
- ✅ Model LLM bahasa Indonesia (IndoT5-base)
- ✅ Real-time chat dengan loading states
- ✅ Responsive design (mobile & desktop)
- ✅ Dark mode support
- ✅ Sidebar dengan informasi aplikasi
- ✅ Semantic search untuk mencari menu

## 🛠️ Cara Menjalankan

### 1. Install Dependencies Frontend

```bash
# Install package npm
npm install

# Atau dengan yarn
yarn install

# Atau dengan pnpm
pnpm install
```

### 2. Setup Backend

```bash
# Masuk ke folder backend
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install dependencies Python
pip install -r requirements.txt
```

### 3. Jalankan Backend Server

```bash
# Dari folder backend
python main.py

# Backend akan berjalan di http://localhost:8000
```

### 4. Jalankan Frontend

```bash
# Kembali ke root folder
cd ..

# Jalankan Next.js development server
npm run dev

# Frontend akan berjalan di http://localhost:3000
```

## 💬 Cara Menggunakan

1. Buka browser dan akses `http://localhost:3000`
2. Ketik pertanyaan tentang nutrisi menu McDonald's
3. Contoh pertanyaan:
   - "Berapa kalori Big Mac?"
   - "Menu sarapan apa yang rendah kalori?"
   - "Kandungan gula McFlurry berapa?"
   - "Rekomendasi menu dengan lemak rendah"
   - "Bandingkan kalori Chicken McNuggets dan McSpicy"

## 🤖 Model AI yang Digunakan

### Embedding Model
**sentence-transformers/paraphrase-multilingual-mpnet-base-v2**
- Untuk semantic search dan retrieval
- Mendukung bahasa Indonesia
- Menghasilkan embeddings 768-dimensi

### LLM Model
**Gemini**


## 📊 Data Nutrisi

Data nutrisi diambil dari menu McDonald's Indonesia dengan informasi:
- ✅ Nama menu
- ✅ Kategori (Breakfast, Ayam, Burger, Drinks, Desserts, dll)
- ✅ Kalori (kkal)
- ✅ Gula (gram)
- ✅ Garam (mg)
- ✅ Lemak (gram)
- ✅ URL sumber

## 🎨 UI Design

Interface menggunakan design system ChatGPT dengan:
- Clean & modern layout
- Sidebar untuk navigasi
- Avatar untuk user dan bot
- Smooth scrolling
- Loading animations
- Responsive design

## 🔧 Konfigurasi

### Frontend Environment (Opsional)
Buat file `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Configuration
Backend sudah dikonfigurasi untuk:
- CORS: Allow dari `http://localhost:3000`
- Port: 8000
- Host: 0.0.0.0 (accessible dari network)

## 📝 API Endpoints

### Chat
```http
POST http://localhost:8000/api/chat
Content-Type: application/json

{
  "message": "Berapa kalori Big Mac?"
}
```

### Get All Menu
```http
GET http://localhost:8000/api/menu
```

### Get Menu by Category
```http
GET http://localhost:8000/api/menu/category/Breakfast
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
npm run build
vercel deploy
```

### Backend (Railway/Render)
```bash
# Pastikan requirements.txt sudah lengkap
# Deploy menggunakan platform pilihan
```

## 📦 Dependencies

### Frontend
- Next.js 16
- React 19
- Tailwind CSS 4
- Radix UI components
- Lucide icons

### Backend
- FastAPI 0.115.0
- Transformers 4.45.2
- Sentence Transformers 3.1.1
- PyTorch 2.5.1
- Uvicorn 0.32.0

## 🤝 Contributing

Feel free to contribute! Pull requests are welcome.

## 📄 License

MIT License

---

**Happy Coding! 🚀**

