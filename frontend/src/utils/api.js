import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes — enough for Render cold start
  headers: { 'Content-Type': 'application/json' }
})

export const searchProduct = (query, source = 'amazon', maxReviews = 5) =>
  api.post('/api/search', { query, source, max_reviews: maxReviews })

export const getProduct = (productId) =>
  api.get(`/api/product/${productId}`)

export const getRecentSearches = () =>
  api.get('/api/recent', { timeout: 10000 }) // shorter timeout for recent

export const getWordFrequency = (productId) =>
  api.get(`/api/wordfreq/${productId}`)

export const healthCheck = () =>
  api.get('/api/health', { timeout: 60000 })

export default api
