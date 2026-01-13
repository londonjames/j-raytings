import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import ItemsApp from './ItemsApp.jsx'
import Admin from './Admin.jsx'
import BooksAdmin from './BooksAdmin.jsx'
import ShowsAdmin from './ShowsAdmin.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import { filmsConfig } from './config/filmsConfig.js'
import { booksConfig } from './config/booksConfig.js'
import { showsConfig } from './config/showsConfig.js'

// Check if we're on the /books or /shows path
// Handle Vercel rewrites: /books/admin, /films/admin, /shows/admin get rewritten, so we check the full URL
const currentPath = window.location.pathname
const fullUrl = window.location.href
// Check multiple ways to detect books path (handles Vercel rewrites)
const isBooksPath = currentPath.startsWith('/books') ||
                   fullUrl.includes('/books/') ||
                   fullUrl.includes('/books/admin') ||
                   fullUrl.includes('/books?') ||
                   (currentPath === '/admin' && fullUrl.includes('books'))
// Shows path detection (for when /shows/admin gets rewritten)
const isShowsPath = currentPath.startsWith('/shows') ||
                    fullUrl.includes('/shows/') ||
                    fullUrl.includes('/shows/admin') ||
                    fullUrl.includes('/shows?') ||
                    (currentPath === '/admin' && fullUrl.includes('shows'))
// Films path detection (for when /films/admin gets rewritten)
const isFilmsPath = currentPath.startsWith('/films') ||
                    fullUrl.includes('/films/') ||
                    fullUrl.includes('/films/admin') ||
                    (currentPath === '/admin' && fullUrl.includes('films') && !fullUrl.includes('books') && !fullUrl.includes('shows'))

// Determine basename - prioritize books, then shows, then films, default to films
const basename = isBooksPath ? '/books' : (isShowsPath ? '/shows' : (isFilmsPath ? '/films' : '/films'))

// Select config based on path
const config = isBooksPath ? booksConfig : (isShowsPath ? showsConfig : filmsConfig)

// Debug logging
console.log('Routing debug:', {
  currentPath,
  fullUrl,
  isBooksPath,
  isShowsPath,
  isFilmsPath,
  basename,
  config: config.type
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter basename={basename}>
        <Routes>
          <Route path="/" element={<ItemsApp config={config} />} />
          <Route path="/admin" element={isBooksPath ? <BooksAdmin /> : (isShowsPath ? <ShowsAdmin /> : <Admin />)} />
          <Route path="/analytics" element={<ItemsApp config={config} />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
