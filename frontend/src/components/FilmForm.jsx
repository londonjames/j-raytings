import { useState, useEffect } from 'react'

function FilmForm({ film, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    title: '',
    rating: '',
    year_watched: '',
    release_year: '',
    genre: '',
    director: '',
    notes: ''
  })

  useEffect(() => {
    if (film) {
      setFormData({
        title: film.title || '',
        rating: film.rating || '',
        year_watched: film.year_watched || '',
        release_year: film.release_year || '',
        genre: film.genre || '',
        director: film.director || '',
        notes: film.notes || ''
      })
    }
  }, [film])

  const handleSubmit = (e) => {
    e.preventDefault()

    // Convert empty strings to null for numeric fields
    const dataToSave = {
      ...formData,
      rating: formData.rating ? parseFloat(formData.rating) : null,
      year_watched: formData.year_watched ? parseInt(formData.year_watched) : null,
      release_year: formData.release_year ? parseInt(formData.release_year) : null
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
        <h2>{film ? 'Edit Film' : 'Add New Film'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="rating">Your Rating (0-10)</label>
              <input
                type="number"
                id="rating"
                name="rating"
                min="0"
                max="10"
                step="0.1"
                value={formData.rating}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="year_watched">Year Watched</label>
              <input
                type="number"
                id="year_watched"
                name="year_watched"
                min="1900"
                max={new Date().getFullYear()}
                value={formData.year_watched}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="release_year">Release Year</label>
              <input
                type="number"
                id="release_year"
                name="release_year"
                min="1900"
                max={new Date().getFullYear()}
                value={formData.release_year}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="genre">Genre</label>
              <input
                type="text"
                id="genre"
                name="genre"
                value={formData.genre}
                onChange={handleChange}
                placeholder="e.g., Drama, Action, Sci-Fi"
              />
            </div>

            <div className="form-group">
              <label htmlFor="director">Director</label>
              <input
                type="text"
                id="director"
                name="director"
                value={formData.director}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="notes">Notes</label>
            <textarea
              id="notes"
              name="notes"
              rows="3"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Your thoughts about this film..."
            />
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
