import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from agent1.config import QDRANT_URL, QDRANT_LOCAL_PATH, QDRANT_COLLECTION, EMBEDDING_MODEL, CATEGORY_TO_TOOL, FEW_SHOT_EXAMPLES, CATEGORIES
from agent1.tools import TOOLS
from agent1.legal import apply_legal_compliance

app = FastAPI(title="Agent 1: The Protocol Specialist")

def get_qdrant_client():
    """Create Qdrant client: local file mode by default, server mode if QDRANT_URL is set."""
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL)
    return QdrantClient(path=QDRANT_LOCAL_PATH)

def _get_minimax_client():
    """Create a fresh MiniMax client each call — safe for concurrent use."""
    return OpenAI(
        api_key=os.getenv("MINIMAX_API_KEY", ""),
        base_url="https://api.minimax.io/v1"
    )

# Lazy singletons — initialized on first use
_embedding_model = None

def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model

class QueryRequest(BaseModel):
    driver_text: str
    gps: str = "Unknown GPS"
    operator_id: str = "Unknown Operator"
    coach_id: str = "Unknown Coach"

class Agent1Response(BaseModel):
    incident_category: str
    tool_executed: dict
    legal_reminders: list
    protocol_context: list

def search_protocol(query_text: str, top_k: int = 3):
    """Vector search across The Book. Creates a fresh Qdrant client per call."""
    model = _get_embedding_model()
    vector = model.encode(query_text).tolist()
    client = get_qdrant_client()
    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=top_k
    )
    return [hit.payload["text"] for hit in results.points]

def classify_incident(driver_text: str, context: list) -> str:
    """Uses MiniMax to classify the incident based on driver text and retrieved context."""
    context_str = "\n".join(context)
    
    prompt = f"""You are the Protocol Specialist for Metro Transit.
Classify the driver's incident into one of the following categories: {', '.join(CATEGORIES)}.

Rules:
1. Use the provided Rulebook Context to ground your decision.
2. Consider panic-induced variance.
3. Output ONLY the exact category name.

{FEW_SHOT_EXAMPLES}

Rulebook Context:
{context_str}

Driver Input: "{driver_text}"
Category:"""

    response = _get_minimax_client().chat.completions.create(
        model="MiniMax-M2.7",
        max_tokens=20,
        temperature=0.0,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    category = response.choices[0].message.content.strip()
    
    # Fallback to mechanical_failure if hallucinated
    if category not in CATEGORIES:
        category = "mechanical_failure"
    return category

def route_to_tool(category: str, request: QueryRequest):
    """Executes the mapped tool for the given category."""
    tool_name = CATEGORY_TO_TOOL.get(category)
    tool_func = TOOLS.get(tool_name)
    
    if not tool_func:
        return {"error": "Tool not found"}

    # Very naive routing of arguments for demonstration
    if tool_name == "call_emergency_services":
        res = tool_func(request.gps, request.driver_text)
    elif tool_name == "page_field_supervisor":
        res = tool_func("Intersection near " + request.gps, request.operator_id)
    elif tool_name == "trigger_regulatory_hold":
        res = tool_func(request.coach_id, f"Ref for {category}")
    else:
        res = None
        
    return res.__dict__ if res else {}

@app.post("/query", response_model=Agent1Response)
def process_query(request: QueryRequest):
    if not os.getenv("MINIMAX_API_KEY"):
        raise HTTPException(status_code=500, detail="MINIMAX_API_KEY not set")
        
    # 1. Search Vector DB
    try:
        context_chunks = search_protocol(request.driver_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant Search Error: {e}")

    # 2. Classify (LLM rerank/confirm)
    category = classify_incident(request.driver_text, context_chunks)
    
    # 3. Route to Action Tool
    tool_result = route_to_tool(category, request)
    
    # 4. Inject Legal Compliance
    reminders = apply_legal_compliance(category, request.operator_id)
    
    return Agent1Response(
        incident_category=category,
        tool_executed=tool_result,
        legal_reminders=reminders,
        protocol_context=context_chunks
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
