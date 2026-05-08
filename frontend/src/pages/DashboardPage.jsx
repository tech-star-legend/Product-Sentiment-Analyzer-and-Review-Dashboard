import { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, RefreshCw, Star, ThumbsUp, ThumbsDown, Minus, Package } from 'lucide-react'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts'
import { getProduct, getWordFrequency } from '../utils/api'
import styles from './DashboardPage.module.css'

const COLORS = {
  positive: '#34d399',
  negative: '#f87171',
  neutral: '#fbbf24'
}

const SENTIMENT_ICON = {
  positive: <ThumbsUp size={13} />,
  negative: <ThumbsDown size={13} />,
  neutral: <Minus size={13} />
}

export default function DashboardPage() {
  const { productId } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()

  const [data, setData] = useState(state || null)
  const [wordFreq, setWordFreq] = useState(null)
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date')
  const [loading, setLoading] = useState(!state)
  const [tab, setTab] = useState('overview')

  useEffect(() => {
    if (!data) {
      setLoading(true)
      getProduct(productId)
        .then(r => setData({ ...r.data.product, reviews: r.data.reviews, summary: r.data.product.summary }))
        .catch(() => navigate('/'))
        .finally(() => setLoading(false))
    }
  }, [productId])

  useEffect(() => {
    if (productId) {
      getWordFrequency(productId).then(r => setWordFreq(r.data)).catch(() => {})
    }
  }, [productId])

  if (loading) return <LoadingSkeleton />
  if (!data) return null

  const { product_name, source, summary, reviews = [], cached } = data

  // Filter + sort
  const filtered = reviews
    .filter(r => filter === 'all' || r.sentiment === filter)
    .sort((a, b) => {
      if (sortBy === 'score') return b.score - a.score
      if (sortBy === 'rating') return b.rating - a.rating
      return 0
    })

  const pieData = [
    { name: 'Positive', value: summary.positive },
    { name: 'Negative', value: summary.negative },
    { name: 'Neutral', value: summary.neutral },
  ]

  // Rating distribution
  const ratingDist = [1,2,3,4,5].map(r => ({
    rating: `${r}★`,
    count: reviews.filter(rev => Math.round(rev.rating) === r).length
  }))

  // Radar chart data
  const radarData = [
    { subject: 'Positive %', value: summary.positive_pct },
    { subject: 'Avg Score', value: ((summary.avg_score + 1) / 2 * 100) },
    { subject: 'Volume', value: Math.min(summary.total / 50 * 100, 100) },
    { subject: 'Confidence', value: reviews.length ? reviews.reduce((a, r) => a + (r.confidence || 0), 0) / reviews.length * 100 : 0 },
    { subject: 'Neutral%', value: 100 - summary.positive_pct - summary.negative_pct },
  ]

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/')}>
          <ArrowLeft size={16} /> Back
        </button>
        <div className={styles.productInfo}>
          <div className={styles.productIcon}><Package size={20} /></div>
          <div>
            <h1 className={styles.productName}>{product_name}</h1>
            <div className={styles.productMeta}>
              <span className={styles.sourceChip}>{source}</span>
              <span className={styles.reviewCount}>{summary.total} reviews analyzed</span>
              {cached && <span className={styles.cachedChip}>cached</span>}
            </div>
          </div>
        </div>
        <button className={styles.refreshBtn} onClick={() => navigate('/')}>
          <RefreshCw size={15} /> New Search
        </button>
      </div>

      {/* Summary Cards */}
      <div className={styles.summaryCards}>
        {[
          { label: 'Positive', value: summary.positive, pct: summary.positive_pct, color: 'positive', icon: <ThumbsUp size={18} /> },
          { label: 'Negative', value: summary.negative, pct: summary.negative_pct, color: 'negative', icon: <ThumbsDown size={18} /> },
          { label: 'Neutral', value: summary.neutral, pct: summary.neutral_pct, color: 'neutral', icon: <Minus size={18} /> },
          { label: 'Avg Score', value: summary.avg_score > 0 ? `+${summary.avg_score}` : summary.avg_score, pct: null, color: 'accent', icon: <Star size={18} /> },
        ].map((c, i) => (
          <div key={i} className={`${styles.summaryCard} ${styles[`card_${c.color}`]}`}>
            <div className={styles.cardIcon}>{c.icon}</div>
            <div className={styles.cardValue}>{c.value}</div>
            <div className={styles.cardLabel}>{c.label}</div>
            {c.pct !== null && <div className={styles.cardPct}>{c.pct}%</div>}
          </div>
        ))}
      </div>

      {/* Sentiment Bar */}
      <div className={styles.sentimentBar}>
        <div className={styles.barPos} style={{ width: `${summary.positive_pct}%` }} />
        <div className={styles.barNeu} style={{ width: `${summary.neutral_pct}%` }} />
        <div className={styles.barNeg} style={{ width: `${summary.negative_pct}%` }} />
      </div>
      <div className={styles.barLabels}>
        <span style={{ color: COLORS.positive }}>▌ {summary.positive_pct}% Positive</span>
        <span style={{ color: COLORS.neutral }}>▌ {summary.neutral_pct}% Neutral</span>
        <span style={{ color: COLORS.negative }}>▌ {summary.negative_pct}% Negative</span>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        {['overview', 'reviews', 'wordcloud'].map(t => (
          <button key={t} className={`${styles.tab} ${tab === t ? styles.tabActive : ''}`} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ── */}
      {tab === 'overview' && (
        <div className={styles.chartsGrid}>
          {/* Pie Chart */}
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Sentiment Distribution</h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={70} outerRadius={110}
                  paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}>
                  {pieData.map((entry, index) => (
                    <Cell key={index} fill={Object.values(COLORS)[index]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#16161f', border: '1px solid #1e1e2e', borderRadius: '8px', color: '#f0eff5' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Rating Distribution */}
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Rating Distribution</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={ratingDist} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                <XAxis dataKey="rating" tick={{ fill: '#8b8a9e', fontSize: 12 }} />
                <YAxis tick={{ fill: '#8b8a9e', fontSize: 12 }} />
                <Tooltip contentStyle={{ background: '#16161f', border: '1px solid #1e1e2e', borderRadius: '8px', color: '#f0eff5' }} />
                <Bar dataKey="count" fill="#7c6af5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Radar Chart */}
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Quality Radar</h3>
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#1e1e2e" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#8b8a9e', fontSize: 11 }} />
                <PolarRadiusAxis tick={false} axisLine={false} domain={[0, 100]} />
                <Radar name="Product" dataKey="value" stroke="#7c6af5" fill="#7c6af5" fillOpacity={0.25} />
                <Tooltip contentStyle={{ background: '#16161f', border: '1px solid #1e1e2e', borderRadius: '8px', color: '#f0eff5' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Score Distribution */}
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>Sentiment Score Breakdown</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={[
                { range: '-1.0 to -0.5', count: reviews.filter(r => r.score <= -0.5).length, fill: COLORS.negative },
                { range: '-0.5 to 0', count: reviews.filter(r => r.score > -0.5 && r.score < 0).length, fill: COLORS.neutral },
                { range: '0 to 0.5', count: reviews.filter(r => r.score >= 0 && r.score < 0.5).length, fill: COLORS.neutral },
                { range: '0.5 to 1.0', count: reviews.filter(r => r.score >= 0.5).length, fill: COLORS.positive },
              ]} margin={{ top: 10, right: 10, bottom: 20, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                <XAxis dataKey="range" tick={{ fill: '#8b8a9e', fontSize: 10 }} angle={-15} textAnchor="end" />
                <YAxis tick={{ fill: '#8b8a9e', fontSize: 12 }} />
                <Tooltip contentStyle={{ background: '#16161f', border: '1px solid #1e1e2e', borderRadius: '8px', color: '#f0eff5' }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {[COLORS.negative, COLORS.neutral, COLORS.neutral, COLORS.positive].map((color, i) => (
                    <Cell key={i} fill={color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* ── REVIEWS TAB ── */}
      {tab === 'reviews' && (
        <div className={styles.reviewsSection}>
          <div className={styles.reviewControls}>
            <div className={styles.filterBtns}>
              {['all', 'positive', 'negative', 'neutral'].map(f => (
                <button key={f} className={`${styles.filterBtn} ${filter === f ? styles.filterActive : ''}`}
                  onClick={() => setFilter(f)} style={filter === f && f !== 'all' ? { borderColor: COLORS[f], color: COLORS[f] } : {}}>
                  {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
                  <span className={styles.filterCount}>
                    {f === 'all' ? summary.total : summary[f]}
                  </span>
                </button>
              ))}
            </div>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} className={styles.sortSelect}>
              <option value="date">Sort: Default</option>
              <option value="score">Sort: By Score</option>
              <option value="rating">Sort: By Rating</option>
            </select>
          </div>

          <div className={styles.reviewList}>
            {filtered.map((r, i) => (
              <ReviewCard key={i} review={r} />
            ))}
          </div>
        </div>
      )}

      {/* ── WORD CLOUD TAB ── */}
      {tab === 'wordcloud' && wordFreq && (
        <div className={styles.wordSection}>
          <WordFreqChart title="Most Frequent Words (All Reviews)" data={wordFreq.all} color="#7c6af5" />
          <div className={styles.wordRow}>
            <WordFreqChart title="Positive Reviews" data={wordFreq.positive} color={COLORS.positive} />
            <WordFreqChart title="Negative Reviews" data={wordFreq.negative} color={COLORS.negative} />
          </div>
        </div>
      )}
    </div>
  )
}

function ReviewCard({ review }) {
  const color = COLORS[review.sentiment] || COLORS.neutral
  return (
    <div className={styles.reviewCard}>
      <div className={styles.reviewHeader}>
        <div className={styles.reviewAuthor}>{review.author || 'Anonymous'}</div>
        <div className={styles.reviewRight}>
          <div className={styles.stars}>
            {'★'.repeat(Math.round(review.rating || 0))}{'☆'.repeat(5 - Math.round(review.rating || 0))}
          </div>
          <span className={styles.sentimentBadge} style={{ color, borderColor: color, background: `${color}18` }}>
            {SENTIMENT_ICON[review.sentiment]}
            {review.sentiment}
          </span>
        </div>
      </div>
      {review.title && <div className={styles.reviewTitle}>"{review.title}"</div>}
      <p className={styles.reviewText}>{review.text}</p>
      <div className={styles.reviewFooter}>
        <span className={styles.reviewDate}>{review.date}</span>
        <span className={styles.scoreChip}>score: {review.score > 0 ? '+' : ''}{review.score?.toFixed(3)}</span>
      </div>
    </div>
  )
}

function WordFreqChart({ title, data, color }) {
  if (!data || !data.length) return null
  const max = data[0][1]
  return (
    <div className={styles.chartCard}>
      <h3 className={styles.chartTitle}>{title}</h3>
      <div className={styles.wordList}>
        {data.slice(0, 15).map(([word, count]) => (
          <div key={word} className={styles.wordItem}>
            <span className={styles.wordLabel}>{word}</span>
            <div className={styles.wordBarWrap}>
              <div className={styles.wordBar} style={{ width: `${(count / max) * 100}%`, background: color }} />
            </div>
            <span className={styles.wordCount}>{count}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className={styles.page}>
      <div className={styles.skeletonHeader} />
      <div className={styles.summaryCards}>
        {[1,2,3,4].map(i => <div key={i} className={`${styles.summaryCard} skeleton`} style={{ height: 110 }} />)}
      </div>
      <div className={styles.chartsGrid}>
        {[1,2,3,4].map(i => <div key={i} className={`${styles.chartCard} skeleton`} style={{ height: 300 }} />)}
      </div>
    </div>
  )
}
