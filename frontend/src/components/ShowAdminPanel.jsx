import { useState, useEffect } from 'react'
import ShowForm from './ShowForm'
import './AdminPanel.css'

const API_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? 'https://web-production-01d1.up.railway.app/api' : 'http://localhost:5001/api')

function ShowAdminPanel({ onLogout }) {
  const handleLogout = () => {
    sessionStorage.removeItem('adminAuthenticated')
    onLogout()
  }
  const [showAddForm, setShowAddForm] = useState(false)
  const [message, setMessage] = useState('')
  const [duplicateWarning, setDuplicateWarning] = useState(null)
  const [shows, setShows] = useState([])
  const [filteredShows, setFilteredShows] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [editingShow, setEditingShow] = useState(null)

  const fetchShows = async () => {
    try {
      const response = await fetch(`${API_URL}/shows?_t=${Date.now()}`, {
        cache: 'no-store'
      })
      const data = await response.json()
      const showsArray = Array.isArray(data) ? data : []
      const sortedData = [...showsArray].sort((a, b) => {
        const aUpdated = a.updated_at ? new Date(a.updated_at) : new Date(0)
        const bUpdated = b.updated_at ? new Date(b.updated_at) : new Date(0)
        if (bUpdated.getTime() !== aUpdated.getTime()) {
          return bUpdated.getTime() - aUpdated.getTime()
        }
        return (b.id || 0) - (a.id || 0)
      })
      setShows(sortedData)
      setFilteredShows(sortedData)
    } catch (error) {
      console.error('Error fetching shows:', error)
      setShows([])
      setFilteredShows([])
    }
  }

  useEffect(() => {
    fetchShows()
  }, [])

  const handleSearch = (term) => {
    setSearchTerm(term)
    if (!term) {
      setFilteredShows(shows)
    } else {
      const filtered = shows.filter(show =>
        show.title?.toLowerCase().includes(term.toLowerCase()) ||
        show.genres?.toLowerCase().includes(term.toLowerCase()) ||
        show.start_year?.toString().includes(term)
      )
      setFilteredShows(filtered)
    }
  }

  const handleSaveShow = async (showData) => {
    try {
      const url = editingShow
        ? `${API_URL}/shows/${editingShow.id}`
        : `${API_URL}/shows`

      const method = editingShow ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(showData)
      })

      if (response.ok) {
        const result = await response.json()
        if (editingShow) {
          setMessage('Show updated successfully!')
        } else if (result.metadata_fetched) {
          setMessage('Show added successfully! Metadata (poster, IMDB rating) auto-fetched.')
        } else {
          setMessage('Show added successfully!')
        }
        setShowAddForm(false)
        setEditingShow(null)
        setDuplicateWarning(null)
        setTimeout(() => {
          fetchShows()
        }, 500)
        setTimeout(() => setMessage(''), 5000)
      } else if (response.status === 409) {
        const result = await response.json()
        setDuplicateWarning(result)
        setMessage('')
      } else {
        let errorMessage = 'Error saving show'
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorData.message || errorMessage
        } catch (e) {
          errorMessage = `Error saving show (${response.status}: ${response.statusText})`
        }
        setMessage(errorMessage)
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage(`Error saving show: ${error.message}`)
    }
  }

  const handleEditShow = (show) => {
    setEditingShow(show)
    setShowAddForm(true)
  }

  const handleDeleteShow = async (id) => {
    if (!confirm('Are you sure you want to delete this show?')) return

    try {
      const response = await fetch(`${API_URL}/shows/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setMessage('Show deleted successfully!')
        fetchShows()
        setTimeout(() => setMessage(''), 3000)
      } else {
        setMessage('Error deleting show')
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage(`Error deleting show: ${error.message}`)
    }
  }

  const formatYears = (startYear, endYear, isOngoing) => {
    if (!startYear) return ''
    if (isOngoing) return `${startYear}-Present`
    if (endYear && endYear !== startYear) return `${startYear}-${endYear}`
    return `${startYear}`
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>Shows Admin Panel</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      {message && (
        <div className={`admin-message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {duplicateWarning && (
        <div className="duplicate-warning">
          <h3>Duplicate Show Detected</h3>
          <p>This show may already exist in the database.</p>
        </div>
      )}

      <div className="admin-content">
        {!showAddForm ? (
          <>
            <div className="admin-actions">
              <button
                onClick={() => {
                  setShowAddForm(true)
                  setEditingShow(null)
                }}
                className="add-film-btn"
              >
                + Add New Show
              </button>
              <a href="/shows" className="view-site-btn">View Public Site</a>
            </div>

            <div className="admin-search">
              <input
                type="text"
                placeholder="Search shows by title, genre, or year..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="search-input"
              />
              <span className="film-count">{filteredShows.length} show(s)</span>
            </div>

            <div className="admin-film-list">
              {(filteredShows || []).map(show => (
                <div key={show.id} className="admin-film-item">
                  <div className="film-info">
                    {show.poster_url && show.poster_url !== 'PLACEHOLDER' && (
                      <img
                        src={show.poster_url}
                        alt={show.title}
                        className="film-thumb"
                        onError={(e) => { e.target.style.display = 'none' }}
                      />
                    )}
                    <div className="film-details">
                      <h3>{show.title}</h3>
                      <div className="film-meta">
                        {show.start_year && <span>{formatYears(show.start_year, show.end_year, show.is_ongoing)}</span>}
                        {show.seasons && <span>{show.seasons} season(s)</span>}
                        {show.j_rayting && <span>Rating: {show.j_rayting}</span>}
                        {show.imdb_rating && <span>IMDB: {show.imdb_rating}</span>}
                        {show.poster_url && show.poster_url !== 'PLACEHOLDER' ? (
                          <span style={{ color: '#68d391' }}>Has poster</span>
                        ) : (
                          <span style={{ color: '#fc8181' }}>No poster</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="film-actions">
                    <button onClick={() => handleEditShow(show)} className="edit-btn">
                      Edit
                    </button>
                    <button onClick={() => handleDeleteShow(show.id)} className="delete-btn">
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="admin-form-container">
            <h2>{editingShow ? 'Edit Show' : 'Add New Show'}</h2>
            {showAddForm && (
              <ShowForm
                show={editingShow}
                onSave={handleSaveShow}
                onCancel={() => {
                  setShowAddForm(false)
                  setEditingShow(null)
                  setDuplicateWarning(null)
                }}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ShowAdminPanel
