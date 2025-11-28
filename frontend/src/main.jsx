import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Admin from './Admin.jsx'
import BooksAdmin from './BooksAdmin.jsx'
import BooksApp from './BooksApp.jsx'

// Check if we're on the /books path
// This checks both the current pathname and the full URL to handle Vercel rewrites
const currentPath = window.location.pathname
const isBooksPath = currentPath.startsWith('/books') || currentPath === '/admin' && document.referrer.includes('/books')

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
