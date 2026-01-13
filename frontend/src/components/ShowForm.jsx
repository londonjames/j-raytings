import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? 'https://web-production-01d1.up.railway.app/api' : 'http://localhost:5001/api')

function ShowForm({ show, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    title: '',
    start_year: '',
    end_year: '',
    is_ongoing: false,
    seasons: '',
    episodes: '',
    j_rayting: '',
    score: '',
    imdb_rating: '',
    imdb_id: '',
    genres: '',
    poster_url: '',
    details_commentary: '',
    date_watched: '',
    a_grade_rank: ''
  })

  useEffect(() => {
    if (show) {
      setFormData({
        title: show.title || '',
        start_year: show.start_year || '',
        end_year: show.end_year || '',
        is_ongoing: show.is_ongoing || false,
        seasons: show.seasons || '',
        episodes: show.episodes || '',
        j_rayting: show.j_rayting || '',
        score: show.score || '',
        imdb_rating: show.imdb_rating || '',
        imdb_id: show.imdb_id || '',
        genres: show.genres || '',
        poster_url: show.poster_url || '',
        details_commentary: show.details_commentary || '',
        date_watched: show.date_watched || '',
        a_grade_rank: show.a_grade_rank || ''
      })
    }
  }, [show])

  const handleSubmit = (e) => {
    e.preventDefault()

    const dataToSave = {
      ...formData,
      start_year: formData.start_year ? parseInt(formData.start_year) : null,
      end_year: formData.end_year ? parseInt(formData.end_year) : null,
      seasons: formData.seasons ? parseInt(formData.seasons) : null,
      episodes: formData.episodes ? parseInt(formData.episodes) : null,
      score: formData.score ? parseInt(formData.score) : null,
      a_grade_rank: formData.a_grade_rank ? parseInt(formData.a_grade_rank) : null
    }

    onSave(dataToSave)
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  return (
    <div className="film-form-overlay">
      <div className="film-form">
        <div className="film-form-header">
          <h2>{show ? 'Edit Show' : 'Add New Show'}</h2>
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

          <div className="form-section">
            <h3>Show Info</h3>

            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                placeholder="e.g., Breaking Bad"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="start_year">Start Year</label>
                <input
                  type="number"
                  id="start_year"
                  name="start_year"
                  min="1950"
                  max={new Date().getFullYear()}
                  value={formData.start_year}
                  onChange={handleChange}
                  placeholder="e.g., 2008"
                />
              </div>

              <div className="form-group">
                <label htmlFor="end_year">End Year</label>
                <input
                  type="number"
                  id="end_year"
                  name="end_year"
                  min="1950"
                  max={new Date().getFullYear() + 5}
                  value={formData.end_year}
                  onChange={handleChange}
                  placeholder="e.g., 2013"
                  disabled={formData.is_ongoing}
                />
              </div>

              <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  id="is_ongoing"
                  name="is_ongoing"
                  checked={formData.is_ongoing}
                  onChange={handleChange}
                  style={{ width: 'auto' }}
                />
                <label htmlFor="is_ongoing" style={{ marginBottom: 0 }}>Still Ongoing</label>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="seasons">Seasons</label>
                <input
                  type="number"
                  id="seasons"
                  name="seasons"
                  min="1"
                  value={formData.seasons}
                  onChange={handleChange}
                  placeholder="e.g., 5"
                />
              </div>

              <div className="form-group">
                <label htmlFor="episodes">Episodes</label>
                <input
                  type="number"
                  id="episodes"
                  name="episodes"
                  min="1"
                  value={formData.episodes}
                  onChange={handleChange}
                  placeholder="e.g., 62"
                />
              </div>

              <div className="form-group">
                <label htmlFor="j_rayting">Grade *</label>
                <select
                  id="j_rayting"
                  name="j_rayting"
                  value={formData.j_rayting}
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
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="genres">Genres</label>
                <input
                  type="text"
                  id="genres"
                  name="genres"
                  value={formData.genres}
                  onChange={handleChange}
                  placeholder="e.g., Drama, Crime"
                />
              </div>

              <div className="form-group">
                <label htmlFor="imdb_rating">IMDB Rating</label>
                <input
                  type="text"
                  id="imdb_rating"
                  name="imdb_rating"
                  value={formData.imdb_rating}
                  onChange={handleChange}
                  placeholder="e.g., 9.5"
                />
              </div>

              <div className="form-group">
                <label htmlFor="imdb_id">IMDB ID</label>
                <input
                  type="text"
                  id="imdb_id"
                  name="imdb_id"
                  value={formData.imdb_id}
                  onChange={handleChange}
                  placeholder="e.g., tt0903747"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="date_watched">Date Watched</label>
              <input
                type="text"
                id="date_watched"
                name="date_watched"
                value={formData.date_watched}
                onChange={handleChange}
                placeholder="e.g., 2023 or January 2024"
              />
            </div>

            <div className="form-group">
              <label htmlFor="poster_url">Poster URL</label>
              <input
                type="url"
                id="poster_url"
                name="poster_url"
                value={formData.poster_url}
                onChange={handleChange}
                placeholder="Paste poster image URL here"
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
                    onError={(e) => { e.target.style.display = 'none' }}
                  />
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="details_commentary">My Thoughts</label>
              <textarea
                id="details_commentary"
                name="details_commentary"
                value={formData.details_commentary || ''}
                onChange={handleChange}
                rows="4"
                placeholder="Your thoughts and commentary about the show..."
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              {show ? 'Update Show' : 'Add Show'}
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

export default ShowForm
