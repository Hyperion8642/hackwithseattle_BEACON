import streamlit as st
import os
import requests
from dotenv import load_dotenv
from agent1.main_agent import process_query, QueryRequest

load_dotenv(".env")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BEACON Emergency Response",
    layout="wide",
    page_icon="🚨",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 50%, #16213e 100%); }

.title-block {
    background: linear-gradient(90deg, #e63946, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.6rem; font-weight: 700; margin-bottom: 0;
}

.subtitle { color: #8892b0; font-size: 1rem; margin-top: 0; }

.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.category-badge {
    display: inline-block;
    background: linear-gradient(90deg, #e63946, #ff6b35);
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    padding: 4px 14px;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.tool-box {
    background: rgba(0, 200, 150, 0.1);
    border-left: 4px solid #00c896;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #e0e0e0;
}

.legal-box {
    background: rgba(255, 180, 0, 0.1);
    border-left: 4px solid #ffb400;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #e0e0e0;
}

.context-box {
    background: rgba(100, 100, 255, 0.07);
    border-left: 4px solid #6464ff;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: #ccd6f6;
}

.pipeline-step {
    display: flex; align-items: center; gap: 10px;
    padding: 6px 0; color: #8892b0; font-size: 0.85rem;
}

.pipeline-step.active { color: #00c896; font-weight: 600; }

.voice-label {
    color: #ccd6f6; font-size: 0.9rem; margin-bottom: 6px;
    font-weight: 600;
}

.transcript-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 0.75rem;
    color: #e0e0e0;
    font-style: italic;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="title-block">🚨 BEACON</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">King County Metro — Emergency Agent Dashboard · Agent 1: Protocol Specialist</p>', unsafe_allow_html=True)
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Operator Settings")
    operator_id = st.text_input("Operator ID", "OP-1234")
    coach_id    = st.text_input("Coach ID",    "COACH-999")
    gps         = st.text_input("GPS / Intersection", "3rd and Pike, Seattle")
    st.divider()

    st.markdown("### 🔀 Pipeline")
    for step, label in [("①", "Spectrum Gateway (iMessage)"),
                        ("②", "RocketRide /dispatch"),
                        ("③", "Agent 1 — Vector Search"),
                        ("④", "MiniMax LLM Classify"),
                        ("⑤", "Legal Compliance Check"),
                        ("⑥", "Response to Driver")]:
        st.markdown(f'<div class="pipeline-step">{step} {label}</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📡 RocketRide Status")
    try:
        r = requests.get("http://localhost:5565/docs", timeout=1)
        st.success("✅ RocketRide Online (port 5565)")
    except Exception:
        st.warning("⚠️ RocketRide Offline\n\nRun: `python rocketride/main.py`")

# ── Main columns ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 🎙️ Driver Input")

    input_mode = st.radio("Input mode", ["🎤 Voice", "⌨️ Text"], horizontal=True, label_visibility="collapsed")
    driver_text = ""

    if "🎤 Voice" in input_mode:
        st.markdown('<p class="voice-label">Click the mic, speak your report, then click again to stop:</p>', unsafe_allow_html=True)

        # Use browser's free Web Speech API — no API key needed
        voice_html = """
        <div style="text-align:center; margin: 10px 0;">
          <button id="micBtn" onclick="toggleRecording()" style="
            background: linear-gradient(90deg,#e63946,#ff6b35);
            border:none; border-radius:50px; padding:14px 32px;
            color:white; font-size:1rem; font-weight:700; cursor:pointer;
            box-shadow: 0 4px 20px rgba(230,57,70,0.4);">
            🎙️ Start Speaking
          </button>
          <p id="status" style="color:#8892b0; margin-top:8px; font-size:0.85rem;">Ready</p>
          <div id="result" style="
            background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1);
            border-radius:8px; padding:10px; margin-top:10px;
            color:#e0e0e0; font-style:italic; min-height:40px; font-size:0.9rem;">
            Your transcript will appear here…
          </div>
          <button onclick="sendToStreamlit()" style="
            margin-top:10px; background:#00c896; border:none;
            border-radius:8px; padding:10px 24px;
            color:white; font-weight:700; cursor:pointer;">
            ✅ Use this transcript
          </button>
        </div>

        <script>
          const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
          const rec = new SpeechRecognition();
          rec.continuous = true;
          rec.interimResults = true;
          rec.lang = 'en-US';
          let recording = false;
          let finalTranscript = '';

          function toggleRecording() {
            if (!recording) {
              finalTranscript = '';
              rec.start();
              recording = true;
              document.getElementById('micBtn').textContent = '🛑 Stop Recording';
              document.getElementById('micBtn').style.background = '#333';
              document.getElementById('status').textContent = '🔴 Recording…';
            } else {
              rec.stop();
              recording = false;
              document.getElementById('micBtn').textContent = '🎙️ Start Speaking';
              document.getElementById('micBtn').style.background = 'linear-gradient(90deg,#e63946,#ff6b35)';
              document.getElementById('status').textContent = 'Done. Click "Use this transcript" to send.';
            }
          }

          rec.onresult = function(event) {
            let interim = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
              if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript + ' ';
              else interim += event.results[i][0].transcript;
            }
            document.getElementById('result').textContent = finalTranscript + interim;
          };

          rec.onerror = function(e) {
            document.getElementById('status').textContent = 'Error: ' + e.error;
          };

          function sendToStreamlit() {
            const text = document.getElementById('result').textContent;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
          }
        </script>
        """
        transcript_from_voice = st.components.v1.html(voice_html, height=280)
        
        if transcript_from_voice and str(transcript_from_voice).strip():
            driver_text = str(transcript_from_voice).strip()
            st.markdown(f'<div class="transcript-box">🎙️ "{driver_text}"</div>', unsafe_allow_html=True)
        else:
            driver_text = st.text_input("Or paste transcript manually:", placeholder="Your spoken words will appear here after recording…")

    else:
        driver_text = st.text_area(
            "Type your emergency report:",
            height=120,
            placeholder="e.g. Green fluid is spraying everywhere, smells sweet..."
        )

    submit = st.button("🚀 Transmit to BEACON", type="primary", use_container_width=True)

# ── Processing ────────────────────────────────────────────────────────────────
if submit and driver_text:
    with col2:
        st.markdown("### ⚡ Agent 1 Response")

        with st.spinner("Routing through RocketRide → Agent 1 (MiniMax)…"):
            try:
                import asyncio
                from rocketride import RocketRideClient
                from rocketride.schema import Question
                
                async def run_rocketride(text, loc, op_id):
                    async with RocketRideClient() as client:
                        # Ensure we connect first
                        await client.connect()
                        res = await client.use(filepath='pipelines/beacon_dispatch.pipe')
                        tok = res['token']
                        q = Question(expectJson=True)
                        q.addQuestion(f"DRIVER REPORT: {text} | LOC: {loc} | OP: {op_id}")
                        rr_response = await client.chat(token=tok, question=q)
                        if 'answers' in rr_response and len(rr_response['answers']) > 0:
                            return rr_response['answers'][0]
                        return {}

                final_plan = asyncio.run(run_rocketride(driver_text, gps, operator_id))

                # ── Display ──
                incident_cat = final_plan.get("incident_category", "UNKNOWN_CATEGORY").replace("_", " ").upper()
                st.markdown(f'<div class="category-badge">🚨 {incident_cat}</div>', unsafe_allow_html=True)

                st.markdown(
                    f'<div class="tool-box">🛠 <strong>BEACON Protocol</strong><br>{final_plan.get("summary", "Protocol Executed.")}</div>',
                    unsafe_allow_html=True
                )

                if final_plan.get("legal_reminders"):
                    legal_html = "".join(f"<li>{r}</li>" for r in final_plan.get("legal_reminders", []))
                    st.markdown(
                        f'<div class="legal-box">⚖️ <strong>Legal Mandates</strong><ul>{legal_html}</ul></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown('<div class="legal-box">✅ No legal mandates for this category.</div>', unsafe_allow_html=True)
                    
                st.markdown("**📚 Retrieved Protocol Context (The Book)**")
                st.markdown('<div class="context-box"><strong>Handled dynamically by RocketRide Engine via Qdrant Nodes</strong></div>', unsafe_allow_html=True)

                # ── TTS: speak the steps back ─────────────────────────────────
                steps = final_plan.get("immediateSteps", ["Await field supervisor.", "Engage parking brake."])
                tts_text = f"Protocol active. Category: {incident_cat}. {'. '.join(steps)}"
                st.markdown("**🔊 Voice Response**")
                st.components.v1.html(f"""
                <script>
                    const msg = new SpeechSynthesisUtterance("{tts_text}");
                    msg.rate = 0.95;
                    msg.pitch = 1.0;
                    window.speechSynthesis.speak(msg);
                </script>
                <p style="color:#8892b0; font-size:0.8rem;">🔊 Speaking protocol steps aloud…</p>
                """, height=40)

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach RocketRide at http://localhost:5565\n\nRun: `python rocketride/main.py`")
            except Exception as e:
                st.error(f"Error: {e}")

elif submit and not driver_text:
    with col2:
        st.warning("No input detected. Please record audio or type a message first.")
