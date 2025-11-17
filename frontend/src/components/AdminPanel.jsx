import { useState } from 'react'
import FilmForm from './FilmForm'
import './AdminPanel.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

function AdminPanel({ onLogout }) {
  const [showAddForm, setShowAddForm] = useState(false)
  const [message, setMessage] = useState('')

  const handleSaveFilm = async (filmData) => {
    try {
      const response = await fetch(`${API_URL}/films`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filmData)
      })

      if (response.ok) {
        const result = await response.json()
        if (result.metadata_fetched) {
          setMessage('Film added successfully! Metadata (poster, genres, runtime) auto-fetched from TMDB.')
        } else {
          setMessage('Film added successfully!')
        }
        setShowAddForm(false)
        setTimeout(() => setMessage(''), 5000)
      } else {
        setMessage('Error adding film')
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage('Error adding film')
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

      <div className="admin-content">
        {!showAddForm ? (
          <div className="admin-actions">
            <button onClick={() => setShowAddForm(true)} className="add-film-btn">
              + Add New Film
            </button>
            <a href="/" className="view-site-btn">View Public Site</a>
          </div>
        ) : (
          <div className="admin-form-container">
            <h2>Add New Film</h2>
            <FilmForm
              onSave={handleSaveFilm}
              onCancel={() => setShowAddForm(false)}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminPanel
