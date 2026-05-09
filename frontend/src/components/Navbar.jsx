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
            <Activity size={16} strokeWidth={2.5} />
          </div>
          <span className={styles.logoText}>
            Sentiment<span>Scope</span>
          </span>
        </Link>

        <div className={styles.links}>
          <Link to="/" className={`${styles.link} ${pathname === '/' ? styles.active : ''}`}>
            <Search size={14} />
            <span>Search</span>
          </Link>
          <Link to="/history" className={`${styles.link} ${pathname === '/history' ? styles.active : ''}`}>
            <History size={14} />
            <span>History</span>
          </Link>
        </div>

        <div className={styles.badge}>
          <span className={styles.dot} />
          Live
        </div>
      </div>
    </nav>
  )
}
