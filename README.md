# SentimentScope 🔍
### Product Review Sentiment Analyzer & Dashboard

A full-stack web application that scrapes product reviews from Amazon/Flipkart,
performs NLP-based sentiment analysis (VADER + TextBlob), and displays insights
on a beautiful interactive dashboard.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (Atlas free tier or local) — see DATABASE_SETUP.md

### 1. First-time setup

**Windows:**
```
setup-windows.bat
```

**Mac / Linux:**
```bash
chmod +x setup-mac-linux.sh run-mac-linux.sh
./setup-mac-linux.sh
```

### 2. Configure database
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set your MONGO_URI
# See DATABASE_SETUP.md for detailed instructions
```

### 3. Run the app

**Windows:**
```
run-windows.bat
```

**Mac / Linux:**
```bash
./run-mac-linux.sh
```

Then open http://localhost:3000 in your browser.

---

## Project Structure

```
sentiment-analyzer/
├── backend/
│   ├── app.py          # Flask API server
│   ├── scraper.py      # Selenium + BeautifulSoup scraper
│   ├── sentiment.py    # VADER + TextBlob NLP analysis
│   ├── requirements.txt
│   └── .env.example    # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx       # Search interface
│   │   │   ├── DashboardPage.jsx  # Analytics dashboard
│   │   │   └── HistoryPage.jsx    # Search history
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   └── utils/api.js           # Axios API client
│   ├── index.html
│   └── package.json
│
├── DATABASE_SETUP.md   # Detailed DB setup guide
├── setup-windows.bat
├── setup-mac-linux.sh
├── run-windows.bat
└── run-mac-linux.sh
```

---

## Features

| Feature | Details |
|---------|---------|
| **Scraping** | Selenium + BeautifulSoup; mock fallback for dev |
| **NLP** | VADER (60%) + TextBlob (40%) weighted ensemble |
| **Charts** | Pie, Bar, Radar, Score distribution (Recharts) |
| **Word Frequency** | Top words by sentiment category |
| **Caching** | 6-hour MongoDB cache to avoid re-scraping |
| **History** | Browse all previous searches |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | Scrape + analyze a product |
| GET | `/api/product/:id` | Get cached product by ID |
| GET | `/api/recent` | List recent searches |
| GET | `/api/wordfreq/:id` | Word frequency data |
| GET | `/api/health` | Health check |

---

## Notes on Web Scraping

Real scraping requires:
- **Chrome** browser installed
- **ChromeDriver** matching your Chrome version (auto-managed by `webdriver-manager`)

If scraping fails (bot detection, rate limits), the app **automatically falls back to 
realistic mock data** so you can still develop and test.

For production use, consider official APIs:
- Amazon: Product Advertising API
- Flipkart: Affiliate API

---

## Tech Stack

**Frontend:** React 18, Vite, Recharts, React Router, Axios  
**Backend:** Flask, Flask-CORS, PyMongo  
**NLP:** VADER Sentiment, TextBlob  
**Scraping:** Selenium, BeautifulSoup4  
**Database:** MongoDB (Atlas or local)
