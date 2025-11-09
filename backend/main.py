from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="McDonald's Nutrition Chatbot API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Hugging Face token from environment
HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

if HF_TOKEN:
    print("✅ Hugging Face token loaded successfully")
else:
    print("⚠️ No Hugging Face token found. Using public models only.")

# Load data
DATA_PATH = os.path.join(os.path.dirname(__file__), "knowledge_json", "mcd_nutrition_cleaned.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    nutrition_data = json.load(f)

# Initialize models with token
print("Loading embedding model...")
embedding_model = SentenceTransformer(
    'sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
    use_auth_token=HF_TOKEN if HF_TOKEN else None
)

print("Loading LLM model for Indonesian...")
# Model bahasa Indonesia dari Hugging Face - IndoNLG (mT5 fine-tuned untuk Indonesia)
model_name = "Wikidepia/IndoT5-base"
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    use_auth_token=HF_TOKEN if HF_TOKEN else None
)
llm_model = AutoModelForSeq2SeqLM.from_pretrained(
    model_name,
    use_auth_token=HF_TOKEN if HF_TOKEN else None
)

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "cpu"
llm_model = llm_model.to(device)
print(f"Model loaded on {device}")

# Create embeddings for all menu items
print("Creating embeddings for menu items...")
menu_texts = []
for item in nutrition_data:
    text = f"{item['nama_menu']} - {item['kategori']}: Kalori: {item['Kalori']}, Gula: {item['Gula']}g, Garam: {item['Garam']}mg, Lemak: {item['Lemak']}g"
    menu_texts.append(text)

menu_embeddings = embedding_model.encode(menu_texts)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    relevant_items: Optional[list] = None

def retrieve_relevant_items(query: str, top_k: int = 3):
    """RAG - Retrieve relevant menu items based on query"""
    query_embedding = embedding_model.encode([query])
    
    # Calculate cosine similarity
    similarities = np.dot(menu_embeddings, query_embedding.T).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    relevant_items = []
    for idx in top_indices:
        if similarities[idx] > 0.3:  # threshold
            relevant_items.append({
                "item": nutrition_data[idx],
                "similarity": float(similarities[idx])
            })
    
    return relevant_items

def generate_response(query: str, context_items: list) -> str:
    """Generate response using LLM with context"""
    
    # Build context from retrieved items
    context = "Informasi menu McDonald's yang relevan:\n\n"
    for item_data in context_items:
        item = item_data["item"]
        context += f"- {item['nama_menu']} ({item['kategori']})\n"
        context += f"  Kalori: {item['Kalori']} kkal\n"
        context += f"  Gula: {item['Gula']} gram\n"
        context += f"  Garam: {item['Garam']} mg\n"
        context += f"  Lemak: {item['Lemak']} gram\n\n"
    
    # Create prompt for Indonesian model
    prompt = f"""Berdasarkan informasi berikut, jawab pertanyaan dengan ramah dan informatif.

{context}

Pertanyaan: {query}

Jawaban:"""
    
    # Generate response
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True).to(device)
    
    with torch.no_grad():
        outputs = llm_model.generate(
            **inputs,
            max_length=256,
            num_beams=4,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.2
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # If response is too short or generic, create a structured response
    if len(response.strip()) < 20 or not response.strip():
        response = create_structured_response(query, context_items)
    
    return response

def create_structured_response(query: str, context_items: list) -> str:
    """Create a structured response when LLM fails"""
    if not context_items:
        return "Maaf, saya tidak menemukan informasi menu yang sesuai dengan pertanyaan Anda. Bisakah Anda mencoba dengan nama menu yang lebih spesifik?"
    
    response = "Berikut informasi nutrisi yang Anda tanyakan:\n\n"
    
    for item_data in context_items:
        item = item_data["item"]
        response += f"📍 **{item['nama_menu']}** ({item['kategori']})\n"
        response += f"   • Kalori: {item['Kalori']} kkal\n"
        response += f"   • Gula: {item['Gula']} gram\n"
        response += f"   • Garam: {item['Garam']} mg\n"
        response += f"   • Lemak: {item['Lemak']} gram\n\n"
    
    # Add health tips based on nutritional content
    high_cal_items = [i for i in context_items if i["item"]["Kalori"] > 500]
    if high_cal_items:
        response += "\n💡 Tips: Menu ini memiliki kalori yang cukup tinggi. Seimbangkan dengan aktivitas fisik ya!"
    
    return response

@app.get("/")
def read_root():
    return {
        "message": "McDonald's Nutrition Chatbot API",
        "status": "running",
        "model": "IndoT5-base (Indonesian Language Model)",
        "embedding": "paraphrase-multilingual-mpnet-base-v2",
        "token_status": "authenticated" if HF_TOKEN else "public_only"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        query = request.message
        
        # Retrieve relevant items using RAG
        relevant_items = retrieve_relevant_items(query, top_k=3)
        
        if not relevant_items:
            return ChatResponse(
                response="Maaf, saya tidak menemukan informasi menu yang sesuai. Coba tanyakan tentang menu seperti Big Mac, McSpicy, Chicken McNuggets, atau menu lainnya.",
                relevant_items=[]
            )
        
        # Generate response using LLM
        response_text = generate_response(query, relevant_items)
        
        return ChatResponse(
            response=response_text,
            relevant_items=[item["item"] for item in relevant_items]
        )
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu")
def get_all_menu():
    """Get all menu items"""
    return {"items": nutrition_data, "total": len(nutrition_data)}

@app.get("/api/menu/category/{category}")
def get_menu_by_category(category: str):
    """Get menu items by category"""
    items = [item for item in nutrition_data if item["kategori"].lower() == category.lower()]
    return {"items": items, "total": len(items)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)