import { useState, useEffect } from 'react'
import FilmForm from './FilmForm'
import './AdminPanel.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

function AdminPanel({ onLogout }) {
  const [showAddForm, setShowAddForm] = useState(false)
  const [message, setMessage] = useState('')
  const [duplicateWarning, setDuplicateWarning] = useState(null)
  const [films, setFilms] = useState([])
  const [filteredFilms, setFilteredFilms] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [editingFilm, setEditingFilm] = useState(null)

  // Fetch all films
  const fetchFilms = async () => {
    try {
      const response = await fetch(`${API_URL}/films`)
      const data = await response.json()
      setFilms(data)
      setFilteredFilms(data)
    } catch (error) {
      console.error('Error fetching films:', error)
    }
  }

  // Fetch films on component mount
  useEffect(() => {
    fetchFilms()
  }, [])

  // Filter films based on search
  const handleSearch = (term) => {
    setSearchTerm(term)
    if (!term) {
      setFilteredFilms(films)
    } else {
      const filtered = films.filter(film =>
        film.title.toLowerCase().includes(term.toLowerCase()) ||
        film.release_year?.toString().includes(term)
      )
      setFilteredFilms(filtered)
    }
  }

  const handleSaveFilm = async (filmData) => {
    try {
      const url = editingFilm
        ? `${API_URL}/films/${editingFilm.id}`
        : `${API_URL}/films`

      const method = editingFilm ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filmData)
      })

      if (response.ok) {
        const result = await response.json()
        if (editingFilm) {
          setMessage('Film updated successfully!')
        } else if (result.metadata_fetched) {
          setMessage('Film added successfully! Metadata (poster, genres, runtime) auto-fetched from TMDB.')
        } else {
          setMessage('Film added successfully!')
        }
        setShowAddForm(false)
        setEditingFilm(null)
        setDuplicateWarning(null)
        fetchFilms()
        setTimeout(() => setMessage(''), 5000)
      } else if (response.status === 409) {
        // Duplicate detected
        const result = await response.json()
        setDuplicateWarning(result)
        setMessage('')
      } else {
        setMessage('Error saving film')
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage('Error saving film')
    }
  }

  const handleEditFilm = (film) => {
    setEditingFilm(film)
    setShowAddForm(true)
  }

  const handleDeleteFilm = async (id) => {
    if (!confirm('Are you sure you want to delete this film?')) return

    try {
      const response = await fetch(`${API_URL}/films/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setMessage('Film deleted successfully!')
        fetchFilms()
        setTimeout(() => setMessage(''), 3000)
      } else {
        setMessage('Error deleting film')
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage('Error deleting film')
    }
  }

  const handleLogout = () => {
    sessionStorage.removeItem('adminAuthenticated')
    onLogout()
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>Admin Panel</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      {message && (
        <div className={`admin-message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {duplicateWarning && (
        <div className="admin-message warning">
          <strong>{duplicateWarning.message}</strong>
          <div style={{ marginTop: '10px' }}>
            <p>Existing films with this title:</p>
            <ul>
              {duplicateWarning.existing_films.map(film => (
                <li key={film.id}>
                  {film.title} ({film.release_year}) - {film.rt_link || 'No RT link'}
                </li>
              ))}
            </ul>
            <p>Please add a Rotten Tomatoes URL in the form below to distinguish this version.</p>
          </div>
        </div>
      )}

      <div className="admin-content">
        {!showAddForm ? (
          <>
            <div className="admin-actions">
              <button onClick={() => setShowAddForm(true)} className="add-film-btn">
                + Add New Film
              </button>
              <a href="/" className="view-site-btn">View Public Site</a>
            </div>

            <div className="admin-search">
              <input
                type="text"
                placeholder="Search films by title or year..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="search-input"
              />
              <span className="film-count">{filteredFilms.length} film(s)</span>
            </div>

            <div className="admin-film-list">
              {filteredFilms.map(film => (
                <div key={film.id} className="admin-film-item">
                  <div className="film-info">
                    {film.poster_url && (
                      <img src={film.poster_url} alt={film.title} className="film-thumb" />
                    )}
                    <div className="film-details">
                      <h3>{film.title}</h3>
                      <div className="film-meta">
                        {film.release_year && <span>Year: {film.release_year}</span>}
                        {film.letter_rating && <span>Rating: {film.letter_rating}</span>}
                        {film.date_seen && <span>Watched: {film.date_seen}</span>}
                      </div>
                    </div>
                  </div>
                  <div className="film-actions">
                    <button onClick={() => handleEditFilm(film)} className="edit-btn">
                      Edit
                    </button>
                    <button onClick={() => handleDeleteFilm(film.id)} className="delete-btn">
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="admin-form-container">
            <h2>{editingFilm ? 'Edit Film' : 'Add New Film'}</h2>
            <FilmForm
              film={editingFilm}
              onSave={handleSaveFilm}
              onCancel={() => {
                setShowAddForm(false)
                setEditingFilm(null)
                setDuplicateWarning(null)
              }}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminPanel
