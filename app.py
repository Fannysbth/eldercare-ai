import streamlit as st
import os
import base64
import json
from datetime import datetime
from cognitive_analyzer import CognitiveAnalyzer
from session_manager import SessionManager

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ElderCare AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load secrets into env ──────────────────────────────────────────────────────
for key in ["ANTHROPIC_API_KEY", "GROQ_API_KEY"]:
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] { background: #f5f0eb !important; font-family: 'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] > .main { background: #f5f0eb; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="block-container"] { padding: 2rem 3rem 4rem; max-width: 1200px; }

.ec-header { display:flex; align-items:center; gap:1.5rem; border-bottom:2px solid #d4c9bc; margin-bottom:2.5rem; }
.ec-logo { font-size:3rem; line-height:1; }
.ec-title { font-family:'DM Serif Display',serif; font-size:2.4rem; color:#2c1810; line-height:1.1; }
.ec-subtitle { font-size:0.95rem; color:#7a6858; margin-top:0.3rem; letter-spacing:0.02em; }
.ec-badge { margin-left:auto; background:#e8dfd4; border:1px solid #c9b99a; color:#6b5744; font-size:0.78rem; font-weight:500; padding:0.35rem 0.85rem; border-radius:20px; white-space:nowrap; }

[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:0; background:#ece5dc; border-radius:12px; padding:4px; border:1px solid #d4c9bc; }
[data-testid="stTabs"] [data-baseweb="tab"] { background:transparent; border-radius:9px; padding:0.6rem 1.4rem; font-family:'DM Sans',sans-serif; font-weight:500; font-size:0.9rem; color:#8a7566; border:none; transition:all 0.2s; }
[data-testid="stTabs"] [aria-selected="true"] { background:#fff !important; color:#2c1810 !important; box-shadow:0 1px 4px rgba(44,24,16,0.12) !important; }
[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding:0; margin-top:1.5rem; }

.ec-card { background:#fff; border:1px solid #ddd4c8; border-radius:16px; padding:1.5rem; margin-bottom:1rem; box-shadow:0 2px 8px rgba(44,24,16,0.05); }
.ec-card-title { font-family:'DM Serif Display',serif; font-size:1.1rem; color:#2c1810; margin-bottom:0.6rem; }
.ec-card-meta { font-size:0.82rem; color:#a09080; margin-bottom:1rem; }

.chat-wrap { display:flex; flex-direction:column; gap:1rem; padding:0.5rem 0; }
.bubble-row { display:flex; align-items:flex-end; gap:0.7rem; }
.bubble-row.user { flex-direction:row-reverse; }
.bubble-avatar { width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1rem; flex-shrink:0; }
.avatar-ai { background:#e8dfd4; }
.avatar-user { background:#2c1810; }
.bubble { max-width:72%; padding:0.9rem 1.2rem; border-radius:18px; font-size:0.92rem; line-height:1.6; }
.bubble-ai { background:#ece5dc; color:#2c1810; border-bottom-left-radius:4px; }
.bubble-user { background:#2c1810; color:#f5f0eb; border-bottom-right-radius:4px; }

.score-ring-wrap { text-align:center; padding:1.5rem 0; }
.score-label { font-family:'DM Serif Display',serif; font-size:1rem; color:#7a6858; margin-top:0.7rem; }
.risk-badge { display:inline-block; padding:0.45rem 1.1rem; border-radius:20px; font-weight:600; font-size:0.88rem; letter-spacing:0.03em; }
.risk-low { background:#d4edda; color:#1c5e2a; border:1px solid #a8d5b5; }
.risk-moderate { background:#fff3cd; color:#7a5a00; border:1px solid #f0c040; }
.risk-high { background:#fde8e8; color:#8b1a1a; border:1px solid #f5a0a0; }

.metric-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-top:1rem; }
.metric-cell { background:#f9f5f0; border:1px solid #e0d6ca; border-radius:12px; padding:1rem; text-align:center; }
.metric-val { font-family:'DM Serif Display',serif; font-size:2rem; color:#2c1810; }
.metric-key { font-size:0.78rem; color:#9a8878; margin-top:0.2rem; text-transform:uppercase; letter-spacing:0.08em; }

.disclaimer { background:#fff8f0; border:1px solid #f0d8b8; border-radius:12px; padding:0.9rem 1.2rem; font-size:0.82rem; color:#8a6040; margin-top:1.5rem; }

/* Audio recorder custom styling */
[data-testid="stAudioRecorder"] button { background:#2c1810 !important; color:#f5f0eb !important; border-radius:50% !important; width:80px !important; height:80px !important; }
[data-testid="stAudioRecorder"] button:hover { opacity:0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Init state ─────────────────────────────────────────────────────────────────
if "session" not in st.session_state:
    st.session_state.session = SessionManager()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_messages" not in st.session_state:
    st.session_state.voice_messages = []
if "analyses" not in st.session_state:
    st.session_state.analyses = []
if "voice_processed" not in st.session_state:
    st.session_state.voice_processed = False
if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

analyzer = CognitiveAnalyzer()
session = st.session_state.session

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ec-header">
  <div class="ec-logo">
    <img src="https://raw.githubusercontent.com/Fannysbth/eldercare-ai/master/logo.png" 
       style="height:150px; width:auto;">
  </div>
  <div>
    <div class="ec-title">ElderCare AI</div>
    <div class="ec-subtitle">Early Cognitive Decline Detection · Screening Tool Only</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_chat, tab_voice, tab_dashboard = st.tabs(["💬  Daily Chat", "🎙️  Voice Conversation", "📊  Dashboard"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    col_chat, col_info = st.columns([3, 1], gap="large")

    with col_chat:
        st.markdown("""
          <div class="ec-card">
            <div class="ec-card-title">Daily Conversation</div>
            <div class="ec-card-meta">Talk naturally — ElderCare AI will listen and gently keep the conversation going.</div>
          </div>
          """, unsafe_allow_html=True)
        
        if st.session_state.messages:
            bubble_html = '<div class="chat-wrap">'
            for msg in st.session_state.messages:
                if msg["role"] == "assistant":
                    bubble_html += f'<div class="bubble-row ai"><div class="bubble-avatar avatar-ai">🧠</div><div class="bubble bubble-ai">{msg["content"]}</div></div>'
                else:
                    bubble_html += f'<div class="bubble-row user"><div class="bubble-avatar avatar-user">👤</div><div class="bubble bubble-user">{msg["content"]}</div></div>'
            bubble_html += '</div>'
            st.markdown(bubble_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:2.5rem 1rem;color:#b0a090;font-size:0.9rem;">
              <div style="font-size:2.5rem;margin-bottom:0.8rem;">👋</div>
              Start a conversation — say hello, share a memory, or just chat about your day.
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Your message", placeholder="Type something… e.g. 'Good morning! How are you?'", label_visibility="collapsed")
            submitted = st.form_submit_button("Send →")

        if submitted and user_input.strip():
            user_text = user_input.strip()
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.spinner("Thinking…"):
                result = analyzer.analyze_text(user_text, st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": result["reply"]})
                st.session_state.analyses.append({
                    "timestamp": datetime.now().isoformat(),
                    "text": user_text,
                    "source": "chat",
                    **result["scores"]
                })
                session.add_entry(user_text, result["scores"])
            st.rerun()

    with col_info:
        st.markdown("""
        <div class="ec-card">
          <div class="ec-card-title">What We Observe</div>
          <div style="font-size:0.85rem;color:#7a6858;line-height:1.7;margin-top:0.5rem;">
            <b>🔤 Vocabulary</b><br>Word variety & richness<br><br>
            <b>📏 Sentence structure</b><br>Complexity & coherence<br><br>
            <b>🔁 Repetition</b><br>Recurring words or ideas<br><br>
            <b>🔗 Topic consistency</b><br>Staying on subject<br><br>
            <b>📅 Memory cues</b><br>Date, name, event recall
          </div>
        </div>
        <div class="disclaimer">⚠️ This is a <b>screening tool only</b>, not a medical diagnosis. Always consult a qualified physician.</div>
        """, unsafe_allow_html=True)

        if st.session_state.analyses:
            latest = st.session_state.analyses[-1]
            risk = latest.get("risk_level", "low")
            score = latest.get("composite_score", 0)
            st.markdown(f"""
            <div class="ec-card" style="margin-top:1rem;">
              <div class="ec-card-title">Latest Signal</div>
              <div style="margin-top:0.6rem;"><span class="risk-badge risk-{risk}">{risk.upper()} RISK</span></div>
              <div style="font-size:0.82rem;color:#9a8878;margin-top:0.8rem;">Composite score: <b>{score:.0f}/100</b></div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VOICE CONVERSATION (using st.audio_input)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_voice:
    col_v1, col_v2 = st.columns([3, 1], gap="large")

    with col_v1:
        st.markdown("""
        <div class="ec-card">
          <div class="ec-card-title">Voice Conversation</div>
          <div class="ec-card-meta">Record your voice, and ElderCare AI will reply with text and speech.</div>
        </div>
        """, unsafe_allow_html=True)

        # Show conversation history as bubbles
        if st.session_state.voice_messages:
            bubble_html = '<div class="chat-wrap">'
            for msg in st.session_state.voice_messages:
                if msg["role"] == "assistant":
                    bubble_html += f'<div class="bubble-row ai"><div class="bubble-avatar avatar-ai">🧠</div><div class="bubble bubble-ai">{msg["content"]}</div></div>'
                else:
                    bubble_html += f'<div class="bubble-row user"><div class="bubble-avatar avatar-user">👤</div><div class="bubble bubble-user">{msg["content"]}</div></div>'
            bubble_html += '</div>'
            st.markdown(bubble_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:2.5rem 1rem;color:#b0a090;font-size:0.9rem;">
              <div style="font-size:2.5rem;margin-bottom:0.8rem;">🎙️</div>
              Click the microphone below, record your voice, then click "Process".<br>
              The AI will reply with text and speech.
            </div>""", unsafe_allow_html=True)

        # Audio recorder using native Streamlit component
        audio_value = st.audio_input("Record your message", key="voice_recorder")

        if audio_value is not None:
            # Read audio bytes
            audio_bytes = audio_value.read()
            if audio_bytes != st.session_state.last_audio_bytes:
                st.session_state.last_audio_bytes = audio_bytes
                st.session_state.voice_processed = False

            if not st.session_state.voice_processed:
                st.session_state.voice_processed = True
                with st.spinner("Transcribing..."):
                    transcript = analyzer.transcribe_bytes(audio_bytes, "recording.wav")

                if not transcript:
                    st.error("❌ Could not transcribe audio. Check your GROQ_API_KEY.")
                else:
                    # Add user message to history
                    st.session_state.voice_messages.append({"role": "user", "content": transcript})

                    # Get AI reply
                    result = analyzer.analyze_transcript(transcript, st.session_state.voice_messages)
                    reply = result["reply"]

                    # Add AI reply to history
                    st.session_state.voice_messages.append({"role": "assistant", "content": reply})

                    # Store analysis
                    st.session_state.analyses.append({
                        "timestamp": datetime.now().isoformat(),
                        "text": transcript,
                        "source": "voice",
                        **result["scores"]
                    })
                    session.add_entry(transcript, result["scores"])

                    # Speak the reply using browser TTS
                    speak_js = f"""
<script>
function speakText(text) {{
    function loadVoicesAndSpeak() {{
        const voices = window.speechSynthesis.getVoices();
        if (!voices.length) {{
            setTimeout(loadVoicesAndSpeak, 100);
            return;
        }}

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.92;  // kecepatan lebih natural
        utterance.pitch = 1.0;   // pitch normal
        utterance.volume = 1.0;

        // pilih suara Indonesia dulu, kalau nggak ada pakai Inggris
        const preferred = voices.find(v => v.lang.includes('id')) || voices.find(v => v.lang.includes('en')) || voices[0];
        utterance.voice = preferred;

        window.speechSynthesis.speak(utterance);
    }}
    loadVoicesAndSpeak();
}}

// langsung speak tanpa tombol karena user baru saja interaksi (rekam audio)
speakText({json.dumps(reply)});
</script>
"""

                    st.markdown(speak_js, unsafe_allow_html=True)

                    # Force rerun to update the chat bubbles
                    st.rerun()

    with col_v2:
        st.markdown("""
        <div class="ec-card">
          <div class="ec-card-title">How to use</div>
          <div style="font-size:0.85rem;color:#7a6858;line-height:1.9;margin-top:0.5rem;">
            1️⃣ Allow microphone access<br>
            2️⃣ Click the microphone button<br>
            3️⃣ Speak naturally (at least 3 seconds)<br>
            4️⃣ Click "Process" (the button appears after recording)<br>
            5️⃣ AI will transcribe and reply with speech
          </div>
        </div>
        <div class="ec-card" style="margin-top:1rem;">
          <div class="ec-card-title">Tips</div>
          <div style="font-size:0.83rem;color:#7a6858;line-height:1.8;margin-top:0.5rem;">
            🔇 Quiet room works best<br>
            💬 Talk about your day, a memory, or describe something you see<br>
            ⏱️ Speak for at least 3 seconds per turn<br>
            🌐 Any language is supported (transcription via Groq Whisper)
          </div>
        </div>
        <div class="disclaimer" style="margin-top:1rem;">
          ⚠️ Voice is transcribed via Groq Whisper (free). AI replies use your browser's built-in text-to-speech.
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.voice_messages:
            turns = len([m for m in st.session_state.voice_messages if m["role"] == "user"])
            st.markdown(f"""
            <div class="ec-card" style="margin-top:1rem;">
              <div class="ec-card-title">Latest Signal</div>
              <div style="margin-top:0.6rem;"><span class="risk-badge risk-{risk}">{risk.upper()} RISK</span></div>
              <div style="font-size:0.82rem;color:#9a8878;margin-top:0.8rem;">Composite score: <b>{score:.0f}/100</b></div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dashboard:
    analyses = st.session_state.analyses

    if not analyses:
        st.markdown("""
        <div class="ec-card" style="text-align:center;padding:3rem 2rem;">
          <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
          <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:#2c1810;margin-bottom:0.6rem;">No data yet</div>
          <div style="font-size:0.9rem;color:#9a8878;">Complete at least one Chat or Voice session to see your dashboard.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        latest = analyses[-1]
        risk = latest.get("risk_level", "low")
        cs = latest.get("composite_score", 0)

        circumference = 2 * 3.14159 * 52
        dash = (cs / 100) * circumference
        ring_color = {"low": "#2d8a4e", "moderate": "#c49a00", "high": "#c0392b"}.get(risk, "#2d8a4e")

        col_d1, col_d2, col_d3 = st.columns([1, 1, 2], gap="large")

        with col_d1:
            st.markdown(f"""
            <div class="ec-card">
              <div class="ec-card-title">Cognitive Risk Score</div>
              <div class="score-ring-wrap">
                <svg width="130" height="130" viewBox="0 0 130 130" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="65" cy="65" r="52" fill="none" stroke="#e8dfd4" stroke-width="12"/>
                  <circle cx="65" cy="65" r="52" fill="none" stroke="{ring_color}" stroke-width="12"
                    stroke-dasharray="{dash:.1f} {circumference:.1f}"
                    stroke-dashoffset="{circumference/4:.1f}" stroke-linecap="round"/>
                  <text x="65" y="60" text-anchor="middle" font-family="DM Serif Display" font-size="26" fill="#2c1810">{cs:.0f}</text>
                  <text x="65" y="78" text-anchor="middle" font-family="DM Sans" font-size="11" fill="#9a8878">/ 100</text>
                </svg>
                <div class="score-label"><span class="risk-badge risk-{risk}">{risk.upper()} RISK</span></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with col_d2:
            avg_ttr = sum(a.get("ttr", 0) for a in analyses) / len(analyses)
            avg_rep = sum(a.get("repetition_score", 0) for a in analyses) / len(analyses)
            chat_n = sum(1 for a in analyses if a.get("source") == "chat")
            voice_n = sum(1 for a in analyses if a.get("source") == "voice")
            st.markdown(f"""
            <div class="ec-card">
              <div class="ec-card-title">Session Summary</div>
              <div class="metric-grid" style="grid-template-columns:1fr;gap:0.7rem;margin-top:0.7rem;">
                <div class="metric-cell"><div class="metric-val">{len(analyses)}</div><div class="metric-key">Total Entries</div></div>
                <div class="metric-cell"><div class="metric-val">{avg_ttr:.2f}</div><div class="metric-key">Avg. TTR</div></div>
                <div class="metric-cell"><div class="metric-val">{avg_rep:.0f}%</div><div class="metric-key">Avg. Repetition</div></div>
              </div>
              <div style="font-size:0.82rem;color:#9a8878;margin-top:0.9rem;">💬 {chat_n} chat &nbsp;·&nbsp; 🎙️ {voice_n} voice</div>
            </div>
            """, unsafe_allow_html=True)

        with col_d3:
            st.markdown('<div class="ec-card"><div class="ec-card-title">Marker Breakdown (Latest Entry)</div>', unsafe_allow_html=True)
            markers = {
                "Type-Token Ratio (TTR)": (latest.get("ttr", 0), 1.0, "Word variety — higher is better"),
                "Sentence Complexity": (latest.get("avg_sentence_length", 0), 20, "Avg words/sentence"),
                "Repetition Rate": (100 - latest.get("repetition_score", 0), 100, "Lower repetition = higher score"),
                "Coherence": (latest.get("coherence_score", 0), 100, "Topic consistency"),
            }
            for label, (val, maxv, desc) in markers.items():
                pct_bar = min(val / maxv, 1.0) if maxv else 0
                bar_color = "#2d8a4e" if pct_bar > 0.6 else ("#c49a00" if pct_bar > 0.35 else "#c0392b")
                st.markdown(f"""
                <div style="margin-bottom:0.9rem;">
                  <div style="display:flex;justify-content:space-between;font-size:0.83rem;color:#4a3828;margin-bottom:0.3rem;">
                    <span><b>{label}</b></span><span style="color:#9a8878;">{desc}</span>
                  </div>
                  <div style="background:#e8dfd4;border-radius:20px;height:8px;">
                    <div style="background:{bar_color};width:{pct_bar*100:.0f}%;height:8px;border-radius:20px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="disclaimer" style="margin-top:1rem;">
          ⚠️ <b>Important:</b> ElderCare AI is a <b>cognitive screening aid only</b> — not a clinical diagnostic tool.
          Scores are based on NLP markers from peer-reviewed research (Lima et al., 2025; PMC12714990).
          A qualified neurologist or geriatrician must evaluate any concerns raised by this tool.
        </div>
        """, unsafe_allow_html=True)