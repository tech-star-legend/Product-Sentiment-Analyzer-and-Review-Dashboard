import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Zap, ShoppingBag, TrendingUp, Clock } from 'lucide-react'
import { searchProduct, getRecentSearches } from '../utils/api'
import styles from './HomePage.module.css'

const SOURCES = [
  { value: 'amazon', label: 'Amazon', emoji: '📦' },
  { value: 'flipkart', label: 'Flipkart', emoji: '🛒' },
]

const SUGGESTIONS = [
  'iPhone 15', 'Samsung Galaxy S24', 'boAt Airdopes',
  'Noise Buds', 'Laptop Cooling Pad', 'MI Smart TV',
  'Kindle Paperwhite', 'Logitech Mouse', 'Canon Camera'
]

export default function HomePage() {
  const [query, setQuery] = useState('')
  const [source, setSource] = useState('amazon')
  const [maxReviews, setMaxReviews] = useState(20)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [recent, setRecent] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    getRecentSearches()
      .then(r => setRecent(r.data.recent || []))
      .catch(() => {})
  }, [])

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await searchProduct(query, source, maxReviews)
      navigate(`/dashboard/${res.data.product_id}`, { state: res.data })
    } catch (err) {
      setError(err.response?.data?.error || 'Search failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      {/* Ambient glow */}
      <div className={styles.glow1} />
      <div className={styles.glow2} />

      <div className={styles.hero}>
        <div className={styles.tagline}>
          <Zap size={14} />
          <span>NLP-Powered Review Intelligence</span>
        </div>

        <h1 className={styles.title}>
          Understand what customers
          <br />
          <em>really</em> think
        </h1>

        <p className={styles.subtitle}>
          Search any product to instantly analyze sentiment across hundreds of reviews.
          Powered by VADER & TextBlob NLP engines.
        </p>

        {/* Search Form */}
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <div className={styles.inputRow}>
            <div className={styles.inputWrap}>
              <Search size={18} className={styles.searchIcon} />
              <input
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Search for a product..."
                className={styles.input}
                disabled={loading}
              />
            </div>

            <select
              value={source}
              onChange={e => setSource(e.target.value)}
              className={styles.select}
              disabled={loading}
            >
              {SOURCES.map(s => (
                <option key={s.value} value={s.value}>
                  {s.emoji} {s.label}
                </option>
              ))}
            </select>

            <select
              value={maxReviews}
              onChange={e => setMaxReviews(Number(e.target.value))}
              className={styles.select}
              disabled={loading}
            >
              <option value={10}>10 reviews</option>
              <option value={20}>20 reviews</option>
              <option value={30}>30 reviews</option>
              <option value={50}>50 reviews</option>
            </select>

            <button type="submit" className={styles.btn} disabled={loading || !query.trim()}>
              {loading ? (
                <span className={styles.spinner} />
              ) : (
                <>
                  <Search size={16} />
                  Analyze
                </>
              )}
            </button>
          </div>

          {error && (
            <div className={styles.error}>{error}</div>
          )}

          {loading && (
            <div className={styles.loadingMsg}>
              <span className={styles.spinner} />
              Scraping reviews & running sentiment analysis...
            </div>
          )}
        </form>

        {/* Suggestions */}
        <div className={styles.suggestions}>
          <span className={styles.suggestLabel}>Try:</span>
          {SUGGESTIONS.map(s => (
            <button key={s} className={styles.chip} onClick={() => setQuery(s)}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Row */}
      <div className={styles.statsRow}>
        {[
          { icon: <ShoppingBag size={20} />, value: '2 Sources', label: 'Amazon & Flipkart' },
          { icon: <TrendingUp size={20} />, value: 'VADER + TextBlob', label: 'Dual NLP Engine' },
          { icon: <Zap size={20} />, value: 'Real-time', label: 'Live Scraping' },
        ].map((s, i) => (
          <div key={i} className={styles.statCard}>
            <div className={styles.statIcon}>{s.icon}</div>
            <div>
              <div className={styles.statValue}>{s.value}</div>
              <div className={styles.statLabel}>{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Searches */}
      {recent.length > 0 && (
        <div className={styles.recentSection}>
          <div className={styles.sectionHeader}>
            <Clock size={15} />
            <span>Recent Searches</span>
          </div>
          <div className={styles.recentGrid}>
            {recent.slice(0, 6).map(p => (
              <button
                key={p._id}
                className={styles.recentCard}
                onClick={() => navigate(`/dashboard/${p._id}`)}
              >
                <div className={styles.recentName}>{p.product_name}</div>
                <div className={styles.recentMeta}>
                  <span className={styles.sourceTag}>{p.source}</span>
                  <span className={styles.positiveTag}>
                    ▲ {p.summary?.positive_pct || 0}% positive
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
