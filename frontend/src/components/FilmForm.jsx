import { useState, useEffect } from 'react'

function FilmForm({ film, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    title: '',
    date_seen: '',
    letter_rating: '',
    format: '',
    order_number: '',
    score: '',
    year_watched: '',
    location: '',
    release_year: '',
    length_minutes: '',
    rotten_tomatoes: '',
    rt_per_minute: '',
    rt_link: '',
    poster_url: '',
    genres: ''
  })

  useEffect(() => {
    if (film) {
      setFormData({
        title: film.title || '',
        date_seen: film.date_seen || '',
        letter_rating: film.letter_rating || '',
        format: film.format || '',
        order_number: film.order_number || '',
        score: film.score || '',
        year_watched: film.year_watched || '',
        location: film.location || '',
        release_year: film.release_year || '',
        length_minutes: film.length_minutes || '',
        rotten_tomatoes: film.rotten_tomatoes || '',
        rt_per_minute: film.rt_per_minute || '',
        rt_link: film.rt_link || '',
        poster_url: film.poster_url || '',
        genres: film.genres || ''
      })
    }
  }, [film])

  const handleSubmit = (e) => {
    e.preventDefault()

    // Convert empty strings to null for numeric fields
    const dataToSave = {
      ...formData,
      order_number: formData.order_number ? parseInt(formData.order_number) : null,
      score: formData.score ? parseInt(formData.score) : null,
      release_year: formData.release_year ? parseInt(formData.release_year) : null,
      length_minutes: formData.length_minutes ? parseInt(formData.length_minutes) : null
    }

    onSave(dataToSave)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <div className="film-form-overlay">
      <div className="film-form">
        <div className="film-form-header">
          <h2>{film ? 'Edit Film' : 'Add New Film'}</h2>
          <button
            type="button"
            className="film-form-close-btn"
            onClick={onCancel}
            title="Close"
            aria-label="Close form"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form onSubmit={handleSubmit}>

          {/* Primary Fields - What you'll fill in */}
          <div className="form-section">
            <h3>Primary Info (Fill These In)</h3>

            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                placeholder="e.g., The Godfather"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="date_seen">Date Watched</label>
                <input
                  type="date"
                  id="date_seen"
                  name="date_seen"
                  value={formData.date_seen}
                  onChange={handleChange}
                  placeholder="Leave blank for pre-2006 films"
                />
              </div>

              <div className="form-group">
                <label htmlFor="letter_rating">Grade *</label>
                <select
                  id="letter_rating"
                  name="letter_rating"
                  value={formData.letter_rating}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Grade</option>
                  <option value="A+">A+</option>
                  <option value="A/A+">A/A+</option>
                  <option value="A">A</option>
                  <option value="A-/A">A-/A</option>
                  <option value="A-">A-</option>
                  <option value="B+/A-">B+/A-</option>
                  <option value="B+">B+</option>
                  <option value="B/B+">B/B+</option>
                  <option value="B">B</option>
                  <option value="B-/B">B-/B</option>
                  <option value="B-">B-</option>
                  <option value="C+/B-">C+/B-</option>
                  <option value="C+">C+</option>
                  <option value="C/C+">C/C+</option>
                  <option value="C">C</option>
                  <option value="C-">C-</option>
                  <option value="D+">D+</option>
                  <option value="D">D</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="format">Format</label>
                <select
                  id="format"
                  name="format"
                  value={formData.format}
                  onChange={handleChange}
                >
                  <option value="">Select Format</option>
                  <option value="Theatre">Theatre</option>
                  <option value="Streaming">Streaming</option>
                  <option value="On-Demand">On-Demand</option>
                  <option value="TV">TV</option>
                  <option value="DVD">DVD</option>
                  <option value="VHS">VHS</option>
                  <option value="Plane">Plane</option>
                </select>
              </div>
            </div>
          </div>

          {/* Auto-filled Fields (from API) */}
          <div className="form-section">
            <h3>Additional Info (Auto-filled from API or Optional)</h3>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="score">Score (0-100)</label>
                <input
                  type="number"
                  id="score"
                  name="score"
                  min="0"
                  max="100"
                  value={formData.score}
                  onChange={handleChange}
                  placeholder="Auto-calculated from grade"
                />
              </div>

              <div className="form-group">
                <label htmlFor="order_number">Order #</label>
                <input
                  type="number"
                  id="order_number"
                  name="order_number"
                  value={formData.order_number}
                  onChange={handleChange}
                  placeholder="Sequence number"
                />
              </div>

              <div className="form-group">
                <label htmlFor="year_watched">Year Watched</label>
                <input
                  type="text"
                  id="year_watched"
                  name="year_watched"
                  value={formData.year_watched}
                  onChange={handleChange}
                  placeholder="e.g., 2024 or Pre-2006"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="location">Location</label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="Where you watched it"
                />
              </div>

              <div className="form-group">
                <label htmlFor="release_year">Release Year</label>
                <input
                  type="number"
                  id="release_year"
                  name="release_year"
                  min="1900"
                  max={new Date().getFullYear() + 5}
                  value={formData.release_year}
                  onChange={handleChange}
                  placeholder="From TMDB API"
                />
              </div>

              <div className="form-group">
                <label htmlFor="length_minutes">Length (minutes)</label>
                <input
                  type="number"
                  id="length_minutes"
                  name="length_minutes"
                  value={formData.length_minutes}
                  onChange={handleChange}
                  placeholder="From TMDB API"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="rotten_tomatoes">Rotten Tomatoes %</label>
                <input
                  type="text"
                  id="rotten_tomatoes"
                  name="rotten_tomatoes"
                  value={formData.rotten_tomatoes}
                  onChange={handleChange}
                  placeholder="e.g., 92%"
                />
              </div>

              <div className="form-group">
                <label htmlFor="rt_per_minute">RT per Minute</label>
                <input
                  type="text"
                  id="rt_per_minute"
                  name="rt_per_minute"
                  value={formData.rt_per_minute}
                  onChange={handleChange}
                  placeholder="Auto-calculated"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="rt_link">Rotten Tomatoes URL</label>
              <input
                type="url"
                id="rt_link"
                name="rt_link"
                value={formData.rt_link}
                onChange={handleChange}
                placeholder="e.g., https://www.rottentomatoes.com/m/the_godfather (for duplicates)"
              />
              <small style={{ color: '#999', fontSize: '0.85rem' }}>
                Required when adding a film with the same title as an existing entry
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="genres">Genres</label>
              <input
                type="text"
                id="genres"
                name="genres"
                value={formData.genres}
                onChange={handleChange}
                placeholder="e.g., Drama, Crime (from TMDB API)"
              />
            </div>

            <div className="form-group">
              <label htmlFor="poster_url">Poster URL / Image URL</label>
              <input
                type="url"
                id="poster_url"
                name="poster_url"
                value={formData.poster_url}
                onChange={handleChange}
                placeholder="Paste image URL here (e.g., https://example.com/poster.jpg)"
              />
              {formData.poster_url && (
                <div style={{ marginTop: '10px' }}>
                  <img 
                    src={formData.poster_url} 
                    alt="Preview" 
                    style={{ 
                      maxWidth: '200px', 
                      maxHeight: '300px', 
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div style={{ display: 'none', color: '#999', fontSize: '0.85rem', marginTop: '5px' }}>
                    Image failed to load. Check URL.
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              {film ? 'Update Film' : 'Add Film'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default FilmForm
