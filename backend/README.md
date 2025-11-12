# McDonald's Nutrition Chatbot - Backend

Backend API untuk chatbot nutrisi McDonald's menggunakan FastAPI dengan RAG (Retrieval Augmented Generation).

## Tech Stack
┌─────────────────────────────────────────────────────────┐
│                  USER INPUT (Query)                      │
│           "Berapa kalori Big Mac?"                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         MODEL 1: EMBEDDING MODEL (Retrieval)             │
│   sentence-transformers/paraphrase-multilingual-mpnet    │
│                                                          │
│   Input: Text query                                      │
│   Output: Vector 768 dimensi                            │
│   Function: Semantic search untuk cari menu relevan     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              VECTOR DATABASE (In-Memory)                 │
│   77 menu items × 768 dimensions = Embedding Matrix     │
│   Cosine Similarity Search → Top 3 relevant items       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│       MODEL 2: LLM (Text Generation)                     │
│            Google Gemini 2.0 Flash Exp                   │
│                                                          │
│   Input: Prompt + Context (retrieved data)              │
│   Output: Natural language response                     │
│   Function: Generate human-like answer                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  FINAL RESPONSE                          │
│   "Big Mac punya 528.8 kkal dengan lemak 25.38g..."    │
└─────────────────────────────────────────────────────────┘
- **FastAPI**: Web framework untuk API
- **Sentence Transformers**: Untuk embedding dan retrieval
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


# System Architecture

┌─────────────────────────────────────────────────────────────┐
│                  USER INPUT (Query)                          │
│              "Berapa kalori Big Mac?"                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         STEP 1: EMBEDDING MODEL (Semantic Search)            │
│   sentence-transformers/paraphrase-multilingual-mpnet-v2     │
│                                                              │
│   Input:  Text query                                         │
│   Output: 768-dimensional vector                            │
│   Function: Convert text to semantic embeddings             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              STEP 2: VECTOR SEARCH (Retrieval)               │
│   In-Memory Vector Database                                  │
│   77 menu items × 768 dimensions = Embedding Matrix         │
│                                                              │
│   • Cosine Similarity Calculation                           │
│   • Name Boosting (25% if menu name in query)              │
│   • Threshold Filtering (similarity > 0.25)                │
│   • Top-3 Most Relevant Items Retrieved                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         STEP 3: CONVERSATION MEMORY (Context)                │
│   Session-Based History Storage                              │
│                                                              │
│   • Last 3 conversations loaded                             │
│   • Automatic session cleanup (> 1 hour)                    │
│   • User + Assistant messages tracked                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         STEP 4: RESPONSE GENERATION (Gemini AI)              │
│              Google Gemini 2.0 Flash Exp                     │
│                                                              │
│   Input:  • Prompt with persona (Ronald AI)                 │
│           • Retrieved nutritional data                      │
│           • Conversation history                            │
│           • Random personality trait                        │
│                                                              │
│   Config: • Temperature: 0.85 (creative)                    │
│           • Top-P: 0.90 (diverse)                           │
│           • Max Tokens: 300                                 │
│                                                              │
│   Output: Natural, conversational Indonesian response       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         STEP 5: POST-PROCESSING (Formatting)                 │
│                                                              │
│   • Clean artifacts ("Jawaban:", etc.)                      │
│   • Add formatted nutrition details (with emojis)           │
│   • Append health tips (caring tone)                        │
│   • Fallback if response too short                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  FINAL JSON RESPONSE                         │
│                                                              │
│   {                                                          │
│     "response": "Big Mac punya 528.8 kkal dengan...",       │
│     "relevant_items": [...],                                │
│     "session_id": "session_123..."                          │
│   }                                                          │
└─────────────────────────────────────────────────────────────┘