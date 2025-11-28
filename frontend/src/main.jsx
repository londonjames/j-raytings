import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Admin from './Admin.jsx'
import BooksAdmin from './BooksAdmin.jsx'
import BooksApp from './BooksApp.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'

// Check if we're on the /books path
// Handle Vercel rewrites: /books/admin and /films/admin get rewritten, so we check the full URL
const currentPath = window.location.pathname
const fullUrl = window.location.href
// Check multiple ways to detect books path (handles Vercel rewrites)
const isBooksPath = currentPath.startsWith('/books') || 
                   fullUrl.includes('/books/') || 
                   fullUrl.includes('/books/admin') ||
                   fullUrl.includes('/books?') ||
                   (currentPath === '/admin' && fullUrl.includes('books'))
// Films path detection (for when /films/admin gets rewritten)
const isFilmsPath = currentPath.startsWith('/films') ||
                    fullUrl.includes('/films/') ||
                    fullUrl.includes('/films/admin') ||
                    (currentPath === '/admin' && fullUrl.includes('films') && !fullUrl.includes('books'))

// Determine basename - prioritize books, then films, default to films
const basename = isBooksPath ? '/books' : (isFilmsPath ? '/films' : '/films')

// Debug logging
console.log('Routing debug:', {
  currentPath,
  fullUrl,
  isBooksPath,
  isFilmsPath,
  basename
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter basename={basename}>
        <Routes>
          <Route path="/" element={isBooksPath ? <BooksApp /> : <App />} />
          <Route path="/admin" element={isBooksPath ? <BooksAdmin /> : <Admin />} />
          <Route path="/analytics" element={isBooksPath ? <BooksApp /> : <App />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
