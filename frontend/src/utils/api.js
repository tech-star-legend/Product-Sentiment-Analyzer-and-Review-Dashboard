import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s for scraping
  headers: { 'Content-Type': 'application/json' }
})

export const searchProduct = (query, source = 'amazon', maxReviews = 20) =>
  api.post('/api/search', { query, source, max_reviews: maxReviews })

export const getProduct = (productId) =>
  api.get(`/api/product/${productId}`)

export const getRecentSearches = () =>
  api.get('/api/recent')

export const getWordFrequency = (productId) =>
  api.get(`/api/wordfreq/${productId}`)

export const healthCheck = () =>
  api.get('/api/health')

export default api
