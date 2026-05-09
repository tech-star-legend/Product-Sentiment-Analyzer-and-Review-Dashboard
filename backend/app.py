from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from flask.json.provider import DefaultJSONProvider
from datetime import datetime, timezone
import os
import traceback
from dotenv import load_dotenv
from sentiment import analyze_sentiment
from scraper import scrape_reviews
import uuid

load_dotenv()

app = Flask(__name__)

# ── CORS — allow ALL origins ──────────────────────────────────────────────────
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

# ── Flask 3.x JSON provider ───────────────────────────────────────────────────
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_provider_class = CustomJSONProvider
app.json = CustomJSONProvider(app)

# ── MongoDB ───────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/sentimentdb")
client = MongoClient(MONGO_URI)
db = client.get_default_database() if "mongodb.net" in MONGO_URI else client["sentimentdb"]
products_col = db["products"]
reviews_col  = db["reviews"]

def now_ts():
    return datetime.now(timezone.utc).timestamp()

def clean_doc(doc):
    if isinstance(doc, dict):
        return {k: clean_doc(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [clean_doc(i) for i in doc]
    if isinstance(doc, ObjectId):
        return str(obj)
    return doc

# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

# ── Search ────────────────────────────────────────────────────────────────────
@app.route("/api/search", methods=["POST", "OPTIONS"])
def search_product():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        data        = request.get_json()
        query       = data.get("query", "").strip()
        source      = data.get("source", "amazon")
        max_reviews = int(data.get("max_reviews", 10))

        if not query:
            return jsonify({"error": "Query is required"}), 400

        print(f"[Search] query='{query}' source={source} max={max_reviews}")

        # Cache check
        existing = products_col.find_one({
            "query": query.lower(),
            "source": source,
            "scraped_at": {"$gte": now_ts() - 21600}
        })

        if existing:
            print("[Search] Returning cached result")
            product_id = str(existing["_id"])
            reviews = list(reviews_col.find({"product_id": product_id}, {"_id": 0}))
            return jsonify({
                "product_id":   product_id,
                "product_name": existing["product_name"],
                "source":       source,
                "cached":       True,
                "reviews":      reviews,
                "summary":      existing.get("summary", {})
            })

        # Scrape
        print("[Search] Scraping...")
        scraped = scrape_reviews(query, source, max_reviews)
        print(f"[Search] Got {len(scraped['reviews'])} reviews")

        if not scraped["reviews"]:
            return jsonify({"error": "No reviews found."}), 404

        # Sentiment
        analyzed_reviews = []
        pos = neg = neu = 0
        for r in scraped["reviews"]:
            r.pop("_id", None)
            result = analyze_sentiment(r["text"])
            r.update(result)
            if r["sentiment"] == "positive":   pos += 1
            elif r["sentiment"] == "negative": neg += 1
            else:                              neu += 1
            analyzed_reviews.append(r)

        total = len(analyzed_reviews)
        summary = {
            "total":        total,
            "positive":     pos,
            "negative":     neg,
            "neutral":      neu,
            "positive_pct": round(pos / total * 100, 1) if total else 0,
            "negative_pct": round(neg / total * 100, 1) if total else 0,
            "neutral_pct":  round(neu / total * 100, 1) if total else 0,
            "avg_score":    round(sum(r["score"] for r in analyzed_reviews) / total, 3) if total else 0,
        }

        # Save
        product_id = str(uuid.uuid4())
        products_col.insert_one({
            "_id":          product_id,
            "query":        query.lower(),
            "product_name": scraped["product_name"],
            "source":       source,
            "scraped_at":   now_ts(),
            "summary":      summary
        })

        for r in analyzed_reviews:
            r["product_id"] = product_id
            r.pop("_id", None)

        reviews_col.insert_many(analyzed_reviews)

        print(f"[Search] Done. {total} reviews saved.")
        return jsonify({
            "product_id":   product_id,
            "product_name": scraped["product_name"],
            "source":       source,
            "cached":       False,
            "reviews":      analyzed_reviews,
            "summary":      summary
        })

    except Exception as e:
        print(f"[Search ERROR] {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ── Get Product ───────────────────────────────────────────────────────────────
@app.route("/api/product/<product_id>", methods=["GET"])
def get_product(product_id):
    product = products_col.find_one({"_id": product_id})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    reviews = list(reviews_col.find({"product_id": product_id}, {"_id": 0}))
    product["_id"] = str(product["_id"])
    return jsonify({"product": product, "reviews": reviews})

# ── Recent ────────────────────────────────────────────────────────────────────
@app.route("/api/recent", methods=["GET"])
def recent_searches():
    recent = list(products_col.find(
        {}, {"_id": 1, "query": 1, "product_name": 1, "source": 1, "summary": 1, "scraped_at": 1}
    ).sort("scraped_at", -1).limit(10))
    for p in recent:
        p["_id"] = str(p["_id"])
    return jsonify({"recent": recent})

# ── Word Frequency ────────────────────────────────────────────────────────────
@app.route("/api/wordfreq/<product_id>", methods=["GET"])
def word_frequency(product_id):
    from collections import Counter
    import re
    STOP = {"the","a","an","is","it","in","on","and","or","to","of","for","this",
            "that","was","with","but","not","are","i","my","me","we","be","at","by",
            "as","so","if","do","he","she","they","you","have","has","had","its",
            "our","your","their","all","from","just","very","am","been"}
    reviews = list(reviews_col.find({"product_id": product_id}, {"text": 1, "sentiment": 1}))
    all_w, pos_w, neg_w = [], [], []
    for r in reviews:
        tokens = [w for w in re.findall(r"\b[a-z]{3,}\b", r.get("text","").lower()) if w not in STOP]
        all_w.extend(tokens)
        if r.get("sentiment") == "positive":   pos_w.extend(tokens)
        elif r.get("sentiment") == "negative": neg_w.extend(tokens)
    return jsonify({
        "all":      Counter(all_w).most_common(30),
        "positive": Counter(pos_w).most_common(20),
        "negative": Counter(neg_w).most_common(20),
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)