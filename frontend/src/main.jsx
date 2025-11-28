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
// Handle Vercel rewrites: /books/admin gets rewritten to /admin, so we check the full URL
const currentPath = window.location.pathname
const fullUrl = window.location.href
// Check multiple ways to detect books path (handles Vercel rewrites)
const isBooksPath = currentPath.startsWith('/books') || 
                   fullUrl.includes('/books/') || 
                   fullUrl.includes('/books/admin') ||
                   fullUrl.includes('/books?') ||
                   (currentPath === '/admin' && fullUrl.includes('books'))

// Debug logging
console.log('Routing debug:', {
  currentPath,
  fullUrl,
  isBooksPath,
  basename: isBooksPath ? '/books' : '/films'
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter basename={isBooksPath ? '/books' : '/films'}>
        <Routes>
          <Route path="/" element={isBooksPath ? <BooksApp /> : <App />} />
          <Route path="/admin" element={isBooksPath ? <BooksAdmin /> : <Admin />} />
          <Route path="/analytics" element={isBooksPath ? <BooksApp /> : <App />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
