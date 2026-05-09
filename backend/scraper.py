"""
scraper.py — Uses mock data on cloud (Render has no Chrome).
Real scraping only works when running locally with Chrome installed.
"""

import time
import random
from datetime import datetime, timedelta

# Check if we're running on Render or any cloud
import os
IS_CLOUD = os.getenv("RENDER") or os.getenv("DYNO") or os.getenv("RAILWAY_ENVIRONMENT")

# Only try Selenium if NOT on cloud
SELENIUM_AVAILABLE = False
if not IS_CLOUD:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from bs4 import BeautifulSoup
        SELENIUM_AVAILABLE = True
    except ImportError:
        pass

# ── Mock Data ─────────────────────────────────────────────────────────────────
_MOCK_REVIEWS = {
    "positive": [
        "Absolutely love this product! It exceeded all my expectations. Highly recommend to everyone.",
        "Best purchase I've made this year. The quality is outstanding and delivery was super fast.",
        "Works perfectly as described. Very happy with this purchase, will definitely buy again soon.",
        "Amazing product! The build quality is superb and it looks even better in person than photos.",
        "Excellent value for money. Customer service was also very helpful and extremely responsive.",
        "This is exactly what I needed. Setup was easy and performance has been completely flawless.",
        "Great quality product. Arrived well-packaged and before the estimated delivery date too.",
        "Five stars! This product is a game changer. Using it daily and loving every single minute.",
        "Fantastic product at a great price. Shipping was quick and packaging was very secure.",
        "Very satisfied with this purchase. The product is durable and works exactly as expected.",
        "Incredible product for the price point. Would strongly recommend to friends and family.",
        "Exceeded my expectations on every level. The design is sleek and performance is top notch.",
        "Really impressed with the quality. Feels premium and works better than more expensive brands.",
        "Outstanding purchase. Delivery was prompt and the product was exactly as described online.",
        "Love everything about this. Easy to use, great build quality, and looks fantastic too.",
    ],
    "negative": [
        "Terrible product. Stopped working after just two weeks. Complete waste of my money.",
        "Very disappointed. The product looks nothing like the pictures online. Returning immediately.",
        "Poor quality. Broke on first use. The company customer service was completely unhelpful.",
        "Do NOT buy this. It is cheaply made and does not work as advertised at all. Total scam.",
        "Worst purchase ever. The item arrived damaged and support refused to replace or refund it.",
        "Overpriced junk. Stopped functioning after a month. Save your money and buy elsewhere.",
        "Defective product. Tried three times and it never worked properly. Very frustrated with this.",
        "Bad experience from start to finish. Late delivery, wrong item, and terrible customer support.",
        "Really bad quality control. Mine had scratches out of the box and did not work correctly.",
        "Not worth it at all. Falls apart very easily and the battery life is absolutely terrible.",
        "Cheap materials and poor construction. Broke within days of normal use. Avoid this product.",
        "False advertising. Product does not match the description or photos on the listing at all.",
        "Completely useless product. Does not perform as claimed and customer service ignored my emails.",
        "Save your money. This product failed within the first week and the seller refused to help.",
        "Very poor quality. The item looks nothing like advertised and feels extremely cheap and flimsy.",
    ],
    "neutral": [
        "It is okay I guess. Does what it is supposed to do but nothing particularly special about it.",
        "Average product. Not bad but not great either. Meets the basic requirements adequately.",
        "Decent purchase. A few minor issues but generally acceptable for the price point.",
        "Works as described. Nothing to complain about but also nothing to really rave about either.",
        "It is fine. Expected better quality at this price but it does get the job done okay.",
        "Mixed feelings about this one. Some features are good while others are a bit disappointing.",
        "Arrived on time. Product is functional but the design could certainly be improved significantly.",
        "Standard product. Does the job but there are probably better options available elsewhere.",
        "Not impressed but not disappointed either. Just a very average and ordinary product overall.",
        "Okay for occasional use but would not rely on it for heavy daily usage requirements.",
    ]
}

_AUTHORS = [
    "Rajesh K.", "Priya M.", "Amit S.", "Sneha R.", "Vikram P.",
    "Ananya T.", "Suresh N.", "Deepika L.", "Karthik B.", "Meena V.",
    "Ravi J.", "Pooja G.", "Arun D.", "Kavitha H.", "Nikhil C.",
    "Sunita W.", "Ganesh F.", "Lakshmi Q.", "Arjun R.", "Divya S."
]

def _mock_scrape(query: str, source: str, max_reviews: int) -> dict:
    random.seed(hash(query) % 999983)
    product_name = f"{query.title()} - Premium Edition"

    n_pos = max(1, int(max_reviews * 0.55))
    n_neg = max(1, int(max_reviews * 0.25))
    n_neu = max(0, max_reviews - n_pos - n_neg)

    reviews = []

    def make(pool, count, rating_range):
        for text in random.choices(pool, k=count):
            days_ago = random.randint(1, 365)
            date_str = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%B %d, %Y")
            reviews.append({
                "text":   text,
                "title":  text[:50] + "..." if len(text) > 50 else text,
                "rating": round(random.uniform(*rating_range), 1),
                "author": random.choice(_AUTHORS),
                "date":   date_str,
                "source": source,
            })

    make(_MOCK_REVIEWS["positive"], n_pos, (3.8, 5.0))
    make(_MOCK_REVIEWS["negative"], n_neg, (1.0, 2.5))
    make(_MOCK_REVIEWS["neutral"],  n_neu, (2.5, 3.7))
    random.shuffle(reviews)

    return {"product_name": product_name, "reviews": reviews[:max_reviews]}


def _get_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    return webdriver.Chrome(options=options)


def _scrape_amazon(query: str, max_reviews: int) -> dict:
    from bs4 import BeautifulSoup
    import re
    driver = _get_driver()
    reviews = []
    product_name = query
    try:
        driver.get(f"https://www.amazon.in/s?k={query.replace(' ', '+')}")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        first = soup.select_one("a.a-link-normal.s-underline-text") or \
                soup.select_one("[data-component-type='s-search-result'] h2 a")
        if not first:
            return {"product_name": query, "reviews": []}
        driver.get("https://www.amazon.in" + first["href"])
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        t = soup.select_one("#productTitle")
        if t: product_name = t.get_text(strip=True)
        asin = re.search(r"/dp/([A-Z0-9]{10})", driver.current_url)
        if asin:
            driver.get(f"https://www.amazon.in/product-reviews/{asin.group(1)}?pageSize=20")
            time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for el in soup.select("[data-hook='review']")[:max_reviews]:
            body = el.select_one("[data-hook='review-body'] span")
            if not body: continue
            rating_el = el.select_one("[data-hook='review-star-rating'] span")
            rating_txt = rating_el.get_text(strip=True) if rating_el else "3.0"
            m = re.search(r"(\d+\.?\d*)", rating_txt)
            reviews.append({
                "text":   body.get_text(strip=True),
                "title":  "",
                "rating": float(m.group(1)) if m else 3.0,
                "author": "Amazon Customer",
                "date":   "",
                "source": "amazon"
            })
    finally:
        driver.quit()
    return {"product_name": product_name, "reviews": reviews}


def scrape_reviews(query: str, source: str = "amazon", max_reviews: int = 20) -> dict:
    """
    On cloud (Render): always use mock data.
    Locally with Chrome: attempt real scraping, fall back to mock.
    """
    if IS_CLOUD:
        print(f"[Scraper] Cloud environment detected — using mock data for '{query}'")
        return _mock_scrape(query, source, max_reviews)

    if SELENIUM_AVAILABLE:
        try:
            result = _scrape_amazon(query, max_reviews) if source != "flipkart" else _mock_scrape(query, source, max_reviews)
            if result["reviews"]:
                return result
        except Exception as e:
            print(f"[Scraper] Real scraping failed: {e}. Using mock data.")

    print(f"[Scraper] Using mock data for '{query}' ({source})")
    return _mock_scrape(query, source, max_reviews)