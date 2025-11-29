import { useState, useEffect } from 'react'
import BookForm from './BookForm'
import './AdminPanel.css'

// Use environment variable for production API URL (Railway backend)
// In development, use local backend
// Default to Railway production URL if no env var is set (for production builds)
const API_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? 'https://web-production-01d1.up.railway.app/api' : 'http://localhost:5001/api')

function BookAdminPanel({ onLogout }) {
  const handleLogout = () => {
    sessionStorage.removeItem('adminAuthenticated')
    onLogout()
  }
  const [showAddForm, setShowAddForm] = useState(false)
  const [message, setMessage] = useState('')
  const [duplicateWarning, setDuplicateWarning] = useState(null)
  const [books, setBooks] = useState([])
  const [filteredBooks, setFilteredBooks] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [editingBook, setEditingBook] = useState(null)

  // Fetch all books
  const fetchBooks = async () => {
    try {
      // Add cache-busting to ensure fresh data
      const response = await fetch(`${API_URL}/books?_t=${Date.now()}`, {
        cache: 'no-store'
      })
      const data = await response.json()
      // Ensure data is an array
      const booksArray = Array.isArray(data) ? data : []
      // Sort by updated_at (most recently updated first), then by id as fallback
      const sortedData = [...booksArray].sort((a, b) => {
        const aUpdated = a.updated_at ? new Date(a.updated_at) : new Date(0)
        const bUpdated = b.updated_at ? new Date(b.updated_at) : new Date(0)
        if (bUpdated.getTime() !== aUpdated.getTime()) {
          return bUpdated.getTime() - aUpdated.getTime() // Most recent first
        }
        return (b.id || 0) - (a.id || 0) // Fallback to ID
      })
      setBooks(sortedData)
      setFilteredBooks(sortedData)
    } catch (error) {
      console.error('Error fetching books:', error)
      setBooks([])
      setFilteredBooks([])
    }
  }

  // Fetch books on component mount
  useEffect(() => {
    fetchBooks()
  }, [])

  // Filter books based on search
  const handleSearch = (term) => {
    setSearchTerm(term)
    if (!term) {
      setFilteredBooks(books)
    } else {
      const filtered = books.filter(book =>
        book.book_name?.toLowerCase().includes(term.toLowerCase()) ||
        book.author?.toLowerCase().includes(term.toLowerCase()) ||
        book.year?.toString().includes(term)
      )
      setFilteredBooks(filtered)
    }
  }

  const handleSaveBook = async (bookData) => {
    try {
      const url = editingBook
        ? `${API_URL}/books/${editingBook.id}`
        : `${API_URL}/books`

      const method = editingBook ? 'PUT' : 'POST'

      console.log('Saving book:', { id: editingBook?.id, cover_url: bookData.cover_url, method })
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookData)
      })
      
      console.log('Save response:', response.status, response.statusText)

      if (response.ok) {
        const result = await response.json()
        if (editingBook) {
          setMessage('Book updated successfully!')
        } else if (result.metadata_fetched) {
          setMessage('Book added successfully! Metadata (cover, rating) auto-fetched from Google Books.')
        } else {
          setMessage('Book added successfully!')
        }
        setShowAddForm(false)
        setEditingBook(null)
        setDuplicateWarning(null)
        // Longer delay to ensure backend has fully saved the new book
        setTimeout(() => {
          fetchBooks()
        }, 500)
        setTimeout(() => setMessage(''), 5000)
      } else if (response.status === 409) {
        // Duplicate detected
        const result = await response.json()
        setDuplicateWarning(result)
        setMessage('')
      } else {
        // Try to get error message from response
        let errorMessage = 'Error saving book'
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorData.message || errorMessage
        } catch (e) {
          errorMessage = `Error saving book (${response.status}: ${response.statusText})`
        }
        setMessage(errorMessage)
        console.error('Error response:', response.status, errorMessage)
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage(`Error saving book: ${error.message}`)
    }
  }

  const handleEditBook = (book) => {
    setEditingBook(book)
    setShowAddForm(true)
  }

  const handleDeleteBook = async (id) => {
    if (!confirm('Are you sure you want to delete this book?')) return

    try {
      const response = await fetch(`${API_URL}/books/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setMessage('Book deleted successfully!')
        fetchBooks()
        setTimeout(() => setMessage(''), 3000)
      } else {
        setMessage('Error deleting book')
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage(`Error deleting book: ${error.message}`)
    }
  }


  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>Books Admin Panel</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      {message && (
        <div className={`admin-message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {duplicateWarning && (
        <div className="duplicate-warning">
          <h3>Duplicate Book Detected</h3>
          <p>This book may already exist in the database:</p>
          <ul>
            {(duplicateWarning.duplicates || []).map((book, index) => (
              <li key={index}>
                {book.book_name} by {book.author} - {book.cover_url ? 'Has cover' : 'No cover'}
              </li>
            ))}
          </ul>
          <p>Please add a cover URL or other distinguishing information in the form below.</p>
        </div>
      )}

      <div className="admin-content">
        {!showAddForm ? (
          <>
            <div className="admin-actions">
              <button 
                onClick={() => {
                  console.log('Add Book button clicked')
                  setShowAddForm(true)
                  setEditingBook(null)
                }} 
                className="add-film-btn"
              >
                + Add New Book
              </button>
              <a href="/books" className="view-site-btn">View Public Site</a>
            </div>

            <div className="admin-search">
              <input
                type="text"
                placeholder="Search books by title, author, or year..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="search-input"
              />
              <span className="film-count">{filteredBooks.length} book(s)</span>
            </div>

            <div className="admin-film-list">
              {(filteredBooks || []).map(book => (
                <div key={book.id} className="admin-film-item">
                  <div className="film-info">
                    {book.cover_url && book.cover_url !== 'PLACEHOLDER' && (
                      <img 
                        src={book.cover_url.startsWith('http') ? `${API_URL}/books/cover-proxy?book_id=${encodeURIComponent(book.google_books_id || '')}&url=${encodeURIComponent(book.cover_url)}` : book.cover_url}
                        alt={book.book_name} 
                        className="film-thumb"
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                      />
                    )}
                    <div className="film-details">
                      <h3>{book.book_name}</h3>
                      <div className="film-meta">
                        {book.author && <span>Author: {book.author}</span>}
                        {book.year && <span>Year: {book.year}</span>}
                        {book.j_rayting && <span>Rating: {book.j_rayting}</span>}
                        {book.pages && <span>Pages: {book.pages}</span>}
                        {book.cover_url && book.cover_url !== 'PLACEHOLDER' ? (
                          <span style={{ color: '#68d391' }}>Has cover</span>
                        ) : (
                          <span style={{ color: '#fc8181' }}>No cover</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="film-actions">
                    <button onClick={() => handleEditBook(book)} className="edit-btn">
                      Edit
                    </button>
                    <button onClick={() => handleDeleteBook(book.id)} className="delete-btn">
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="admin-form-container">
            <h2>{editingBook ? 'Edit Book' : 'Add New Book'}</h2>
            {showAddForm && (
              <BookForm
                book={editingBook}
                onSave={handleSaveBook}
                onCancel={() => {
                  console.log('Cancel clicked')
                  setShowAddForm(false)
                  setEditingBook(null)
                  setDuplicateWarning(null)
                }}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default BookAdminPanel

