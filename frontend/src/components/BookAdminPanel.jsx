import { useState, useEffect } from 'react'
import BookForm from './BookForm'
import './AdminPanel.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

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
      const response = await fetch(`${API_URL}/books`)
      const data = await response.json()
      setBooks(data)
      setFilteredBooks(data)
    } catch (error) {
      console.error('Error fetching books:', error)
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

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookData)
      })

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
        fetchBooks()
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

  const handleUpdateCover = async (bookId, bookName, author) => {
    try {
      const response = await fetch(`${API_URL}/admin/books/${bookId}/cover`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          book_name: bookName,
          author: author
        })
      })

      if (response.ok) {
        const result = await response.json()
        setMessage(`Cover updated successfully! ${result.cover_url ? 'New cover URL: ' + result.cover_url.substring(0, 60) + '...' : ''}`)
        fetchBooks()
        setTimeout(() => setMessage(''), 5000)
      } else {
        const errorData = await response.json()
        setMessage(`Error updating cover: ${errorData.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage(`Error updating cover: ${error.message}`)
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
            {duplicateWarning.duplicates.map((book, index) => (
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
              <button onClick={() => setShowAddForm(true)} className="add-film-btn">
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
              {filteredBooks.map(book => (
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
                    <button 
                      onClick={() => handleUpdateCover(book.id, book.book_name, book.author)} 
                      className="edit-btn"
                      title="Update cover from Google Books"
                    >
                      Update Cover
                    </button>
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
            <BookForm
              book={editingBook}
              onSave={handleSaveBook}
              onCancel={() => {
                setShowAddForm(false)
                setEditingBook(null)
                setDuplicateWarning(null)
              }}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default BookAdminPanel

