# McDonald's Nutrition Chatbot - Backend

Backend API untuk chatbot nutrisi McDonald's menggunakan FastAPI dengan RAG (Retrieval Augmented Generation).

## Tech Stack

- **FastAPI**: Web framework untuk API
- **Sentence Transformers**: Untuk embedding dan retrieval
- **Hugging Face Transformers**: Model LLM bahasa Indonesia (IndoT5-base)
- **PyTorch**: Deep learning framework

## Model yang Digunakan

1. **Embedding Model**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
   - Untuk mengkonversi teks menjadi vector embeddings
   - Mendukung bahasa Indonesia

2. **LLM Model**: `Wikidepia/IndoT5-base`
   - Model T5 yang di-fine-tune untuk bahasa Indonesia
   - Digunakan untuk generate response

## Cara Menjalankan

### 1. Setup Virtual Environment (Recommended)

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat

# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan Server

```bash
# Dari folder backend
python main.py

# Atau menggunakan uvicorn langsung
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di `http://localhost:8000`

## API Endpoints

### 1. Chat Endpoint
```
POST /api/chat
Content-Type: application/json

{
  "message": "Berapa kalori Big Mac?"
}
```

Response:
```json
{
  "response": "Big Mac memiliki 528.8 kkal...",
  "relevant_items": [...]
}
```

### 2. Get All Menu
```
GET /api/menu
```

### 3. Get Menu by Category
```
GET /api/menu/category/Breakfast
```

## RAG Architecture

1. **Retrieval**: Menggunakan sentence embeddings untuk mencari menu yang relevan
2. **Augmentation**: Menambahkan context dari menu yang di-retrieve
3. **Generation**: LLM menggenerate response berdasarkan context

## Model Alternatif (Bahasa Indonesia)

Jika ingin mencoba model lain:

1. **IndoGPT** - `indonesian-nlp/gpt2-small-indonesian-522M`
2. **IndoBART** - `indobenchmark/indobart-v2`
3. **mBART** - `facebook/mbart-large-50`
4. **IndoNLG** - `Wikidepia/IndoNLG-base`

Ganti `model_name` di `main.py` untuk mencoba model berbeda.
