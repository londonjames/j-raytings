import React, { useState } from 'react'

function FilmList({ films, onEdit, onDelete, viewMode = 'grid' }) {
  const [loadedImages, setLoadedImages] = useState(new Set())

  const handleImageLoad = (filmId) => {
    setLoadedImages(prev => new Set([...prev, filmId]))
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
                {film.rotten_tomatoes && (
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
      {films.map(film => (
        <div key={film.id} className="film-card">
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
                  {film.rotten_tomatoes && (
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
      ))}
    </div>
  )
}

export default FilmList
