import React, { useState } from 'react'

// Use environment variable for production API URL (Railway backend)
// In development, use local backend
// Default to Railway production URL if no env var is set (for production builds)
const API_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? 'https://web-production-01d1.up.railway.app/api' : 'http://localhost:5001/api')

function BookList({ books, onEdit, onDelete, viewMode = 'grid' }) {
  const [loadedImages, setLoadedImages] = useState(new Set())
  const [flippedCards, setFlippedCards] = useState(new Set())

  // Helper function to extract Google Books ID from URL
  const getGoogleBooksId = (url) => {
    if (!url) return null
    const match = url.match(/[?&]id=([^&]+)/)
    return match ? match[1] : null
  }

  // Helper function to get cover image URL
  // Use direct URLs when possible (Amazon, Goodreads) to avoid proxy latency
  // Only use proxy for Google Books URLs that may have CORS issues
  const getCoverProxyUrl = (coverUrl, googleBooksId) => {
    if (!coverUrl || !coverUrl.startsWith('http')) return coverUrl
    
    // Check if it's a Google Books URL - these may have CORS issues, use proxy
    const isGoogleBooksUrl = coverUrl.includes('books.google.com') || 
                             coverUrl.includes('googleapis.com') ||
                             coverUrl.includes('googleusercontent.com')
    
    // For non-Google Books URLs (Amazon, Goodreads, etc.), use direct URL
    // These typically don't have CORS restrictions and will load much faster
    if (!isGoogleBooksUrl) {
      return coverUrl
    }
    
    // For Google Books URLs, use proxy only if needed
    // Create a simple hash from the URL for cache-busting
    let hash = 0
    for (let i = 0; i < coverUrl.length; i++) {
      const char = coverUrl.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32bit integer
    }
    const urlHash = Math.abs(hash).toString(36).slice(0, 10)
    
    // Use proxy for Google Books URLs
    if (googleBooksId) {
      return `${API_URL}/books/cover-proxy?book_id=${encodeURIComponent(googleBooksId)}&url=${encodeURIComponent(coverUrl)}&_cb=${urlHash}`
    }
    return `${API_URL}/books/cover-proxy?url=${encodeURIComponent(coverUrl)}&_cb=${urlHash}`
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

    // Handle "Month-YY" format (e.g., "April-08" -> "Apr 2008")
    if (dateRead.includes('-')) {
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

  if (viewMode === 'list') {
    return (
      <div className="film-list-view">
        {books.map(book => (
          <div key={book.id} className="film-row">
            {book.cover_url && (
              <img
                src={book.cover_url.startsWith('http') ? getCoverProxyUrl(book.cover_url, book.google_books_id) : book.cover_url}
                alt={`${book.book_name} cover`}
                className="film-poster-small"
                loading="lazy"
                onError={(e) => {
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
        ))}
      </div>
    )
  }

  return (
    <div className="film-list">
      {books.map(book => {
        const isFlipped = flippedCards.has(book.id)
        return (
          <div key={book.id} className={`film-card-container ${isFlipped ? 'flipped' : ''}`}>
            <div className="film-card-flipper">
              {/* FRONT OF CARD */}
              <div className="film-card film-card-front" onClick={() => toggleFlip(book.id)} onDoubleClick={() => toggleFlip(book.id)}>
                <div className="poster-container">
                  {book.cover_url && book.cover_url !== 'PLACEHOLDER' ? (
                    <>
                      {!loadedImages.has(book.id) && <div className="poster-skeleton"></div>}
                      <img
                        src={getCoverProxyUrl(book.cover_url, book.google_books_id)}
                        alt={`${book.book_name} cover`}
                        className={`film-poster ${loadedImages.has(book.id) ? 'loaded' : ''}`}
                        loading="lazy"
                        onLoad={() => handleImageLoad(book.id)}
                        onError={(e) => {
                          console.error(`Failed to load cover for ${book.book_name}:`, book.cover_url);
                          console.error(`Proxy URL was: ${getCoverProxyUrl(book.cover_url, book.google_books_id)}`);
                          console.error(`API_URL is: ${API_URL}`);
                          e.target.style.display = 'none';
                        }}
                        onLoadStart={() => {
                          // Debug: log what URL is being loaded
                          if (book.book_name === 'The Right Stuff' || book.book_name === 'Animal Farm' || book.book_name === 'Confessions of an Advertising Man') {
                            console.log(`Loading ${book.book_name}:`, {
                              cover_url: book.cover_url,
                              proxy_url: getCoverProxyUrl(book.cover_url, book.google_books_id)
                            });
                          }
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
                  {book.cover_url && book.cover_url !== 'PLACEHOLDER' && (
                    <img
                      src={book.cover_url.startsWith('http') ? getCoverProxyUrl(book.cover_url, book.google_books_id) : book.cover_url}
                      alt={`${book.book_name} cover`}
                      className="poster-thumbnail"
                      onError={(e) => {
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
                      {book.year && <span>Read: {book.year}</span>}
                      {book.pages && <span>• {book.pages} pages</span>}
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
                    {book.type && (
                      <div className="detail-row">
                        <span className="detail-label">Type:</span>
                        <span className="detail-value">{book.type}</span>
                      </div>
                    )}
                    {book.form && (
                      <div className="detail-row">
                        <span className="detail-label">Form:</span>
                        <span className="detail-value">{book.form}</span>
                      </div>
                    )}
                    {book.pages && (
                      <div className="detail-row">
                        <span className="detail-label">Pages:</span>
                        <span className="detail-value">{book.pages}</span>
                      </div>
                    )}
                    {book.year_written && (
                      <div className="detail-row">
                        <span className="detail-label">Written:</span>
                        <span className="detail-value">{book.year_written}</span>
                      </div>
                    )}
                  </div>
                )}

                {book.details_commentary && (
                  <div className="card-back-commentary">
                    <span className="commentary-label">Notes:</span>
                    <p className="commentary-text">{book.details_commentary}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default BookList

