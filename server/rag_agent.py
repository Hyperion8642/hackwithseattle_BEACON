import asyncio
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from rocketride import RocketRideClient
from rocketride.schema import Question

load_dotenv()


def _sync_rocketride_port() -> None:
    """Detect the running RocketRide engine port and patch ROCKETRIDE_URI."""
    try:
        out = subprocess.check_output(["lsof", "-i", "-P", "-n"], text=True)
    except Exception:
        return
    for line in out.splitlines():
        if "engine" in line and "LISTEN" in line and "127.0.0.1" in line:
            m = re.search(r"127\.0\.0\.1:(\d+)", line)
            if m:
                port = m.group(1)
                os.environ["ROCKETRIDE_URI"] = f"http://localhost:{port}"
                env_path = Path(__file__).parent.parent / ".env"
                if env_path.exists():
                    text = env_path.read_text()
                    updated = re.sub(
                        r"^(ROCKETRIDE_URI=http://localhost:)\d+",
                        rf"\g<1>{port}",
                        text,
                        flags=re.MULTILINE,
                    )
                    if updated != text:
                        env_path.write_text(updated)
                return


_sync_rocketride_port()

minimax = OpenAI(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.io/v1",
)

_executor = ThreadPoolExecutor(max_workers=1)
_client: RocketRideClient | None = None
_token: str | None = None

app = FastAPI(title="RAG Agent")


class RAGRequest(BaseModel):
    question: str


class RAGResponse(BaseModel):
    answer: str


async def get_rag_client():
    global _client, _token
    if _client is None:
        _client = RocketRideClient()
        await _client.connect()
        result = await _client.use(filepath="pipelines/rag_search.pipe", use_existing=True)
        _token = result["token"]
    return _client, _token


def build_context(documents: list) -> str:
    chunks = []
    for doc in documents:
        if isinstance(doc, str):
            chunks.append(doc)
        elif isinstance(doc, dict):
            chunks.append(doc.get("text") or doc.get("content") or str(doc))
    return "\n\n---\n\n".join(chunks)


def extract_answer(full_response: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL)
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
    return cleaned.strip()


async def ask_rag(question: str) -> str:
    client, token = await get_rag_client()
    q = Question()
    q.addQuestion(question)
    response = await client.chat(token=token, question=q)

    documents = response.get("documents", [])
    if not documents:
        return "I do not have that info stored. Please contact your coordinator for assistance."

    context = build_context(documents)
    completion = minimax.chat.completions.create(
        model="MiniMax-M2.7",
        max_tokens=1500,
        temperature=0.0,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are a transit operations assistant replying via iMessage. "
                    f"Do NOT use ** around section titles or headers. Only use **word** around individual important words or terms inline within a sentence.\n\n"
                    f"Use the manual sections below to answer the driver's question. "
                    f"Include directly relevant information AND any related information that could be useful.\n\n"
                    f"If the manual context contains nothing relevant or related to the question, "
                    f"reply exactly: 'I do not know, please contact admin.'\n\n"
                    f"Determine the question type and use the matching format:\n\n"
                    f"IF the question is about a problem, incident, or emergency, use:\n"
                    f"🔧 Possible Fixes:\n"
                    f"- List 2-4 concise actionable steps. Do NOT cite section numbers here.\n"
                    f"- Include related procedures or precautions.\n\n"
                    f"❓ Why This Happened: (only for mechanical/technical/operational issues — skip entirely for people-related incidents like assault, misconduct, medical)\n"
                    f"- 1-2 sentences on the likely cause.\n\n"
                    f"IF the question is factual or informational (e.g. what is X, where is X, how does X work, what are the boundaries of X), use:\n"
                    f"ℹ️ Answer:\n"
                    f"- Answer the question directly and completely using the manual context. Do not say 'this is a factual question'.\n\n"
                    f"ALWAYS include these two sections at the end:\n\n"
                    f"📞 Contacts:\n"
                    f"- List any phone numbers, emails, or named contacts from the manual relevant to this situation.\n"
                    f"- Omit this section entirely if no contact info exists in the context.\n\n"
                    f"📖 Source:\n"
                    f"- List the section numbers and titles the answer was drawn from.\n\n"
                    f"End with exactly this line: 'Do you need any other information?'\n\n"
                    f"Manual context:\n{context}\n\nDriver question: {question}"
                ),
            },
        ],
    )
    return extract_answer(completion.choices[0].message.content)


@app.post("/rag", response_model=RAGResponse)
async def rag_endpoint(req: RAGRequest) -> RAGResponse:
    full_response = await ask_rag(req.question)
    answer = extract_answer(full_response)
    return RAGResponse(answer=answer)


async def async_input(prompt: str = "") -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, input, prompt)


async def cli() -> None:
    print("RAG Agent ready — searching in The Book. Type 'quit' to exit.\n")
    while True:
        user_input = await async_input("You: ")
        if user_input.strip().lower() in ("quit", "exit", "q"):
            break

        full_response = await ask_rag(user_input)
        answer = extract_answer(full_response)
        print(f"\nBot: {full_response}")
        print(f"\n[iMessage reply]: {answer}\n")


if __name__ == "__main__":
    asyncio.run(cli())
