"""
scraper.py — Review scraper for Amazon & Flipkart using Selenium + BeautifulSoup.

IMPORTANT:
  Web scraping e-commerce sites may violate their Terms of Service.
  Use this for educational/personal research only, and respect robots.txt.
  For production, use official APIs (Amazon Product Advertising API, etc.)

This module provides:
  1. Real scraping via Selenium (requires ChromeDriver)
  2. A rich mock-data fallback for development/testing
"""

import time
import random
import re
from datetime import datetime, timedelta

# ── Optional Selenium import ───────────────────────────────────────────────────
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def _get_driver():
    """Configure headless Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(options=options)


# ── Amazon Scraper ─────────────────────────────────────────────────────────────
def _scrape_amazon(query: str, max_reviews: int) -> dict:
    driver = _get_driver()
    reviews = []
    product_name = query

    try:
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        first_result = soup.select_one("a.a-link-normal.s-underline-text")
        if not first_result:
            first_result = soup.select_one("[data-component-type='s-search-result'] h2 a")

        if not first_result:
            return {"product_name": query, "reviews": []}

        product_url = "https://www.amazon.in" + first_result["href"]
        driver.get(product_url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        title_el = soup.select_one("#productTitle")
        if title_el:
            product_name = title_el.get_text(strip=True)

        # Navigate to reviews page
        asin_match = re.search(r"/dp/([A-Z0-9]{10})", product_url)
        if asin_match:
            asin = asin_match.group(1)
            review_url = f"https://www.amazon.in/product-reviews/{asin}?pageSize=20"
            driver.get(review_url)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        review_els = soup.select("[data-hook='review']")

        for el in review_els[:max_reviews]:
            body_el = el.select_one("[data-hook='review-body'] span")
            rating_el = el.select_one("[data-hook='review-star-rating'] span")
            title_el = el.select_one("[data-hook='review-title'] span:not(.a-icon-alt)")
            date_el = el.select_one("[data-hook='review-date']")
            author_el = el.select_one(".a-profile-name")

            if not body_el:
                continue

            text = body_el.get_text(strip=True)
            rating_text = rating_el.get_text(strip=True) if rating_el else "3.0"
            rating_match = re.search(r"(\d+\.?\d*)", rating_text)
            rating = float(rating_match.group(1)) if rating_match else 3.0

            reviews.append({
                "text": text,
                "title": title_el.get_text(strip=True) if title_el else "",
                "rating": rating,
                "author": author_el.get_text(strip=True) if author_el else "Anonymous",
                "date": date_el.get_text(strip=True) if date_el else "",
                "source": "amazon"
            })

    finally:
        driver.quit()

    return {"product_name": product_name, "reviews": reviews}


# ── Flipkart Scraper ───────────────────────────────────────────────────────────
def _scrape_flipkart(query: str, max_reviews: int) -> dict:
    driver = _get_driver()
    reviews = []
    product_name = query

    try:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(2)

        # Close login popup if appears
        try:
            close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
            close_btn.click()
        except Exception:
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        first_result = soup.select_one("a[href*='/p/']")
        if not first_result:
            return {"product_name": query, "reviews": []}

        product_url = "https://www.flipkart.com" + first_result["href"]
        driver.get(product_url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        title_el = soup.select_one("span.B_NuCI") or soup.select_one("h1.yhB1nd")
        if title_el:
            product_name = title_el.get_text(strip=True)

        # Click "All Reviews" button
        try:
            all_reviews_btn = driver.find_element(By.XPATH, "//span[contains(text(),'All') and contains(text(),'Reviews')]")
            all_reviews_btn.click()
            time.sleep(2)
        except Exception:
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        review_els = soup.select("div.col.EPCmJX") or soup.select("div._27M-vq")

        for el in review_els[:max_reviews]:
            body_el = el.select_one("div.t-ZTKy") or el.select_one("p.F7cALs")
            rating_el = el.select_one("div._3LWZlK")
            title_el = el.select_one("p._2-N8zT")
            author_el = el.select_one("p._2sc7ZR span")
            date_el = el.select_one("p._2sc7ZR")

            if not body_el:
                continue

            text = body_el.get_text(strip=True)
            rating = float(rating_el.get_text(strip=True)) if rating_el else 3.0

            reviews.append({
                "text": text,
                "title": title_el.get_text(strip=True) if title_el else "",
                "rating": rating,
                "author": author_el.get_text(strip=True) if author_el else "Anonymous",
                "date": date_el.get_text(strip=True) if date_el else "",
                "source": "flipkart"
            })

    finally:
        driver.quit()

    return {"product_name": product_name, "reviews": reviews}


# ── Mock Data Generator (Development Fallback) ─────────────────────────────────
_MOCK_REVIEWS = {
    "positive": [
        "Absolutely love this product! It exceeded all my expectations. Highly recommend.",
        "Best purchase I've made this year. The quality is outstanding and delivery was fast.",
        "Works perfectly as described. Very happy with this purchase, will definitely buy again.",
        "Amazing product! The build quality is superb and it looks even better in person.",
        "Excellent value for money. Customer service was also very helpful and responsive.",
        "This is exactly what I needed. Setup was easy and performance has been flawless.",
        "Great quality product. Arrived well-packaged and before the estimated delivery date.",
        "Five stars! This product is a game changer. Using it daily and loving every minute.",
        "Fantastic product at a great price. Shipping was quick and packaging was secure.",
        "Very satisfied with this purchase. The product is durable and works as expected.",
    ],
    "negative": [
        "Terrible product. Stopped working after just two weeks. Complete waste of money.",
        "Very disappointed. The product looks nothing like the pictures. Returning immediately.",
        "Poor quality. Broke on first use. The company's customer service was unhelpful.",
        "Do NOT buy this. It's cheaply made and doesn't work as advertised. Total scam.",
        "Worst purchase ever. The item arrived damaged and support refused to replace it.",
        "Overpriced junk. Stopped functioning after a month. Save your money and buy elsewhere.",
        "Defective product. Tried three times and it never worked properly. Very frustrated.",
        "Bad experience from start to finish. Late delivery, wrong item, terrible support.",
        "Really bad quality control. Mine had scratches out of the box and didn't work right.",
        "Not worth it at all. Falls apart easily and the battery life is absolutely terrible.",
    ],
    "neutral": [
        "It's okay I guess. Does what it's supposed to do but nothing special about it.",
        "Average product. Not bad but not great either. Meets basic requirements.",
        "Decent purchase. A few minor issues but generally acceptable for the price.",
        "Works as described. Nothing to complain about but also nothing to rave about.",
        "It's fine. Expected better quality at this price but it gets the job done.",
        "Mixed feelings. Some features are good, others are disappointing.",
        "Arrived on time. Product is functional but design could be improved.",
        "Standard product. Does the job but there are better options available.",
        "Not impressed but not disappointed either. Just an average product overall.",
        "Okay for occasional use but wouldn't rely on it for heavy daily usage.",
    ]
}

_AUTHORS = ["Rajesh K.", "Priya M.", "Amit S.", "Sneha R.", "Vikram P.", "Ananya T.",
            "Suresh N.", "Deepika L.", "Karthik B.", "Meena V.", "Ravi J.", "Pooja G.",
            "Arun D.", "Kavitha H.", "Nikhil C.", "Sunita W.", "Ganesh F.", "Lakshmi Q."]

def _mock_scrape(query: str, source: str, max_reviews: int) -> dict:
    """Generate realistic mock reviews for development/testing."""
    random.seed(hash(query) % 999999)
    product_name = f"{query.title()} - Premium Edition"
    reviews = []

    # Distribution: ~55% positive, ~25% negative, ~20% neutral
    n_pos = max(1, int(max_reviews * 0.55))
    n_neg = max(1, int(max_reviews * 0.25))
    n_neu = max_reviews - n_pos - n_neg

    def make_reviews(pool, count, rating_range, sentiment_label):
        selected = random.choices(pool, k=count)
        for i, text in enumerate(selected):
            days_ago = random.randint(1, 365)
            review_date = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%B %d, %Y")
            reviews.append({
                "text": text,
                "title": text[:50] + "..." if len(text) > 50 else text,
                "rating": round(random.uniform(*rating_range), 1),
                "author": random.choice(_AUTHORS),
                "date": review_date,
                "source": source,
            })

    make_reviews(_MOCK_REVIEWS["positive"], n_pos, (3.8, 5.0), "positive")
    make_reviews(_MOCK_REVIEWS["negative"], n_neg, (1.0, 2.5), "negative")
    make_reviews(_MOCK_REVIEWS["neutral"],  n_neu, (2.5, 3.7), "neutral")

    random.shuffle(reviews)
    return {"product_name": product_name, "reviews": reviews[:max_reviews]}


# ── Public entry point ─────────────────────────────────────────────────────────
def scrape_reviews(query: str, source: str = "amazon", max_reviews: int = 20) -> dict:
    """
    Main scraping function. Attempts real scraping first; falls back to mock data.

    Args:
        query: Product search query
        source: "amazon" or "flipkart"
        max_reviews: Maximum number of reviews to collect

    Returns:
        dict with keys: product_name, reviews (list of dicts)
    """
    if SELENIUM_AVAILABLE:
        try:
            if source == "flipkart":
                result = _scrape_flipkart(query, max_reviews)
            else:
                result = _scrape_amazon(query, max_reviews)

            if result["reviews"]:
                return result
            # Fall through to mock if no reviews found
        except Exception as e:
            print(f"[Scraper] Real scraping failed: {e}. Using mock data.")

    print(f"[Scraper] Using mock data for '{query}' ({source})")
    return _mock_scrape(query, source, max_reviews)
