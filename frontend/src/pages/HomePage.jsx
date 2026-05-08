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

const LOADING_MESSAGES = [
  '⏳ Waking up server (first request takes ~30 seconds)...',
  '🔄 Server is starting up, please wait...',
  '📡 Connecting to backend...',
  '🔍 Scraping reviews & running sentiment analysis...',
  '🧠 Analyzing sentiment with VADER + TextBlob...',
  '📊 Almost done, preparing your results...',
]

export default function HomePage() {
  const [query, setQuery] = useState('')
  const [source, setSource] = useState('amazon')
  const [maxReviews, setMaxReviews] = useState(20)
  const [loading, setLoading] = useState(false)
  const [loadingMsg, setLoadingMsg] = useState('')
  const [error, setError] = useState(null)
  const [recent, setRecent] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    getRecentSearches()
      .then(r => setRecent(r.data.recent || []))
      .catch(() => {})
  }, [])

  // Cycle through loading messages
  useEffect(() => {
    if (!loading) return
    let i = 0
    setLoadingMsg(LOADING_MESSAGES[0])
    const interval = setInterval(() => {
      i = (i + 1) % LOADING_MESSAGES.length
      setLoadingMsg(LOADING_MESSAGES[i])
    }, 5000)
    return () => clearInterval(interval)
  }, [loading])

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await searchProduct(query, source, maxReviews)
      navigate(`/dashboard/${res.data.product_id}`, { state: res.data })
    } catch (err) {
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        setError('Server is taking too long to respond. This happens when the server was sleeping — please try again, it should be awake now!')
      } else {
        setError(err.response?.data?.error || 'Search failed. Please try again in a few seconds.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
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

            <select value={source} onChange={e => setSource(e.target.value)}
              className={styles.select} disabled={loading}>
              {SOURCES.map(s => (
                <option key={s.value} value={s.value}>{s.emoji} {s.label}</option>
              ))}
            </select>

            <select value={maxReviews} onChange={e => setMaxReviews(Number(e.target.value))}
              className={styles.select} disabled={loading}>
              <option value={10}>10 reviews</option>
              <option value={20}>20 reviews</option>
              <option value={30}>30 reviews</option>
              <option value={50}>50 reviews</option>
            </select>

            <button type="submit" className={styles.btn} disabled={loading || !query.trim()}>
              {loading ? <span className={styles.spinner} /> : <><Search size={16} />Analyze</>}
            </button>
          </div>

          {error && <div className={styles.error}>{error}</div>}

          {loading && (
            <div className={styles.loadingBox}>
              <span className={styles.spinner} />
              <span>{loadingMsg}</span>
            </div>
          )}
        </form>

        {/* Cold start notice */}
        <div className={styles.notice}>
          💡 First request may take up to 30 seconds — free server wakes up on demand
        </div>

        <div className={styles.suggestions}>
          <span className={styles.suggestLabel}>Try:</span>
          {SUGGESTIONS.map(s => (
            <button key={s} className={styles.chip} onClick={() => setQuery(s)}>{s}</button>
          ))}
        </div>
      </div>

      <div className={styles.statsRow}>
        {[
          { icon: <ShoppingBag size={20} />, value: '2 Sources', label: 'Amazon & Flipkart' },
          { icon: <TrendingUp size={20} />, value: 'VADER + TextBlob', label: 'Dual NLP Engine' },
          { icon: <Zap size={20} />, value: 'Real-time', label: 'Live Analysis' },
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

      {recent.length > 0 && (
        <div className={styles.recentSection}>
          <div className={styles.sectionHeader}>
            <Clock size={15} />
            <span>Recent Searches</span>
          </div>
          <div className={styles.recentGrid}>
            {recent.slice(0, 6).map(p => (
              <button key={p._id} className={styles.recentCard}
                onClick={() => navigate(`/dashboard/${p._id}`)}>
                <div className={styles.recentName}>{p.product_name}</div>
                <div className={styles.recentMeta}>
                  <span className={styles.sourceTag}>{p.source}</span>
                  <span className={styles.positiveTag}>▲ {p.summary?.positive_pct || 0}% positive</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
