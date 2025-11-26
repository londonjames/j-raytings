import React, { useState } from 'react'

function FilmList({ films, onEdit, onDelete, viewMode = 'grid' }) {
  const [loadedImages, setLoadedImages] = useState(new Set())
  const [flippedCards, setFlippedCards] = useState(new Set())

  const handleImageLoad = (filmId) => {
    setLoadedImages(prev => new Set([...prev, filmId]))
  }

  const toggleFlip = (filmId) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev)
      if (newSet.has(filmId)) {
        newSet.delete(filmId)
      } else {
        newSet.add(filmId)
      }
      return newSet
    })
  }

  // Helper function to format date as "Jan 1, 2010"
  const formatDate = (dateSeen) => {
    if (!dateSeen) return null

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    // Parse MM/DD/YYYY format
    if (dateSeen.includes('/')) {
      const parts = dateSeen.split('/')
      if (parts.length === 3) {
        const month = parseInt(parts[0]) - 1
        const day = parseInt(parts[1])
        const year = parseInt(parts[2])
        return `${months[month]} ${day}, ${year}`
      }
    }

    // Handle "Month-YY" format (e.g., "April-08" -> "Apr 2008")
    if (dateSeen.includes('-')) {
      const parts = dateSeen.split('-')
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

    // If it's already in a non-date format (like "Theatre", "1990s", etc.), return as-is
    return dateSeen
  }

  // Helper function to format film titles
  const formatTitle = (title) => {
    if (!title) return ''

    // Check if title has a comma (e.g., "Godfather, The")
    if (title.includes(',')) {
      const parts = title.split(',').map(s => s.trim())
      if (parts.length === 2) {
        // Reverse it: "Godfather, The" -> "The Godfather"
        return `${parts[1]} ${parts[0]}`
      }
    }
    return title
  }

  // Helper function to format year watched from date_seen
  const formatYearWatched = (dateSeen) => {
    if (!dateSeen) return ''

    // Check if it's already in decade format (e.g., "1990s", "2000s")
    if (dateSeen.includes('s')) {
      return dateSeen
    }

    // Extract year from date format (e.g., "12/25/2020" -> "2020" or "February-07" -> "2007")
    if (dateSeen.includes('/')) {
      const parts = dateSeen.split('/')
      if (parts.length === 3) {
        return parts[2] // Return the year part
      }
    }

    // Handle formats like "February-07" or "March-12"
    if (dateSeen.includes('-')) {
      const parts = dateSeen.split('-')
      if (parts.length === 2) {
        const yearPart = parts[1]
        // Convert 2-digit year to 4-digit (e.g., "07" -> "2007", "12" -> "2012")
        const year = parseInt(yearPart)
        return year < 50 ? `20${yearPart}` : `19${yearPart}`
      }
    }

    return dateSeen
  }

  // Helper function to format format field (capitalize VHS and DVD)
  const formatFormat = (format) => {
    if (!format) return ''
    
    // Capitalize VHS and DVD regardless of case (case-insensitive replacement)
    let formatted = format
    formatted = formatted.replace(/\bvhs\b/gi, 'VHS')
    formatted = formatted.replace(/\bdvd\b/gi, 'DVD')
    
    return formatted
  }

  if (films.length === 0) {
    return (
      <div className="empty-state">
        <p>Nope, nothing here!</p>
        <p className="empty-state-hint">Either you're searching wrong or James hasn't seen the film :)</p>
      </div>
    )
  }

  if (viewMode === 'list') {
    return (
      <div className="film-list-view">
        {films.map(film => (
          <div key={film.id} className="film-row">
            {film.poster_url && (
              <img
                src={film.poster_url}
                alt={`${film.title} poster`}
                className="film-poster-small"
                loading="lazy"
              />
            )}
            <div className="film-row-content">
              <h3>{formatTitle(film.title)}</h3>
              <div className="film-row-bottom">
                {film.release_year && (
                  <span className="meta-item">{film.release_year}</span>
                )}
                {film.length_minutes && (
                  <span className="meta-item">{film.length_minutes} min</span>
                )}
                {film.rotten_tomatoes && film.rotten_tomatoes !== 'no RT score' && (
                  <span className="meta-item rt-score">🍅 {film.rotten_tomatoes}</span>
                )}
              </div>
            </div>
            {film.letter_rating && (
              <div className="rating-box-list">
                <span className="rating">{film.letter_rating}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="film-list">
      {films.map(film => {
        const isFlipped = flippedCards.has(film.id)
        return (
          <div key={film.id} className={`film-card-container ${isFlipped ? 'flipped' : ''}`}>
            <div className="film-card-flipper">
              {/* FRONT OF CARD */}
              <div className="film-card film-card-front" onClick={() => toggleFlip(film.id)} onDoubleClick={() => toggleFlip(film.id)}>
                <div className="poster-container">
                  {film.poster_url && film.poster_url !== 'PLACEHOLDER' ? (
                    <>
                      {!loadedImages.has(film.id) && <div className="poster-skeleton"></div>}
                      <img
                        src={film.poster_url}
                        alt={`${film.title} poster`}
                        className={`film-poster ${loadedImages.has(film.id) ? 'loaded' : ''}`}
                        loading="lazy"
                        onLoad={() => handleImageLoad(film.id)}
                      />
                    </>
                  ) : (
                    <div className="poster-placeholder">
                      <p>Sorry, too obscure to pull a poster</p>
                    </div>
                  )}
                </div>

                <div className="film-content">
                  <div className="film-info-container">
                    <div className="film-info-left-column">
                      <h3 className={`film-title ${formatTitle(film.title).length > 25 ? 'film-title-long' : ''}`}>
                        {formatTitle(film.title)}
                      </h3>
                      <div className="film-metadata">
                        {film.release_year && (
                          <span className="info-item">{film.release_year}</span>
                        )}
                        {film.length_minutes && (
                          <span className="info-item">{film.length_minutes} min</span>
                        )}
                        {film.rotten_tomatoes && film.rotten_tomatoes !== 'no RT score' && (
                          <span className="info-item rt-score">🍅 {film.rotten_tomatoes}</span>
                        )}
                      </div>
                    </div>
                    {film.letter_rating && (
                      <div className="rating-box">
                        <span className="rating">{film.letter_rating}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* BACK OF CARD */}
              <div className="film-card-back" onClick={() => toggleFlip(film.id)} onDoubleClick={() => toggleFlip(film.id)}>
                <button className="close-btn" onClick={(e) => { e.stopPropagation(); toggleFlip(film.id); }}>✕</button>

                <div className="card-back-header">
                  {film.poster_url && film.poster_url !== 'PLACEHOLDER' && (
                    <img
                      src={film.poster_url}
                      alt={`${film.title} poster`}
                      className="poster-thumbnail"
                    />
                  )}
                  <div className="header-text">
                    <h3 className="film-title-back">{formatTitle(film.title)}</h3>
                    <div className="year-duration">
                      {film.release_year && <span>{film.release_year}</span>}
                      {film.length_minutes && <span>• {film.length_minutes} min</span>}
                    </div>
                  </div>
                </div>

                <div className="card-back-metrics">
                  {film.letter_rating && (
                    <div className="metric-item">
                      <span className="metric-label">J-Rayting:</span>
                      <span className="metric-value with-rating-box">{film.letter_rating}</span>
                    </div>
                  )}

                  {film.rotten_tomatoes && film.rt_link && (
                    <div className="metric-item">
                      <span className="metric-label">Score:</span>
                      <a
                        href={film.rt_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rt-link"
                        onClick={(e) => e.stopPropagation()}
                      >
                        🍅 {film.rotten_tomatoes} ↗
                      </a>
                    </div>
                  )}

                  {film.rt_per_minute && (
                    <div className="metric-item">
                      <span className="metric-label">RT/Minute:</span>
                      <span className="metric-value">{film.rt_per_minute}</span>
                    </div>
                  )}
                </div>

                {!film.date_seen && !film.format && !film.location ? (
                  <div className="card-back-details no-data">
                    James watched before 2006,<br />when he started officially tracking!
                  </div>
                ) : (
                  <div className="card-back-details">
                    {film.date_seen && (
                      <div className="detail-row">
                        <span className="detail-label">Watched:</span>
                        <span className="detail-value">{formatDate(film.date_seen)}</span>
                      </div>
                    )}
                    {film.format && (
                      <div className="detail-row">
                        <span className="detail-label">Format:</span>
                        <span className="detail-value">{formatFormat(film.format)}</span>
                      </div>
                    )}
                    {film.location && (
                      <div className="detail-row">
                        <span className="detail-label">Location:</span>
                        <span className="detail-value">{film.location}</span>
                      </div>
                    )}
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

export default FilmList
