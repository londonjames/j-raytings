import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Admin from './Admin.jsx'
import BooksAdmin from './BooksAdmin.jsx'
import BooksApp from './BooksApp.jsx'

// Check if we're on the /books path
// Handle Vercel rewrites: /books/admin gets rewritten to /admin, so we check the full URL
const currentPath = window.location.pathname
const fullUrl = window.location.href
const isBooksPath = currentPath.startsWith('/books') || fullUrl.includes('/books/')

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter basename={isBooksPath ? '/books' : '/films'}>
      <Routes>
        <Route path="/" element={isBooksPath ? <BooksApp /> : <App />} />
        <Route path="/admin" element={isBooksPath ? <BooksAdmin /> : <Admin />} />
        <Route path="/analytics" element={isBooksPath ? <BooksApp /> : <App />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
