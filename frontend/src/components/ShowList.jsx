import React, { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? 'https://web-production-01d1.up.railway.app/api' : 'http://localhost:5001/api')

// Major streaming providers we want to show (TMDB provider IDs)
const MAJOR_PROVIDERS = {
  8: 'Netflix',
  9: 'Amazon Prime Video',
  119: 'Amazon Prime Video',
  1899: 'Max',
  15: 'Hulu',
  337: 'Disney+',
  350: 'Apple TV+',
  386: 'Peacock',
  387: 'Peacock Premium',
  531: 'Paramount+',
  526: 'AMC+',
  1825: 'Max Amazon Channel',
  2100: 'Max'
}

// StreamingLogos component - shows 1-2 streaming service logos
const StreamingLogos = ({ watchProviders, maxLogos = 2 }) => {
  if (!watchProviders?.flatrate?.length) return null

  // Filter to only major providers and limit count
  const majorProviders = watchProviders.flatrate
    .filter(p => MAJOR_PROVIDERS[p.id])
    .slice(0, maxLogos)

  if (majorProviders.length === 0) return null

  return (
    <div className="streaming-logos" onClick={(e) => e.stopPropagation()}>
      {majorProviders.map(provider => (
        <a
          key={provider.id}
          href={watchProviders.link}
          target="_blank"
          rel="noopener noreferrer"
          title={`Watch on ${provider.name}`}
          className="streaming-logo-link"
        >
          <img
            src={provider.logo}
            alt={provider.name}
            className="streaming-logo"
            loading="lazy"
          />
        </a>
      ))}
    </div>
  )
}

function ShowList({ shows, onEdit, onDelete, viewMode = 'grid' }) {
  const [loadedImages, setLoadedImages] = useState(new Set())
  const [flippedCards, setFlippedCards] = useState(new Set())
  const [thoughtsModal, setThoughtsModal] = useState(null)

  // Show hint animation on first load (only in grid view)
  useEffect(() => {
    if (viewMode !== 'grid') return

    const hasSeenHint = localStorage.getItem('hasSeenShowFlipHint')
    if (!hasSeenHint && shows.length > 0) {
      setTimeout(() => {
        const firstCardFlipper = document.querySelector('.film-card-flipper')
        if (firstCardFlipper) {
          firstCardFlipper.style.transition = 'transform 1.5s ease-in-out'
          firstCardFlipper.style.transform = 'rotateY(180deg)'
          setTimeout(() => {
            firstCardFlipper.style.transform = 'rotateY(0deg)'
            setTimeout(() => {
              firstCardFlipper.style.transition = ''
              firstCardFlipper.style.transform = ''
              localStorage.setItem('hasSeenShowFlipHint', 'true')
            }, 1500)
          }, 2000)
        }
      }, 2000)
    }
  }, [shows.length, viewMode])

  const handleImageLoad = (showId) => {
    setLoadedImages(prev => new Set([...prev, showId]))
  }

  const toggleFlip = (showId) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev)
      if (newSet.has(showId)) {
        newSet.delete(showId)
      } else {
        newSet.add(showId)
      }
      return newSet
    })
  }

  // Helper to shorten end year if same century (2008-2013 → 2008-13)
  const shortenEndYear = (startYear, endYear) => {
    if (!startYear || !endYear) return endYear
    const startCentury = Math.floor(startYear / 100)
    const endCentury = Math.floor(endYear / 100)
    if (startCentury === endCentury) {
      return String(endYear).slice(-2) // Last 2 digits
    }
    return endYear
  }

  // Format years and seasons together (e.g., "2008-13; 5 seasons") - for front card
  const formatYearsAndSeasons = (startYear, endYear, isOngoing, seasons) => {
    let yearPart = ''
    if (startYear) {
      if (isOngoing) {
        yearPart = `${startYear}-Present`
      } else if (endYear && endYear !== startYear) {
        yearPart = `${startYear}-${shortenEndYear(startYear, endYear)}`
      } else {
        yearPart = `${startYear}`
      }
    }

    let seasonPart = ''
    if (seasons) {
      seasonPart = seasons === 1 ? '1 season' : `${seasons} seasons`
    }

    if (yearPart && seasonPart) {
      return `${yearPart}; ${seasonPart}`
    }
    return yearPart || seasonPart
  }

  // Format years only (for back card)
  const formatYears = (startYear, endYear, isOngoing) => {
    if (!startYear) return ''
    if (isOngoing) return `${startYear}-Present`
    if (endYear && endYear !== startYear) return `${startYear}-${shortenEndYear(startYear, endYear)}`
    return `${startYear}`
  }

  // Format seasons only (for back card)
  const formatSeasons = (seasons) => {
    if (!seasons) return ''
    return seasons === 1 ? '1 season' : `${seasons} seasons`
  }

  // IMDB badge component - styled like RT (text label + colored score)
  const IMDbBadge = ({ rating, imdbId }) => {
    const badge = (
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px'
      }}>
        <span style={{
          fontFamily: 'Impact, Arial Black, Arial, sans-serif',
          letterSpacing: '-0.5px'
        }}>IMDb</span>
        <span style={{ color: '#F5C518' }}>{rating}</span>
      </span>
    )

    if (imdbId) {
      return (
        <a
          href={`https://www.imdb.com/title/${imdbId}`}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          style={{ textDecoration: 'none', color: 'inherit' }}
        >
          {badge}
        </a>
      )
    }
    return badge
  }

  if (viewMode === 'list') {
    return (
      <div className="film-list-view">
        {shows.map((show, index) => {
          const shouldLoadEagerly = index < 10
          const shouldPrioritize = index < 30

          return (
            <div key={show.id} className="film-row">
              {show.poster_url && (
                <img
                  src={show.poster_url}
                  alt={`${show.title} poster`}
                  className="film-poster-small"
                  loading={shouldLoadEagerly ? "eager" : "lazy"}
                  fetchPriority={shouldLoadEagerly ? "high" : (shouldPrioritize ? "auto" : "low")}
                  onError={(e) => { e.target.style.display = 'none' }}
                />
              )}
              <div className="film-row-content">
                <h3>{show.title}</h3>
                <div className="film-row-bottom">
                  {(show.start_year || show.seasons) && (
                    <span className="meta-item">{formatYearsAndSeasons(show.start_year, show.end_year, show.is_ongoing, show.seasons)}</span>
                  )}
                  {show.imdb_rating && (
                    <span className="meta-item"><IMDbBadge rating={show.imdb_rating} imdbId={show.imdb_id} /></span>
                  )}
                </div>
              </div>
              {show.j_rayting && (
                <div className="rating-box-list">
                  <span className="rating">{show.j_rayting}</span>
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
      {shows.map((show, index) => {
        const isFlipped = flippedCards.has(show.id)
        const shouldLoadEagerly = index < 10
        const shouldPrioritize = index < 30

        return (
          <div key={show.id} className={`film-card-container ${isFlipped ? 'flipped' : ''}`}>
            <div className="film-card-flipper">
              {/* FRONT OF CARD */}
              <div className="film-card film-card-front" onClick={() => toggleFlip(show.id)} onDoubleClick={() => toggleFlip(show.id)}>
                <div className="poster-container">
                  {show.poster_url && show.poster_url !== 'PLACEHOLDER' ? (
                    <>
                      {!loadedImages.has(show.id) && <div className="poster-skeleton"></div>}
                      <img
                        src={show.poster_url}
                        alt={`${show.title} poster`}
                        className={`film-poster ${loadedImages.has(show.id) ? 'loaded' : ''}`}
                        loading={shouldLoadEagerly ? "eager" : "lazy"}
                        fetchPriority={shouldLoadEagerly ? "high" : (shouldPrioritize ? "auto" : "low")}
                        onLoad={() => handleImageLoad(show.id)}
                        onError={(e) => { e.target.style.display = 'none' }}
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
                      <div className="film-title-row">
                        <h3 className={`film-title ${show.title && show.title.length > 25 ? 'film-title-long' : ''}`}>
                          {show.title}
                        </h3>
                        <StreamingLogos watchProviders={show.watch_providers} maxLogos={1} />
                      </div>
                      <div className="film-metadata">
                        {(show.start_year || show.seasons) && (
                          <span className="info-item">{formatYearsAndSeasons(show.start_year, show.end_year, show.is_ongoing, show.seasons)}</span>
                        )}
                        {show.imdb_rating && (
                          <span className="info-item"><IMDbBadge rating={show.imdb_rating} imdbId={show.imdb_id} /></span>
                        )}
                      </div>
                    </div>
                    {show.j_rayting && (
                      <div className="rating-box">
                        <span className="rating">{show.j_rayting}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* BACK OF CARD */}
              <div className="film-card-back" onClick={() => toggleFlip(show.id)} onDoubleClick={() => toggleFlip(show.id)}>
                <button className="close-btn" onClick={(e) => { e.stopPropagation(); toggleFlip(show.id); }}>✕</button>

                <div className="card-back-header">
                  {show.poster_url && show.poster_url !== 'PLACEHOLDER' && (
                    <img
                      src={show.poster_url}
                      alt={`${show.title} poster`}
                      className="poster-thumbnail"
                      loading="lazy"
                      fetchPriority={shouldPrioritize ? "auto" : "low"}
                      onError={(e) => { e.target.style.display = 'none' }}
                    />
                  )}
                  <div className="header-text">
                    <h3 className="film-title-back">{show.title}</h3>
                    <div className="year-duration">
                      {show.start_year && <span>{formatYears(show.start_year, show.end_year, show.is_ongoing)}</span>}
                    </div>
                    {show.seasons && (
                      <div className="year-duration" style={{ marginTop: '2px' }}>
                        <span>{formatSeasons(show.seasons)}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="card-back-metrics">
                  {show.j_rayting && (
                    <div className="metric-item metric-item-rating">
                      <span className="metric-label">J-Rayting:</span>
                      <span className="metric-value with-rating-box">{show.j_rayting}</span>
                    </div>
                  )}

                  {show.imdb_rating && (
                    <div className="metric-item metric-item-rt">
                      <span className="metric-label"></span>
                      <span className="metric-value">
                        <IMDbBadge rating={show.imdb_rating} imdbId={show.imdb_id} />
                        {show.imdb_id && ' ↗'}
                      </span>
                    </div>
                  )}
                </div>

                <div className="card-back-details">
                  {show.genres && (
                    <div className="detail-row">
                      <span className="detail-label">Genre:</span>
                      <span className="detail-value">{show.genres}</span>
                    </div>
                  )}
                  {show.episodes && (
                    <div className="detail-row">
                      <span className="detail-label">Episodes:</span>
                      <span className="detail-value">{show.episodes}</span>
                    </div>
                  )}
                  {show.details_commentary && (
                    <div className="detail-row">
                      <span className="detail-label">My Thoughts:</span>
                      <span className="detail-value">
                        <button
                          onClick={(e) => { e.stopPropagation(); setThoughtsModal(show.id); }}
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
                </div>
              </div>
            </div>
          </div>
        )
      })}

      {/* Thoughts Modal */}
      {thoughtsModal && (() => {
        const show = shows.find(s => s.id === thoughtsModal)
        if (!show || !show.details_commentary) return null
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
                  {show.title}
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
                {show.details_commentary}
              </div>
            </div>
          </div>
        )
      })()}
    </div>
  )
}

export default ShowList
