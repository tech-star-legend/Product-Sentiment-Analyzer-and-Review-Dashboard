import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, TrendingUp, TrendingDown, Package, ExternalLink } from 'lucide-react'
import { getRecentSearches } from '../utils/api'
import styles from './HistoryPage.module.css'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getRecentSearches()
      .then(r => setHistory(r.data.recent || []))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className={styles.page}>
      <div className={styles.header}><h1>Search History</h1></div>
      <div className={styles.grid}>
        {[1,2,3,4,5,6].map(i => (
          <div key={i} className="skeleton" style={{ height: 160, borderRadius: 12 }} />
        ))}
      </div>
    </div>
  )

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <Clock size={20} />
        <h1>Search History</h1>
        <span className={styles.count}>{history.length} searches</span>
      </div>

      {history.length === 0 ? (
        <div className={styles.empty}>
          <Package size={40} />
          <p>No searches yet. Start by searching for a product!</p>
          <button className={styles.goBtn} onClick={() => navigate('/')}>Search Products</button>
        </div>
      ) : (
        <div className={styles.grid}>
          {history.map(p => {
            const s = p.summary || {}
            const dominant = s.positive_pct > s.negative_pct ? 'positive' : 'negative'
            return (
              <div key={p._id} className={styles.card} onClick={() => navigate(`/dashboard/${p._id}`)}>
                <div className={styles.cardTop}>
                  <div className={styles.sourceTag}>{p.source}</div>
                  <ExternalLink size={14} className={styles.extIcon} />
                </div>
                <div className={styles.name}>{p.product_name}</div>
                <div className={styles.query}>"{p.query}"</div>
                <div className={styles.stats}>
                  <div className={`${styles.stat} ${styles.statPos}`}>
                    <TrendingUp size={13} />
                    <span>{s.positive_pct || 0}%</span>
                  </div>
                  <div className={`${styles.stat} ${styles.statNeg}`}>
                    <TrendingDown size={13} />
                    <span>{s.negative_pct || 0}%</span>
                  </div>
                  <div className={styles.stat}>
                    <span>{s.total || 0} reviews</span>
                  </div>
                </div>
                <div className={styles.miniBar}>
                  <div style={{ width: `${s.positive_pct || 0}%`, background: '#34d399', height: '100%' }} />
                  <div style={{ width: `${s.neutral_pct || 0}%`,  background: '#fbbf24', height: '100%' }} />
                  <div style={{ width: `${s.negative_pct || 0}%`, background: '#f87171', height: '100%' }} />
                </div>
                <div className={styles.dateStr}>
                  {new Date(p.scraped_at * 1000).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
