"""
cognitive_analyzer.py
─────────────────────
Research-based cognitive linguistic analysis.

Key references:
• Lima et al. (2025) — spoken language biomarkers, Communications Medicine / Nature
• PMC12714990 / Frontiers in Aging Neuroscience (2025) — LLM + speech for dementia

Thresholds (conservative):
  Low risk    : composite < 40
  Moderate    : 40–64
  High risk   : ≥ 65

API keys (all FREE):
  ANTHROPIC_API_KEY → stores your GEMINI API key (name kept for compatibility)
  GROQ_API_KEY      → Groq free tier, Whisper transcription
"""

import os
import re
import tempfile
from collections import Counter

import google.generativeai as genai

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# ── Linguistic Features ────────────────────────────────────────────────────────

def tokenize(text: str) -> list:
    return re.findall(r"\b[a-zA-Z']+\b", text.lower())

def compute_ttr(tokens: list) -> float:
    if not tokens: return 1.0
    return len(set(tokens)) / len(tokens)

def compute_repetition_score(tokens: list) -> float:
    if len(tokens) < 4: return 0.0
    bigrams = [(tokens[i], tokens[i+1]) for i in range(len(tokens)-1)]
    counts = Counter(bigrams)
    repeated = sum(v - 1 for v in counts.values() if v > 1)
    return min(repeated / max(len(bigrams), 1) * 100, 100)

def compute_sentence_metrics(text: str) -> tuple:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text.strip()) if len(s.strip()) > 2]
    if not sentences: return 0.0, 0.0
    lengths = [len(tokenize(s)) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths) if len(lengths) > 1 else 0.0
    return avg, variance

def compute_coherence_score(text: str, history: list) -> float:
    STOPWORDS = {
        "the","a","an","is","are","was","were","be","been","have","has","had",
        "do","does","did","will","would","could","should","i","you","he","she",
        "we","they","it","this","that","my","your","his","her","our","their",
        "and","or","but","if","in","on","at","to","for","of","with","by",
        "from","so","just","then","not","no","yes","ok","well","yeah","um","uh",
    }
    current_words = set(tokenize(text)) - STOPWORDS
    if not current_words or not history: return 80.0
    prev_user = [m["content"] for m in history if m["role"] == "user"]
    if not prev_user: return 80.0
    prev_words = set(tokenize(prev_user[-1])) - STOPWORDS
    if not prev_words: return 80.0
    overlap = len(current_words & prev_words)
    union = len(current_words | prev_words)
    return min((overlap / union if union else 0) * 400, 100)

def compute_composite_score(ttr, repetition, avg_sentence_length, coherence) -> float:
    score = 0.0
    if ttr < 0.35:              score += 35
    elif ttr < 0.45:            score += 25
    elif ttr < 0.55:            score += 12
    if repetition > 30:         score += 30
    elif repetition > 20:       score += 20
    elif repetition > 10:       score += 10
    if avg_sentence_length < 5:     score += 20
    elif avg_sentence_length < 8:   score += 12
    elif avg_sentence_length < 11:  score += 5
    if coherence < 25:          score += 15
    elif coherence < 40:        score += 8
    elif coherence < 55:        score += 3
    return min(score, 100)

def risk_level(composite: float) -> str:
    if composite < 40: return "low"
    elif composite < 65: return "moderate"
    else: return "high"


# ── System Prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are ElderCare AI, a warm and gentle conversational companion for older adults.
Your purpose is to have natural, friendly daily conversations — not to perform medical tests.

Guidelines:
- Be warm, patient, and encouraging
- Ask open-ended questions that invite storytelling (memories, daily life, opinions)
- Gently steer toward topics that naturally reveal memory and language use
  (e.g. "Tell me about your morning", "What's a favourite meal you remember?")
- Never mention cognitive assessment, dementia, or scoring
- Keep responses concise: 2–3 sentences maximum
- If the person seems confused or distressed, be calm and reassuring
- Respond in the same language the user speaks in"""

FALLBACK_REPLIES = [
    "That's lovely to hear! Could you tell me more about that?",
    "How wonderful! What else has been on your mind lately?",
    "Thank you for sharing that. What does a typical morning look like for you?",
    "That sounds really interesting. Do you have a favourite memory from that time?",
    "I'd love to hear more. What happened next?",
]


# ── Main Class ─────────────────────────────────────────────────────────────────

class CognitiveAnalyzer:
    def __init__(self):
        # ANTHROPIC_API_KEY variable holds Gemini key (name kept for compatibility)
        gemini_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT,
            )
        else:
            self.model = None

        groq_key = os.environ.get("GROQ_API_KEY", "")
        self.groq = Groq(api_key=groq_key) if (GROQ_AVAILABLE and groq_key) else None

    # ── Text / Chat ────────────────────────────────────────────────────────────
    def analyze_text(self, user_text: str, history: list) -> dict:
        tokens = tokenize(user_text)
        ttr = compute_ttr(tokens)
        rep = compute_repetition_score(tokens)
        avg_sl, sl_var = compute_sentence_metrics(user_text)
        coh = compute_coherence_score(user_text, history)
        composite = compute_composite_score(ttr, rep, avg_sl, coh)

        scores = {
            "ttr": ttr,
            "repetition_score": rep,
            "avg_sentence_length": avg_sl,
            "sentence_length_variance": sl_var,
            "coherence_score": coh,
            "composite_score": composite,
            "risk_level": risk_level(composite),
        }
        return {"reply": self._get_ai_reply(user_text, history), "scores": scores}

    def analyze_transcript(self, transcript: str, history: list) -> dict:
        """Same as analyze_text — used by voice conversation tab."""
        return self.analyze_text(transcript, history)

    def _get_ai_reply(self, user_text: str, history: list) -> str:
        if not self.model:
            import random
            return random.choice(FALLBACK_REPLIES)
        gemini_history = []
        for m in history[-10:]:
            role = "user" if m["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [m["content"]]})
        try:
            chat = self.model.start_chat(history=gemini_history)
            return chat.send_message(user_text).text.strip()
        except Exception:
            import random
            return random.choice(FALLBACK_REPLIES)

    # ── Audio upload (old tab, kept for compatibility) ─────────────────────────
    def analyze_audio(self, uploaded_file) -> dict:
        transcript = self._transcribe_file(uploaded_file)
        if not transcript:
            return {"transcript": "", "scores": {}}
        tokens = tokenize(transcript)
        ttr = compute_ttr(tokens)
        rep = compute_repetition_score(tokens)
        avg_sl, sl_var = compute_sentence_metrics(transcript)
        composite = compute_composite_score(ttr, rep, avg_sl, 80.0)
        scores = {
            "ttr": ttr, "repetition_score": rep,
            "avg_sentence_length": avg_sl, "sentence_length_variance": sl_var,
            "coherence_score": 80.0, "composite_score": composite,
            "risk_level": risk_level(composite),
        }
        return {"transcript": transcript, "scores": scores}

    def _transcribe_file(self, uploaded_file) -> str:
        if not self.groq: return ""
        suffix = f".{uploaded_file.name.split('.')[-1]}" if "." in uploaded_file.name else ".wav"
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                result = self.groq.audio.transcriptions.create(
                    file=(uploaded_file.name, f),
                    model="whisper-large-v3",
                    response_format="text",
                )
            os.unlink(tmp_path)
            return result.strip() if isinstance(result, str) else str(result).strip()
        except Exception:
            return ""

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "recording.wav") -> str:
        """Transcribe raw audio bytes — used by voice conversation tab."""
        if not self.groq: return ""
        suffix = "." + filename.split(".")[-1] if "." in filename else ".wav"
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                result = self.groq.audio.transcriptions.create(
                    file=(filename, f),
                    model="whisper-large-v3",
                    response_format="text",
                )
            os.unlink(tmp_path)
            return result.strip() if isinstance(result, str) else str(result).strip()
        except Exception:
            return ""
