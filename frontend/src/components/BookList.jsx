import React, { useState } from 'react'

// Use environment variable for production API URL (Railway backend)
// In development, use local backend
// Default to Railway production URL if no env var is set (for production builds)
const API_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? 'https://web-production-01d1.up.railway.app/api' : 'http://localhost:5001/api')

function BookList({ books, onEdit, onDelete, viewMode = 'grid' }) {
  const [loadedImages, setLoadedImages] = useState(new Set())
  const [flippedCards, setFlippedCards] = useState(new Set())
  const [thoughtsModal, setThoughtsModal] = useState(null) // Store the book whose thoughts modal is open

  // Helper function to extract Google Books ID from URL
  const getGoogleBooksId = (url) => {
    if (!url) return null
    const match = url.match(/[?&]id=([^&]+)/)
    return match ? match[1] : null
  }

  const handleImageLoad = (bookId) => {
    setLoadedImages(prev => new Set([...prev, bookId]))
  }

  const toggleFlip = (bookId) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev)
      if (newSet.has(bookId)) {
        newSet.delete(bookId)
      } else {
        newSet.add(bookId)
      }
      return newSet
    })
  }

  // Helper function to format date as "Jan 1, 2010"
  const formatDate = (dateRead) => {
    if (!dateRead) return null

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    // Parse MM/DD/YYYY format
    if (dateRead.includes('/')) {
      const parts = dateRead.split('/')
      if (parts.length === 3) {
        const month = parseInt(parts[0]) - 1
        const day = parseInt(parts[1])
        const year = parseInt(parts[2])
        return `${months[month]} ${day}, ${year}`
      }
    }

    // Parse YYYY-MM-DD format (e.g., "2025-01-03" -> "Jan 3, 2025")
    if (dateRead.includes('-') && dateRead.length >= 10) {
      const parts = dateRead.split('-')
      if (parts.length === 3 && parts[0].length === 4) {
        const year = parseInt(parts[0])
        const month = parseInt(parts[1]) - 1
        const day = parseInt(parts[2])
        if (month >= 0 && month < 12 && day > 0 && day <= 31) {
          return `${months[month]} ${day}, ${year}`
        }
      }
    }

    // Handle "Month-YY" format (e.g., "April-08" -> "Apr 2008")
    if (dateRead.includes('-') && dateRead.length <= 10) {
      const parts = dateRead.split('-')
      if (parts.length === 2) {
        const monthName = parts[0]
        const yearPart = parts[1]

        // Find month abbreviation
        const monthIndex = monthNames.findIndex(m => m === monthName)
        if (monthIndex !== -1) {
          // Convert 2-digit year to 4-digit (e.g., "07" -> "2007", "98" -> "1998")
          const year = parseInt(yearPart)
          const fullYear = year < 50 ? `20${yearPart.padStart(2, '0')}` : `19${yearPart.padStart(2, '0')}`
          return `${months[monthIndex]} ${fullYear}`
        }
      }
    }

    // If it's already in a non-date format, return as-is
    return dateRead
  }

  if (books.length === 0) {
    return (
      <div className="empty-state">
        <p>Nope, nothing here!</p>
        <p className="empty-state-hint">Either you're searching wrong or James hasn't read the book :)</p>
      </div>
    )
  }

  // Helper function to get image URL - simplified like films
  const getImageUrl = (coverUrl, googleBooksId) => {
    if (!coverUrl || coverUrl === 'PLACEHOLDER') return null
    if (!coverUrl.startsWith('http')) return null
    
    // For Google Books URLs with ID, use stable publisher URL format
    if (googleBooksId && (coverUrl.includes('books.google.com') || coverUrl.includes('googleapis.com') || coverUrl.includes('googleusercontent.com'))) {
      return `https://books.google.com/books/publisher/content/images/frontcover/${googleBooksId}?fife=w480-h690`
    }
    
    // For all other URLs, use directly (like films do)
    return coverUrl
  }

  if (viewMode === 'list') {
    return (
      <div className="film-list-view">
        {books.map((book, index) => {
          const imageUrl = getImageUrl(book.cover_url, book.google_books_id)
          const shouldLoadEagerly = index < 10
          const shouldPrioritize = index < 30 // First 30 get priority hints
          
          return (
            <div key={book.id} className="film-row">
              {imageUrl && (
                <img
                  src={imageUrl}
                  alt={`${book.book_name} cover`}
                  className="film-poster-small"
                  loading={shouldLoadEagerly ? "eager" : "lazy"}
                  fetchPriority={shouldLoadEagerly ? "high" : (shouldPrioritize ? "auto" : "low")}
                  onError={(e) => {
                    // Try proxy as fallback for Google Books URLs
                    const isGoogleBooksUrl = book.cover_url && (
                      book.cover_url.includes('books.google.com') || 
                      book.cover_url.includes('googleapis.com') ||
                      book.cover_url.includes('googleusercontent.com')
                    )
                    
                    if (isGoogleBooksUrl && !e.target.src.includes('/books/cover-proxy')) {
                      let hash = 0
                      for (let i = 0; i < book.cover_url.length; i++) {
                        const char = book.cover_url.charCodeAt(i)
                        hash = ((hash << 5) - hash) + char
                        hash = hash & hash
                      }
                      const urlHash = Math.abs(hash).toString(36).slice(0, 10)
                      const proxyUrl = book.google_books_id
                        ? `${API_URL}/books/cover-proxy?book_id=${encodeURIComponent(book.google_books_id)}&url=${encodeURIComponent(book.cover_url)}&_cb=${urlHash}`
                        : `${API_URL}/books/cover-proxy?url=${encodeURIComponent(book.cover_url)}&_cb=${urlHash}`
                      
                      e.target.src = proxyUrl
                      return
                    }
                    
                    e.target.style.display = 'none';
                  }}
                />
              )}
            <div className="film-row-content">
              <h3>{book.book_name}</h3>
              {book.author && (
                <div className="film-row-author">by {book.author}</div>
              )}
              <div className="film-row-bottom">
                {book.year && (
                  <span className="meta-item">Read: {book.year}</span>
                )}
                {book.pages && (
                  <span className="meta-item">{book.pages} pages</span>
                )}
              </div>
            </div>
              {book.j_rayting && (
                <div className="rating-box-list">
                  <span className="rating">{book.j_rayting}</span>
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="film-list">
      {books.map((book, index) => {
        const isFlipped = flippedCards.has(book.id)
        // Prioritize first 10 images with eager loading, next 20 get priority hints
        const shouldLoadEagerly = index < 10
        const shouldPrioritize = index < 30 // First 30 get priority hints
        const imageUrl = getImageUrl(book.cover_url, book.google_books_id)
        
        return (
          <div key={book.id} className={`film-card-container ${isFlipped ? 'flipped' : ''}`}>
            <div className="film-card-flipper">
              {/* FRONT OF CARD */}
              <div className="film-card film-card-front" onClick={() => toggleFlip(book.id)} onDoubleClick={() => toggleFlip(book.id)}>
                <div className="poster-container">
                  {imageUrl ? (
                    <>
                      {!loadedImages.has(book.id) && <div className="poster-skeleton"></div>}
                      <img
                        src={imageUrl}
                        alt={`${book.book_name} cover`}
                        className={`film-poster ${loadedImages.has(book.id) ? 'loaded' : ''}`}
                        loading={shouldLoadEagerly ? "eager" : "lazy"}
                        fetchPriority={shouldLoadEagerly ? "high" : (shouldPrioritize ? "auto" : "low")}
                        onLoad={() => handleImageLoad(book.id)}
                        onError={(e) => {
                          // If direct URL failed and it's a Google Books URL, try proxy
                          const isGoogleBooksUrl = book.cover_url && (
                            book.cover_url.includes('books.google.com') || 
                            book.cover_url.includes('googleapis.com') ||
                            book.cover_url.includes('googleusercontent.com')
                          )
                          
                          if (isGoogleBooksUrl && !e.target.src.includes('/books/cover-proxy')) {
                            // Create proxy URL as fallback
                            let hash = 0
                            for (let i = 0; i < book.cover_url.length; i++) {
                              const char = book.cover_url.charCodeAt(i)
                              hash = ((hash << 5) - hash) + char
                              hash = hash & hash
                            }
                            const urlHash = Math.abs(hash).toString(36).slice(0, 10)
                            const proxyUrl = book.google_books_id
                              ? `${API_URL}/books/cover-proxy?book_id=${encodeURIComponent(book.google_books_id)}&url=${encodeURIComponent(book.cover_url)}&_cb=${urlHash}`
                              : `${API_URL}/books/cover-proxy?url=${encodeURIComponent(book.cover_url)}&_cb=${urlHash}`
                            
                            e.target.src = proxyUrl
                            return
                          }
                          
                          // If proxy also fails or not a Google Books URL, hide image
                          e.target.style.display = 'none';
                        }}
                      />
                    </>
                  ) : (
                    <div className="poster-placeholder">
                      <p>Sorry, too obscure to pull a cover</p>
                    </div>
                  )}
                </div>

                <div className="film-content book-content">
                  <div className="film-info-container">
                    <div className="film-info-left-column book-info-left-column">
                      <div className="book-title-group">
                        <h3 className={`film-title ${book.book_name && book.book_name.length > 25 ? 'film-title-long' : ''}`}>
                          {book.book_name}
                        </h3>
                        {book.author && (
                          <div className="book-author-inline">by {book.author}</div>
                        )}
                      </div>
                      <div className="film-metadata book-metadata">
                        {book.year_written && (
                          <span className="info-item">{book.year_written}</span>
                        )}
                        {book.pages && (
                          <span className="info-item">{book.pages} pages</span>
                        )}
                      </div>
                    </div>
                    {book.j_rayting && (
                      <div className="rating-box">
                        <span className="rating">{book.j_rayting}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* BACK OF CARD */}
              <div className="film-card-back" onClick={() => toggleFlip(book.id)} onDoubleClick={() => toggleFlip(book.id)}>
                <button className="close-btn" onClick={(e) => { e.stopPropagation(); toggleFlip(book.id); }}>✕</button>

                <div className="card-back-header">
                  {imageUrl && (
                    <img
                      src={imageUrl}
                      alt={`${book.book_name} cover`}
                      className="poster-thumbnail"
                      loading="lazy"
                      fetchPriority={shouldPrioritize ? "auto" : "low"}
                      onError={(e) => {
                        // Try proxy as fallback for Google Books URLs
                        const isGoogleBooksUrl = book.cover_url && (
                          book.cover_url.includes('books.google.com') || 
                          book.cover_url.includes('googleapis.com') ||
                          book.cover_url.includes('googleusercontent.com')
                        )
                        
                        if (isGoogleBooksUrl && !e.target.src.includes('/books/cover-proxy')) {
                          let hash = 0
                          for (let i = 0; i < book.cover_url.length; i++) {
                            const char = book.cover_url.charCodeAt(i)
                            hash = ((hash << 5) - hash) + char
                            hash = hash & hash
                          }
                          const urlHash = Math.abs(hash).toString(36).slice(0, 10)
                          const proxyUrl = book.google_books_id
                            ? `${API_URL}/books/cover-proxy?book_id=${encodeURIComponent(book.google_books_id)}&url=${encodeURIComponent(book.cover_url)}&_cb=${urlHash}`
                            : `${API_URL}/books/cover-proxy?url=${encodeURIComponent(book.cover_url)}&_cb=${urlHash}`
                          
                          e.target.src = proxyUrl
                          return
                        }
                        
                        e.target.style.display = 'none';
                      }}
                    />
                  )}
                  <div className="header-text">
                    <h3 className="film-title-back">{book.book_name}</h3>
                    {book.author && (
                      <div className="book-author-back">by {book.author}</div>
                    )}
                    <div className="year-duration">
                      {book.year_written && book.pages && (
                        <span>{book.year_written}   {book.pages} pages</span>
                      )}
                      {book.year_written && !book.pages && (
                        <span>{book.year_written}</span>
                      )}
                      {!book.year_written && book.pages && (
                        <span>{book.pages} pages</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="card-back-metrics">
                  {book.j_rayting && (
                    <div className="metric-item">
                      <span className="metric-label">J-Rayting:</span>
                      <span className="metric-value with-rating-box">{book.j_rayting}</span>
                    </div>
                  )}
                </div>

                {!book.date_read && !book.type && !book.form ? (
                  <div className="card-back-details no-data">
                    James read before tracking started!
                  </div>
                ) : (
                  <div className="card-back-details">
                    {book.date_read && (
                      <div className="detail-row">
                        <span className="detail-label">Read:</span>
                        <span className="detail-value">{formatDate(book.date_read)}</span>
                      </div>
                    )}
                    {book.form && (
                      <div className="detail-row">
                        <span className="detail-label">Format:</span>
                        <span className="detail-value">{book.form}</span>
                      </div>
                    )}
                    {book.type && (
                      <div className="detail-row">
                        <span className="detail-label">Type:</span>
                        <span className="detail-value">{book.type}</span>
                      </div>
                    )}
                    {book.details_commentary && (
                      <div className="detail-row">
                        <span className="detail-label">Thoughts:</span>
                        <span className="detail-value">
                          <button 
                            onClick={() => setThoughtsModal(book.id)}
                            style={{ 
                              background: 'none', 
                              border: 'none', 
                              color: 'inherit', 
                              textDecoration: 'underline', 
                              cursor: 'pointer',
                              padding: 0,
                              font: 'inherit'
                            }}
                          >
                            Click Here
                          </button>
                        </span>
                      </div>
                    )}
                    {book.notion_link ? (
                      <div className="detail-row">
                        <span className="detail-label">Notion note:</span>
                        <span className="detail-value">
                          <a href={book.notion_link} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit', textDecoration: 'underline' }}>
                            Open
                          </a>
                        </span>
                      </div>
                    ) : (
                      <div className="detail-row">
                        <span className="detail-label">Notion note:</span>
                        <span className="detail-value">Not Available</span>
                      </div>
                    )}
                  </div>
                )}

              </div>
            </div>
          </div>
        )
      })}

      {/* Thoughts Modal */}
      {thoughtsModal && (() => {
        const book = books.find(b => b.id === thoughtsModal)
        if (!book || !book.details_commentary) return null
        return (
          <div 
            className="thoughts-modal-overlay"
            onClick={() => setThoughtsModal(null)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.8)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              padding: '20px'
            }}
          >
            <div 
              className="thoughts-modal-content"
              onClick={(e) => e.stopPropagation()}
              style={{
                background: '#1c1c1c',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                padding: '24px',
                maxWidth: '600px',
                maxHeight: '80vh',
                overflow: 'auto',
                color: '#e0e0e0'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ color: '#fff', fontSize: '1.2rem', fontWeight: 600 }}>
                  {book.book_name}
                </h3>
                <button
                  onClick={() => setThoughtsModal(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#e0e0e0',
                    fontSize: '24px',
                    cursor: 'pointer',
                    padding: '0',
                    width: '30px',
                    height: '30px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  ✕
                </button>
              </div>
              <div style={{ color: '#e0e0e0', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                {book.details_commentary}
              </div>
            </div>
          </div>
        )
      })()}
    </div>
  )
}

export default BookList

