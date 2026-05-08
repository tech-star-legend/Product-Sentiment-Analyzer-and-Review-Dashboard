from flask import Flask, jsonify, request
from flask_cors import CORS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random

app = Flask(__name__)
CORS(app)

analyzer = SentimentIntensityAnalyzer()

MOCK_REVIEWS = {
    "oppo": [
        "Oppo camera quality is absolutely stunning, best I have ever used!",
        "Battery drains so fast, very disappointed with this phone.",
        "Good build quality and nice display but software could be better.",
        "Worst customer service experience ever with Oppo.",
        "Amazing value for money, love the design and performance.",
        "The phone heats up too quickly during gaming.",
        "Oppo's fast charging is a game changer, charges in under 30 minutes!",
        "Screen cracked easily, not very durable.",
        "Smooth performance and great camera modes.",
        "Average phone, nothing special to talk about.",
    ],
    "samsung": [
        "Samsung Galaxy is the best Android phone money can buy!",
        "Overpriced for what you get honestly.",
        "One UI is smooth and the display is gorgeous.",
        "Battery life could be much better for the price.",
        "Camera system is versatile and takes amazing shots.",
        "Build quality feels premium and solid.",
        "Software updates are slow and frustrating.",
        "Night mode photography is absolutely incredible.",
        "Good phone overall, would recommend to friends.",
        "TouchWiz lags sometimes which is annoying.",
    ],
    "iphone": [
        "iPhone is simply the best smartphone ever made.",
        "Way too expensive, not worth the price tag.",
        "iOS is smooth and the ecosystem is great.",
        "Battery life is disappointing compared to Android.",
        "Camera quality is unmatched in low light.",
        "No headphone jack is still frustrating.",
        "Build quality and premium feel is excellent.",
        "Face ID works perfectly even in dark.",
        "Great phone but too pricey for average users.",
        "App Store has the best quality apps.",
    ],
    "redmi": [
        "Redmi offers the best budget smartphone experience!",
        "Ads in MIUI are very annoying and intrusive.",
        "Great battery life and fast charging for the price.",
        "Build quality feels cheap and plasticky.",
        "Performance is smooth for daily use tasks.",
        "Camera is decent but struggles in low light.",
        "Best value phone you can buy under 15000 rupees.",
        "Software is bloated with unnecessary apps.",
        "Display quality is surprisingly good for budget segment.",
        "Good phone but MIUI needs serious improvement.",
    ],
    "oneplus": [
        "OnePlus OxygenOS is the cleanest Android available!",
        "Heating issues during gaming are a concern.",
        "Flagship performance at mid-range price is amazing.",
        "No wireless charging is a major disappointment.",
        "Display is super smooth at 120Hz refresh rate.",
        "Camera has improved a lot in recent models.",
        "Build quality and design looks very premium.",
        "After-sale service is excellent and responsive.",
        "Alert slider is a unique and useful feature.",
        "Battery life is outstanding, lasts all day easily.",
    ],
}

DEFAULT_REVIEWS = [
    "This product is really good and worth buying!",
    "Terrible quality, broke after one week of use.",
    "Average product, nothing special about it.",
    "Excellent build quality and great performance overall.",
    "Poor customer support ruined my experience.",
    "Good value for money, would recommend.",
    "Delivery was fast and packaging was great.",
    "Not as described, very disappointed with the purchase.",
    "Works perfectly, very happy with this product.",
    "Okay product but could have been better quality.",
]


def get_reviews(product_name):
    key = product_name.lower().strip()
    for brand, reviews in MOCK_REVIEWS.items():
        if brand in key or key in brand:
            return reviews
    return DEFAULT_REVIEWS


def classify_sentiment(score):
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"


@app.route("/analyze", methods=["GET"])
def analyze():
    product = request.args.get("product", "").strip()
    if not product:
        return jsonify({"error": "Product name is required"}), 400

    reviews = get_reviews(product)
    results = []

    positive = 0
    negative = 0
    neutral = 0

    for review in reviews:
        scores = analyzer.polarity_scores(review)
        compound = scores["compound"]
        sentiment = classify_sentiment(compound)

        if sentiment == "positive":
            positive += 1
        elif sentiment == "negative":
            negative += 1
        else:
            neutral += 1

        results.append({
            "review": review,
            "sentiment": sentiment,
            "score": round(compound, 3),
        })

    total = len(results)
    avg_score = round(sum(r["score"] for r in results) / total, 3) if total else 0

    return jsonify({
        "product": product,
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "average_score": avg_score,
        "reviews": results,
    })


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running", "message": "Sentiment API is live"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)