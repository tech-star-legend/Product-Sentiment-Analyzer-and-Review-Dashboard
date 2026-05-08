import { Link, useLocation } from 'react-router-dom'
import { Activity, History, Search } from 'lucide-react'
import styles from './Navbar.module.css'

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <nav className={styles.nav}>
      <div className={styles.inner}>
        <Link to="/" className={styles.logo}>
          <div className={styles.logoIcon}>
            <Activity size={18} strokeWidth={2.5} />
          </div>
          <span className={styles.logoText}>SentimentScope</span>
        </Link>

        <div className={styles.links}>
          <Link to="/" className={`${styles.link} ${pathname === '/' ? styles.active : ''}`}>
            <Search size={15} />
            <span>Search</span>
          </Link>
          <Link to="/history" className={`${styles.link} ${pathname === '/history' ? styles.active : ''}`}>
            <History size={15} />
            <span>History</span>
          </Link>
        </div>

        <div className={styles.badge}>
          <span className={styles.dot} />
          Live Analysis
        </div>
      </div>
    </nav>
  )
}
