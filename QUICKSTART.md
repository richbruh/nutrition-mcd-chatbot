# 🚀 Quick Start Guide - McDonald's Nutrition Chatbot

## Prerequisites

- Node.js 18+ dan npm/yarn/pnpm
- Python 3.9+
- Git

## 📥 Langkah-langkah Setup

### 1️⃣ Install Dependencies Frontend

```powershell
# Pastikan Anda berada di root folder project
npm install
```

### 2️⃣ Setup Python Backend

```powershell
# Masuk ke folder backend
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies Python
pip install -r requirements.txt

# Kembali ke root folder
cd ..
```

### 3️⃣ Jalankan Backend Server

```powershell
# Di terminal baru, masuk ke folder backend
cd backend

# Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# Jalankan server
python main.py
```

**Output yang diharapkan:**
```
Loading embedding model...
Loading LLM model for Indonesian...
Model loaded on cpu
Creating embeddings for menu items...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

⏰ **Note:** First run akan download model (~1-2GB), mohon bersabar!

### 4️⃣ Jalankan Frontend

```powershell
# Di terminal baru, pastikan di root folder
npm run dev
```

**Output yang diharapkan:**
```
▲ Next.js 16.0.0
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000
```

### 5️⃣ Akses Aplikasi

Buka browser dan akses:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 💬 Contoh Pertanyaan

Coba tanyakan:
- "Berapa kalori Big Mac?"
- "Menu sarapan apa yang rendah kalori?"
- "Kandungan gula McFlurry OREO berapa?"
- "Rekomendasi burger dengan lemak rendah"
- "Bandingkan kalori McNuggets dan McSpicy"

## 🔧 Troubleshooting

### Error: Port 3000 already in use
```powershell
# Ganti port Next.js
npm run dev -- -p 3001
```

### Error: Port 8000 already in use
```python
# Edit backend/main.py, ganti port di baris terakhir:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Error: Model download gagal
```powershell
# Set HuggingFace cache
$env:TRANSFORMERS_CACHE="./models"
python main.py
```

### Error: CUDA/GPU tidak terdeteksi
Tidak masalah! Model akan otomatis menggunakan CPU. 
Untuk menggunakan GPU, install PyTorch dengan CUDA support:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 📊 Struktur Project

```
nutrition-mcd/
├── app/                    # Next.js pages
│   ├── page.tsx           # Home (Chat interface)
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── chat/              # Chat components
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   └── ChatInput.tsx
│   └── ui/                # ShadCN components
├── backend/
│   ├── main.py            # FastAPI server
│   ├── requirements.txt   # Python deps
│   └── knowledge_json/
│       └── mcd_nutrition_cleaned.json
└── package.json
```

## 🎯 Tech Stack

**Frontend:**
- Next.js 16 + React 19
- TypeScript
- Tailwind CSS 4
- ShadCN UI
- Lucide Icons

**Backend:**
- FastAPI (Python)
- Sentence Transformers (Embedding)
- Hugging Face Transformers (LLM)
- IndoT5-base (Indonesian Model)
- RAG Architecture

## 🤖 Model yang Digunakan

1. **Embedding:** `paraphrase-multilingual-mpnet-base-v2`
   - Untuk semantic search
   - Size: ~420MB

2. **LLM:** `Wikidepia/IndoT5-base`
   - Indonesian language model
   - Size: ~900MB

## ⚡ Performance Tips

- **GPU:** Install PyTorch with CUDA for faster inference
- **Model Cache:** Models disimpan di `~/.cache/huggingface`
- **RAM:** Minimum 8GB recommended
- **Storage:** ~2GB untuk models

## 📝 API Testing

Test backend API dengan curl:

```powershell
# Test health check
curl http://localhost:8000

# Test chat
curl -X POST http://localhost:8000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "Berapa kalori Big Mac?"}'

# Get all menu
curl http://localhost:8000/api/menu
```

## 🎨 Customization

### Ganti Model LLM
Edit `backend/main.py`:
```python
# Ganti dengan model lain
model_name = "indobenchmark/indobart-v2"
# atau
model_name = "facebook/mbart-large-50"
```

### Ganti Warna Theme
Edit `app/globals.css` untuk mengubah color scheme.

### Tambah Data Menu
Tambahkan data baru di `backend/knowledge_json/mcd_nutrition_cleaned.json`

## 🚀 Production Deployment

### Frontend (Vercel)
```powershell
npm run build
vercel deploy
```

### Backend (Railway/Render)
1. Push code ke GitHub
2. Connect repository ke Railway/Render
3. Set environment variables
4. Deploy!

## 📞 Support

Jika ada masalah:
1. Check error logs di terminal
2. Pastikan semua dependencies terinstall
3. Restart both frontend dan backend
4. Check firewall/antivirus

## ⭐ Features

✅ Real-time chat interface  
✅ RAG-based accurate retrieval  
✅ Indonesian language support  
✅ Responsive design  
✅ Dark mode ready  
✅ Fast semantic search  
✅ Loading states & animations  

---

**Happy coding! 🎉**
