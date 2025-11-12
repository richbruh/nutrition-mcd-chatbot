import os
import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai

load_dotenv()

app = FastAPI(
    title="McDonald's Nutrition Chatbot API",
    description="RAG-powered nutrition assistant with conversational AI",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CONFIGURATION ====================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

gemini_client = None
if not GOOGLE_API_KEY:
    print("⚠️  WARNING: GOOGLE_API_KEY missing in .env")
else:
    gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    print("✅ Gemini client configured")

# ==================== DATA LOADING ====================
DATA_PATH = os.path.join(os.path.dirname(__file__), "knowledge_json", "mcd_nutrition_cleaned.json")
EMB_CACHE_PATH = os.path.join(os.path.dirname(__file__), "menu_embeddings.npy")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    nutrition_data = json.load(f)

print(f"📊 Loaded {len(nutrition_data)} menu items")

# Validasi data
REQUIRED_FIELDS = {"nama_menu", "kategori", "Kalori", "Gula", "Garam", "Lemak"}
incomplete = any(not REQUIRED_FIELDS.issubset(item.keys()) for item in nutrition_data)
if incomplete:
    print("⚠️  WARNING: Some items missing required fields:", REQUIRED_FIELDS)

# ==================== EMBEDDING MODEL ====================
print("🔄 Loading embedding model...")
embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    token=HF_TOKEN if HF_TOKEN else None
)

# Cache embeddings untuk startup lebih cepat
if os.path.exists(EMB_CACHE_PATH):
    print("📦 Loading cached embeddings...")
    menu_embeddings = np.load(EMB_CACHE_PATH)
else:
    print("🔄 Creating embeddings (first time only)...")
    menu_texts = []
    for item in nutrition_data:
        menu_texts.append(
            f"{item.get('nama_menu','(unknown)')} - {item.get('kategori','?')}: "
            f"Kalori:{item.get('Kalori',0)} Gula:{item.get('Gula',0)} "
            f"Garam:{item.get('Garam',0)} Lemak:{item.get('Lemak',0)}"
        )
    menu_embeddings = embedding_model.encode(menu_texts, normalize_embeddings=True)
    np.save(EMB_CACHE_PATH, menu_embeddings)
    print("💾 Embeddings cached")

print(f"✅ Ready with {len(menu_embeddings)} embeddings\n")

# ==================== CONVERSATION PERSISTENCE ====================
CONVERSATION_FILE = os.path.join(os.path.dirname(__file__), "conversation_cache.json")

def load_conversation_history():
    """Load conversation history dari file"""
    global conversation_history
    if os.path.exists(CONVERSATION_FILE):
        try:
            with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert timestamp strings back to datetime
                for session_id, history in data.items():
                    for item in history:
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                conversation_history = data
                print(f"✅ Loaded {len(conversation_history)} conversation sessions")
        except Exception as e:
            print(f"⚠️  Error loading conversation history: {e}")
            conversation_history = {}
    else:
        conversation_history = {}

def save_conversation_history():
    """Save conversation history ke file"""
    try:
        # Convert datetime to ISO string for JSON serialization
        data = {}
        for session_id, history in conversation_history.items():
            data[session_id] = []
            for item in history:
                data[session_id].append({
                    'user': item['user'],
                    'assistant': item['assistant'],
                    'timestamp': item['timestamp'].isoformat()
                })
        
        with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving conversation history: {e}")

# ==================== CONVERSATION MEMORY ====================
conversation_history: Dict[str, List[dict]] = {}

load_conversation_history()

def cleanup_old_sessions():
    """Remove sessions older than 1 hour"""
    now = datetime.now()
    to_remove = []
    for session_id, history in conversation_history.items():
        if history and (now - history[-1]["timestamp"]) > timedelta(hours=1):
            to_remove.append(session_id)
    for session_id in to_remove:
        del conversation_history[session_id]

def get_conversation_context(session_id: str, max_history: int = 3) -> str:
    """Get last N conversations untuk konteks"""
    if session_id not in conversation_history:
        return ""
    
    history = conversation_history[session_id][-max_history:]
    if not history:
        return ""
    
    context = "\n\nPercakapan sebelumnya:\n"
    for h in history:
        context += f"User: {h['user']}\nAssistant: {h['assistant'][:150]}...\n"
    return context

# ==================== MODELS ====================
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    history: Optional[List[Message]] = None

class ChatResponse(BaseModel):
    response: str
    relevant_items: Optional[List[dict]] = None
    session_id: str

# ==================== HELPER FUNCTIONS ====================

def get_category_emoji(category: str) -> str:
    """Emoji per kategori menu"""
    emojis = {
        "Burger": "🍔",
        "Ayam": "🍗",
        "Breakfast": "🌅",
        "Drinks": "🥤",
        "Desserts": "🍨",
        "Ikan": "🐟",
        "Sides": "🍟"
    }
    return emojis.get(category, "🍽️")

def is_zero_item(itm: dict) -> bool:
    """Check if item has all zero nutrition (like plain water)"""
    return all(float(itm.get(k, 0) or 0) == 0.0 for k in ["Kalori", "Gula", "Garam", "Lemak"])

def retrieve_relevant_items(query: str, top_k: int = 3, threshold: float = 0.25):
    """RAG Retrieval dengan boosting nama menu"""
    q_emb = embedding_model.encode([query], normalize_embeddings=True)
    sims = np.dot(menu_embeddings, q_emb.T).flatten()
    
    # Boost similarity jika nama menu muncul di query
    boosts = np.ones_like(sims)
    query_lower = query.lower()
    for idx, itm in enumerate(nutrition_data):
        name = str(itm.get("nama_menu", "")).lower()
        if name and name in query_lower:
            boosts[idx] = 1.25  # 25% boost
    
    sims = sims * boosts
    
    # Ambil lebih banyak candidates, lalu filter
    top_idx = sims.argsort()[-(top_k * 3):][::-1]
    results = []
    
    for idx in top_idx:
        itm = nutrition_data[idx]
        if sims[idx] >= threshold and not is_zero_item(itm):
            results.append({
                "item": itm,
                "similarity": float(sims[idx])
            })
            if len(results) >= top_k:
                break
    
    return results

def format_items_friendly(items: list) -> str:
    """Format detail nutrisi dengan style friendly"""
    if not items:
        return ""
    
    out = "\n\n📊 **Detail Lengkapnya:**\n"
    for i, data in enumerate(items, 1):
        itm = data["item"]
        emoji = get_category_emoji(itm.get('kategori', ''))
        out += (
            f"\n{emoji} **{itm.get('nama_menu','?')}** ({itm.get('kategori','?')})\n"
            f"   • Kalori: {itm.get('Kalori',0):.1f} kkal\n"
            f"   • Lemak: {itm.get('Lemak',0):.1f}g\n"
            f"   • Gula: {itm.get('Gula',0):.1f}g\n"
            f"   • Garam: {itm.get('Garam',0):.1f}mg\n"
        )
    return out

def health_tips_friendly(items: list) -> str:
    """Health tips dengan tone caring, not preachy"""
    if not items:
        return ""
    
    tips = []
    has_high_value = False
    
    for data in items:
        itm = data["item"]
        kal = itm.get("Kalori", 0)
        gula = itm.get("Gula", 0)
        garam = itm.get("Garam", 0)
        lemak = itm.get("Lemak", 0)
        
        if kal > 600:
            tips.append("💪 Kalori lumayan tinggi nih! Perfect buat setelah olahraga atau hari aktif.")
            has_high_value = True
        if gula > 30:
            tips.append("🍬 Gulanya cukup banyak, mungkin skip minuman manis ya?")
            has_high_value = True
        if garam > 1000:
            tips.append("💧 Garamnya tinggi, jangan lupa minum air putih lebih banyak!")
            has_high_value = True
        if lemak > 25:
            tips.append("🥗 Lemaknya lumayan, seimbangkan dengan sayur atau buah!")
            has_high_value = True
    
    if not has_high_value:
        return "\n\n✨ **Good choice!** Menu ini cukup balanced untuk dinikmati."
    
    # Limit to 3 tips max
    tips = list(set(tips))[:3]
    return "\n\n💡 **Tips Sehat:**\n" + "\n".join(f"   {t}" for t in tips)

def create_fallback(query: str, items: list) -> str:
    """Smart fallback dengan saran"""
    if not items:
        # Kasih saran menu populer random
        popular_items = random.sample(
            [item for item in nutrition_data if not is_zero_item(item)],
            min(3, len(nutrition_data))
        )
        suggestions = ", ".join([item['nama_menu'] for item in popular_items])
        
        return (
            f"🤔 Hmm, saya kurang paham pertanyaan kamu tentang '{query}'.\n\n"
            f"Coba tanya tentang menu spesifik seperti: **{suggestions}**?\n\n"
            f"Atau tanya aja \"Rekomendasi menu sarapan\" atau \"Menu rendah kalori\"!"
        )
    
    first = items[0]["item"]
    emoji = get_category_emoji(first.get('kategori', ''))
    
    return (
        f"{emoji} Berdasarkan pertanyaan kamu, mungkin maksudnya **{first.get('nama_menu','menu')}**?\n\n"
        f"Menu ini punya:\n"
        f"• Kalori: {first.get('Kalori',0):.1f} kkal\n"
        f"• Lemak: {first.get('Lemak',0):.1f}g\n"
        f"• Gula: {first.get('Gula',0):.1f}g\n"
        f"• Garam: {first.get('Garam',0):.1f}mg"
        + format_items_friendly(items)
        + health_tips_friendly(items)
        + "\n\nAda yang mau ditanyakan lagi? 😊"
    )

def generate_response_gemini(query: str, items: list, conv_context: str = "") -> str:
    """Generate response dengan Gemini - Auto-detect user intent & context dari query"""
    if gemini_client is None:
        return create_fallback(query, items)

    # Build context dari retrieved items
    context_lines = []
    total_calories = 0
    total_lemak = 0
    total_gula = 0
    total_garam = 0
    
    for d in items:
        itm = d["item"]
        total_calories += itm.get('Kalori', 0)
        total_lemak += itm.get('Lemak', 0)
        total_gula += itm.get('Gula', 0)
        total_garam += itm.get('Garam', 0)
        
        context_lines.append(
            f"{itm.get('nama_menu','?')} ({itm.get('kategori','?')}): "
            f"Kalori {itm.get('Kalori',0)} kkal, Lemak {itm.get('Lemak',0)} g, "
            f"Gula {itm.get('Gula',0)} g, Garam {itm.get('Garam',0)} mg"
        )
    
    context = "\n".join(context_lines)
    avg_calories = total_calories / len(items) if items else 0

    # Auto-detect user context dari query
    query_lower = query.lower()
    
    # Detect health goals
    user_context_detected = []
    
    if any(word in query_lower for word in ["diet", "turun berat", "kurus", "langsing", "menurunkan"]):
        user_context_detected.append("🎯 Goal: Weight loss / Diet")
    elif any(word in query_lower for word in ["bulking", "nambah berat", "gemuk", "massa otot", "gym"]):
        user_context_detected.append("🎯 Goal: Muscle gain / Bulking")
    elif any(word in query_lower for word in ["sehat", "menjaga", "maintenance", "balance"]):
        user_context_detected.append("🎯 Goal: Healthy maintenance")
    
    # Detect activity level
    if any(word in query_lower for word in ["olahraga", "workout", "gym", "lari", "jogging", "fitness"]):
        user_context_detected.append("💪 Activity: Active/Exercise")
    elif any(word in query_lower for word in ["kantoran", "duduk", "kerja", "sedentary"]):
        user_context_detected.append("🪑 Activity: Sedentary/Office work")
    
    # Detect health conditions
    if any(word in query_lower for word in ["diabetes", "diabetik", "gula darah"]):
        user_context_detected.append("⚠️ Condition: Diabetes concern")
    elif any(word in query_lower for word in ["darah tinggi", "hipertensi", "tekanan darah"]):
        user_context_detected.append("⚠️ Condition: Hypertension concern")
    elif any(word in query_lower for word in ["kolesterol", "lemak darah"]):
        user_context_detected.append("⚠️ Condition: Cholesterol concern")
    
    # Detect meal timing
    if any(word in query_lower for word in ["pagi", "sarapan", "breakfast"]):
        user_context_detected.append("🌅 Timing: Breakfast/Morning")
    elif any(word in query_lower for word in ["siang", "lunch", "makan siang"]):
        user_context_detected.append("☀️ Timing: Lunch/Afternoon")
    elif any(word in query_lower for word in ["malam", "dinner", "makan malam"]):
        user_context_detected.append("🌙 Timing: Dinner/Evening")
    
    # Detect preferences
    if any(word in query_lower for word in ["rendah kalori", "low cal", "sedikit kalori"]):
        user_context_detected.append("📉 Preference: Low calorie")
    elif any(word in query_lower for word in ["rendah gula", "no sugar", "tanpa gula"]):
        user_context_detected.append("🍬 Preference: Low sugar")
    elif any(word in query_lower for word in ["rendah garam", "low sodium", "sedikit garam"]):
        user_context_detected.append("🧂 Preference: Low sodium")
    elif any(word in query_lower for word in ["rendah lemak", "low fat", "sedikit lemak"]):
        user_context_detected.append("🥑 Preference: Low fat")
    
    # Build context summary
    context_summary = ""
    if user_context_detected:
        context_summary = f"\n**Konteks User yang Terdeteksi dari Query:**\n" + "\n".join([f"• {ctx}" for ctx in user_context_detected])

    # Random personality untuk variasi
    personalities = [
        "Kamu lagi ceria dan suka kasih fun fact nutrisi yang menarik",
        "Kamu lagi fokus health-conscious tapi tetap realistis dan tidak menggurui",
        "Kamu lagi casual banget, bicara kayak temen yang peduli kesehatan",
        "Kamu lagi profesional tapi tetap friendly dan approachable",
        "Kamu lagi excited banget kasih tips kesehatan yang actionable"
    ]
    personality = random.choice(personalities)

    # REFINED PROMPT dengan auto-detection
    prompt = f"""Kamu adalah **Dr. Ronald**, ahli nutrisi bersertifikat yang bekerja untuk McDonald's Indonesia.

**Identitas & Expertise:**
- Sarjana Gizi & Dietetik dengan 10+ tahun pengalaman
- Spesialis dalam meal planning, portion control, dan lifestyle nutrition
- Ahli dalam menyeimbangkan fast food dengan pola hidup sehat
- Berbicara dengan bahasa Indonesia yang ramah, tidak menggurui, dan praktis

**Mood hari ini:** {personality}

**Data Menu McDonald's (AKURAT & LENGKAP):**
{context}

**Ringkasan Nutrisi Total:**
- Total Kalori: {total_calories:.1f} kkal (Rata-rata: {avg_calories:.1f} kkal/item)
- Total Lemak: {total_lemak:.1f}g ({(total_lemak/70)*100:.0f}% kebutuhan harian)
- Total Gula: {total_gula:.1f}g ({(total_gula/50)*100:.0f}% batas WHO)
- Total Garam: {total_garam:.1f}mg ({(total_garam/2000)*100:.0f}% batas harian)

{context_summary}

{conv_context}

**Pertanyaan Customer:** {query}

**INSTRUKSI PENTING:**

1️⃣ **PAHAMI KONTEKS USER:**
   - Baca konteks yang terdeteksi di atas
   - Sesuaikan jawaban dengan goal/kondisi/preferensi mereka
   - Jika user mention aktivitas/kondisi kesehatan, PRIORITASKAN dalam rekomendasi
   - Jika tidak ada konteks khusus, berikan advice umum yang balanced

2️⃣ **ANALISIS NUTRISI (Sesuai Data yang Ada):**
   - Breakdown kalori, lemak, gula, dan garam (HANYA DATA INI)
   - Bandingkan dengan kebutuhan harian standar
   - Identifikasi kelebihan/kekurangan nutrisi
   - JANGAN sebutkan Protein/Karbohidrat (tidak ada datanya)

3️⃣ **REKOMENDASI PERSONAL:**
   - Sesuaikan dengan konteks user yang terdeteksi
   - Jika user diet: fokus ke kalori & lemak, kasih alternatif lebih ringan
   - Jika user bulking: fokus ke kalori & energi, suggest pairing protein
   - Jika user diabetes: fokus ke gula, warning & alternatives
   - Jika user hipertensi: fokus ke garam, warning & tips reduce sodium
   - Jika user workout: suggest timing & pairing dengan protein
   - Jika user kantoran: suggest portion control & balance meal

4️⃣ **MEAL TIMING & PAIRING:**
   - Sesuaikan dengan waktu makan yang disebutkan user
   - Sarapan: fokus energi pagi & sustained energy
   - Siang: main meal, kombinasi seimbang
   - Malam: warning jika high calorie, suggest lighter options
   - Suggest kombinasi menu untuk balanced meal

5️⃣ **ACTIONABLE TIPS (3 TIPS SPESIFIK):**
   - Modifikasi pesanan untuk lebih sehat (no mayo, less sugar, etc)
   - Aktivitas fisik equivalent (berapa menit jalan/jogging untuk burn kalori)
   - Meal timing optimal & frekuensi aman per minggu
   - Pairing dengan makanan lain (sayur/buah/protein)

**KETERBATASAN DATA:**
- Data HANYA: Kalori, Lemak, Gula, Garam
- JANGAN sebutkan Protein/Karbohidrat
- Jika ditanya: "Maaf, data protein/karbo belum tersedia. Tapi berdasarkan kalori & lemak, saya bisa estimasi bahwa..."

**FORMAT JAWABAN:**

**Struktur Ideal (pilih yang relevan):**
1. **Opening (1-2 kalimat):** Langsung jawab pertanyaan + highlight utama
2. **Analisis Personal (jika ada konteks):** Sesuaikan dengan goal/kondisi user
3. **Breakdown Nutrisi:** Quick summary dengan emoji status (🟢🟡🔴)
4. **Rekomendasi Praktis:** 2-3 bullet points actionable
5. **Tips Modifikasi (jika perlu):** Cara bikin lebih sehat
6. **Exercise Equivalent (jika high cal):** Berapa menit aktivitas untuk burn
7. **Closing:** Pertanyaan follow-up untuk engagement

**Style Guidelines:**
- Mulai dengan emoji yang relevan (🍔🥗💪🏃‍♂️)
- Gunakan **bold** untuk highlight penting
- Bullet points untuk readability
- Status emoji: 🟢 Rendah/Baik, 🟡 Sedang/Perhatian, 🔴 Tinggi/Warning
- Maksimal 5 paragraf singkat (kecuali user minta detail lengkap)
- Tone friendly, bukan menggurui
- Fokus pada "bagaimana tetap sehat sambil enjoy McDonald's"

**Contoh Opening yang Baik:**
✅ "Big Mac (528 kkal) cocok buat kamu yang aktif, tapi garamnya 877mg—hampir setengah batas harian! 💧"
✅ "Untuk diet, McChicken (400 kkal) lebih aman dari Big Mac. Lemaknya juga 30% lebih rendah 🎯"
✅ "Menu ini oke buat sarapan energi tinggi, tapi imbangi dengan sayur di siang/malam ya! 🌅"

**Contoh Opening yang Buruk:**
❌ "Berdasarkan data yang tersedia..."
❌ "Menu ini mengandung..."
❌ "Saya akan menjelaskan..."

**PENTING:**
- Jika user tanya hal di luar nutrisi/menu, arahkan kembali ke topik
- Jika data tidak lengkap, akui dengan jujur
- Disclaimer: Ini bukan pengganti konsultasi medis profesional

**Mulai jawaban sekarang (langsung, tanpa prefix "Jawaban:" atau "Dr. Ronald:"):**"""

    try:
        resp = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.78,
                "top_p": 0.88,
                "top_k": 45,
                "max_output_tokens": 450,
                "stop_sequences": ["\n\n\n\n"],
            },
        )
        
        text = (getattr(resp, "text", "") or "").strip()
        
        # Clean up
        text = text.replace("Jawaban:", "").replace("Dr. Ronald:", "").replace("**Jawaban:**", "").strip()
        
        if len(text) < 30:
            return create_fallback(query, items)
        
        # Enhanced formatting
        query_lower = query.lower()
        wants_details = any(keyword in query_lower for keyword in [
            "detail", "lengkap", "analisis", "breakdown", "kandungan", 
            "porsi", "sehat", "diet", "olahraga", "rekomendasi", "bandingkan",
            "vs", "perbandingan", "semua", "info lengkap", "compare"
        ])
        
        if wants_details:
            text += format_nutrition_analysis(items)
            text += format_portion_guide(items)
            text += health_tips_advanced(items)
        else:
            text += health_tips_friendly(items)
        
        return text
        
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return create_fallback(query, items)

# ==================== API ENDPOINTS ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chat endpoint dengan conversation memory"""
    
    cleanup_old_sessions()
    
    q = req.message.strip()
    session_id = req.session_id or "default"
    
    if len(q) < 2:
        return ChatResponse(
            response="🤔 Pertanyaan terlalu pendek nih. Coba jelaskan lebih detail ya!",
            relevant_items=[],
            session_id=session_id
        )
    
    items = retrieve_relevant_items(q, top_k=3, threshold=0.25)
    
    if not items:
        popular = random.sample(
            [item for item in nutrition_data if not is_zero_item(item)],
            min(3, len(nutrition_data))
        )
        suggestions = ", ".join([item['nama_menu'] for item in popular])
        
        return ChatResponse(
            response=(
                f"🤔 Hmm, saya kurang nemu menu yang cocok dengan '{q}'.\n\n"
                f"Coba tanya tentang: **{suggestions}**?\n\n"
                f"Atau tanya \"Menu rendah kalori\" atau \"Rekomendasi sarapan\"!"
            ),
            relevant_items=[],
            session_id=session_id
        )
    
    conv_context = get_conversation_context(session_id, max_history=3)
    answer = generate_response_gemini(q, items, conv_context)
    
    # Save to history
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    conversation_history[session_id].append({
        "user": q,
        "assistant": answer,
        "timestamp": datetime.now()
    })
    
    if len(conversation_history[session_id]) > 10:
        conversation_history[session_id] = conversation_history[session_id][-10:]
    
    # ✅ AUTO-SAVE setelah setiap conversation
    save_conversation_history()
    
    return ChatResponse(
        response=answer,
        relevant_items=[i["item"] for i in items],
        session_id=session_id
    )
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "items_loaded": len(nutrition_data),
        "embeddings_cached": os.path.exists(EMB_CACHE_PATH),
        "gemini_configured": bool(GOOGLE_API_KEY),
        "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
        "active_sessions": len(conversation_history),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/popular-menus")
async def get_popular_menus(limit: int = 5):
    """Get random popular menus"""
    valid_items = [item for item in nutrition_data if not is_zero_item(item)]
    popular = random.sample(valid_items, min(limit, len(valid_items)))
    return {"menus": popular}

@app.post("/api/clear-session")
async def clear_session(session_id: str = "default"):
    """Clear conversation history untuk session tertentu"""
    if session_id in conversation_history:
        del conversation_history[session_id]
        return {"message": f"Session {session_id} cleared"}
    return {"message": "Session not found"}

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🍔 McDonald's Nutrition Chatbot API v2.0")
    print("="*60)
    print(f"✅ Loaded {len(nutrition_data)} menu items")
    print(f"✅ Embedding model ready")
    print(f"✅ Gemini client: {'Configured' if gemini_client else 'Not configured'}")
    print(f"✅ Server ready at http://localhost:8000")
    print(f"✅ Health check: http://localhost:8000/api/health")
    print("="*60 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )