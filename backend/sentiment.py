"""
sentiment.py — Dual-engine sentiment analysis using VADER + TextBlob
Falls back gracefully if either library is unavailable.
"""
from datetime import datetime

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a review text.
    Returns a dict with:
      - sentiment: "positive" | "negative" | "neutral"
      - score: float in [-1, 1]
      - confidence: float in [0, 1]
      - vader_compound: float (if available)
      - textblob_polarity: float (if available)
    """
    if not text or not text.strip():
        return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}

    scores = {}

    # ── VADER ─────────────────────────────────────────────────────────────────
    if VADER_AVAILABLE:
        vs = _vader.polarity_scores(text)
        scores["vader_compound"] = vs["compound"]
        scores["vader_pos"] = vs["pos"]
        scores["vader_neg"] = vs["neg"]
        scores["vader_neu"] = vs["neu"]

    # ── TextBlob ──────────────────────────────────────────────────────────────
    if TEXTBLOB_AVAILABLE:
        blob = TextBlob(text)
        scores["textblob_polarity"] = blob.sentiment.polarity
        scores["textblob_subjectivity"] = blob.sentiment.subjectivity

    # ── Aggregate score ───────────────────────────────────────────────────────
    if VADER_AVAILABLE and TEXTBLOB_AVAILABLE:
        # Weighted average: VADER 60%, TextBlob 40%
        final_score = 0.6 * scores["vader_compound"] + 0.4 * scores["textblob_polarity"]
    elif VADER_AVAILABLE:
        final_score = scores["vader_compound"]
    elif TEXTBLOB_AVAILABLE:
        final_score = scores["textblob_polarity"]
    else:
        # Naive fallback: keyword counting
        final_score = _naive_sentiment(text)

    # ── Classification thresholds ─────────────────────────────────────────────
    if final_score >= 0.05:
        sentiment = "positive"
    elif final_score <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    confidence = min(abs(final_score) * 1.5, 1.0)

    return {
        "sentiment": sentiment,
        "score": round(final_score, 4),
        "confidence": round(confidence, 4),
        **scores
    }


def _naive_sentiment(text: str) -> float:
    """Keyword-based fallback when NLP libs are unavailable."""
    POS = {"good","great","excellent","amazing","love","best","awesome","fantastic",
           "perfect","happy","satisfied","recommend","quality","fast","reliable"}
    NEG = {"bad","terrible","awful","worst","hate","poor","broken","slow","defective",
           "disappointed","waste","refund","return","damaged","fake","useless"}
    words = set(text.lower().split())
    p = len(words & POS)
    n = len(words & NEG)
    total = p + n
    if total == 0:
        return 0.0
    return (p - n) / total
