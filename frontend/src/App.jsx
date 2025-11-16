import { useState, useEffect, useCallback } from 'react'
import './App.css'
import FilmList from './components/FilmList'
import FilmForm from './components/FilmForm'
import SearchBar from './components/SearchBar'
import SortBar from './components/SortBar'
import FilterBar from './components/FilterBar'
import Analytics from './components/Analytics'

const API_URL = 'http://localhost:5001/api'

function App() {
  const [films, setFilms] = useState([])
  const [filteredFilms, setFilteredFilms] = useState([])
  const [editingFilm, setEditingFilm] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeFilter, setActiveFilter] = useState({ rating: [], year: [], rt: [], genre: [] })
  const [sortConfig, setSortConfig] = useState({ sortBy: '', direction: 'desc' })
  const [viewMode, setViewMode] = useState(() => {
    // Load from localStorage or default to 'grid'
    return localStorage.getItem('viewMode') || 'grid'
  })
  const [resetKey, setResetKey] = useState(0)
  const [showAnalytics, setShowAnalytics] = useState(false)

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

  useEffect(() => {
    fetchFilms()
  }, [])

  // Save view mode to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('viewMode', viewMode)
  }, [viewMode])

  // Add or update film
  const handleSaveFilm = async (filmData) => {
    try {
      const url = editingFilm
        ? `${API_URL}/films/${editingFilm.id}`
        : `${API_URL}/films`

      const method = editingFilm ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filmData)
      })

      if (response.ok) {
        fetchFilms()
        setShowForm(false)
        setEditingFilm(null)
      }
    } catch (error) {
      console.error('Error saving film:', error)
    }
  }

  // Delete film
  const handleDeleteFilm = async (id) => {
    if (!confirm('Are you sure you want to delete this film?')) return

    try {
      const response = await fetch(`${API_URL}/films/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchFilms()
      }
    } catch (error) {
      console.error('Error deleting film:', error)
    }
  }

  // Edit film
  const handleEditFilm = (film) => {
    setEditingFilm(film)
    setShowForm(true)
  }

  // Helper function to format film titles (same as FilmList)
  const formatTitle = (title) => {
    if (!title) return ''
    if (title.includes(',')) {
      const parts = title.split(',').map(s => s.trim())
      if (parts.length === 2) {
        return `${parts[1]} ${parts[0]}`
      }
    }
    return title
  }

  // Apply filters and search
  const applyFiltersAndSearch = useCallback((searchValue, filterConfig) => {
    let filtered = [...films]

    // Apply search
    if (searchValue) {
      const searchLower = searchValue.toLowerCase()
      filtered = filtered.filter(film => {
        const originalTitle = film.title.toLowerCase()
        const formattedTitle = formatTitle(film.title).toLowerCase()
        return originalTitle.includes(searchLower) || formattedTitle.includes(searchLower)
      })
    }

    // Apply rating filter
    if (filterConfig.rating && filterConfig.rating.length > 0) {
      filtered = filtered.filter(film => {
        return filterConfig.rating.includes(film.letter_rating)
      })
    }

    // Apply year filter
    if (filterConfig.year && filterConfig.year.length > 0) {
      filtered = filtered.filter(film => {
        if (!film.release_year) return false
        const year = parseInt(film.release_year)

        return filterConfig.year.some(selectedDecade => {
          if (selectedDecade === 'Pre-1950') {
            return year < 1950
          } else {
            const decade = selectedDecade.replace('s', '')
            const decadeStart = parseInt(decade)
            return year >= decadeStart && year < decadeStart + 10
          }
        })
      })
    }

    // Apply RT score filter
    if (filterConfig.rt && filterConfig.rt.length > 0) {
      filtered = filtered.filter(film => {
        if (!film.rotten_tomatoes) return false
        const rtScore = parseInt(film.rotten_tomatoes.replace('%', ''))

        return filterConfig.rt.some(selectedRange => {
          const [min, max] = selectedRange.split('-').map(n => parseInt(n))
          return rtScore >= min && rtScore <= max
        })
      })
    }

    // Apply genre filter
    if (filterConfig.genre && filterConfig.genre.length > 0) {
      filtered = filtered.filter(film => {
        if (!film.genres) return false
        const filmGenres = film.genres.split(', ')

        return filterConfig.genre.some(selectedGenre => {
          return filmGenres.includes(selectedGenre)
        })
      })
    }

    // Apply sorting
    filtered = sortFilms(filtered, sortConfig)

    setFilteredFilms(filtered)
  }, [films, sortConfig])

  // Sort films based on configuration
  const sortFilms = (filmsToSort, config) => {
    const sorted = [...filmsToSort]
    const { sortBy, direction } = config

    sorted.sort((a, b) => {
      let comparison = 0

      // Default to rating if no sort is selected
      const actualSortBy = sortBy || 'rating'

      if (actualSortBy === 'rating') {
        // Use numeric score field (20 = A+, 19 = A/A+, etc.)
        // Higher score = better rating
        const aScore = a.score || 0
        const bScore = b.score || 0
        comparison = bScore - aScore // Higher score first
      } else if (actualSortBy === 'year') {
        const aYear = parseInt(a.release_year) || 0
        const bYear = parseInt(b.release_year) || 0
        comparison = bYear - aYear // Newer first
      } else if (actualSortBy === 'rt') {
        const aRT = parseInt(a.rotten_tomatoes?.replace('%', '')) || 0
        const bRT = parseInt(b.rotten_tomatoes?.replace('%', '')) || 0
        comparison = bRT - aRT // Higher RT first
      }

      // For desc (best first): keep comparison as is
      // For asc (worst first): reverse it
      return direction === 'desc' ? comparison : -comparison
    })

    return sorted
  }

  // Search films
  const handleSearch = (newSearchTerm) => {
    setSearchTerm(newSearchTerm)
    applyFiltersAndSearch(newSearchTerm, activeFilter)
  }

  // Handle filter change
  const handleFilterChange = (filterConfig) => {
    setActiveFilter(filterConfig)
    applyFiltersAndSearch(searchTerm, filterConfig)
  }

  // Handle sort change
  const handleSortChange = (newSortConfig) => {
    setSortConfig(newSortConfig)
    applyFiltersAndSearch(searchTerm, activeFilter)
  }

  // Re-apply filters when films data changes
  useEffect(() => {
    applyFiltersAndSearch(searchTerm, activeFilter)
  }, [films, sortConfig, searchTerm, activeFilter, applyFiltersAndSearch])

  // Reset to home experience
  const handleReset = () => {
    // Clear all filters and search
    const newFilters = { rating: [], year: [], rt: [], genre: [] }
    setSearchTerm('')
    setActiveFilter(newFilters)
    setSortConfig({ sortBy: '', direction: 'desc' })
    setShowAnalytics(false)

    // Apply the reset immediately
    applyFiltersAndSearch('', newFilters)

    // Force child components to remount
    setResetKey(prev => prev + 1)
  }

  // Toggle analytics view
  const handleAnalyticsToggle = () => {
    setShowAnalytics(!showAnalytics)
  }

  return (
    <div className="app">
      <div className="sticky-header">
        <div className="container">
          <div className="header-controls">
            <div className="site-title" onClick={handleReset} style={{ cursor: 'pointer' }}>J-RAYTINGS</div>
            <div className="search-and-filter">
              <SearchBar
                key={`search-${resetKey}`}
                onSearch={handleSearch}
                totalFilms={films.length}
                filteredFilms={filteredFilms.length}
              />
              <SortBar key={`sort-${resetKey}`} onSortChange={handleSortChange} />
              <FilterBar key={`filter-${resetKey}`} onFilterChange={handleFilterChange} />
              <button
                className={`analytics-button ${showAnalytics ? 'active' : ''}`}
                onClick={handleAnalyticsToggle}
                title="Analytics"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="2" y="15" width="3.5" height="6" rx="0.5"></rect>
                  <rect x="7.5" y="10" width="3.5" height="11" rx="0.5"></rect>
                  <rect x="13" y="6" width="3.5" height="15" rx="0.5"></rect>
                  <rect x="18.5" y="3" width="3.5" height="18" rx="0.5"></rect>
                </svg>
              </button>
            </div>
            <div className="view-controls">
              <button
                className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                onClick={() => setViewMode('grid')}
                title="Grid view"
              >
                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                  <rect x="2" y="2" width="6" height="6" rx="1"/>
                  <rect x="12" y="2" width="6" height="6" rx="1"/>
                  <rect x="2" y="12" width="6" height="6" rx="1"/>
                  <rect x="12" y="12" width="6" height="6" rx="1"/>
                </svg>
              </button>
              <button
                className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                onClick={() => setViewMode('list')}
                title="List view"
              >
                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                  <rect x="2" y="3" width="16" height="2" rx="1"/>
                  <rect x="2" y="9" width="16" height="2" rx="1"/>
                  <rect x="2" y="15" width="16" height="2" rx="1"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="container">
        {showAnalytics ? (
          <Analytics />
        ) : (
          <FilmList
            films={filteredFilms}
            onEdit={handleEditFilm}
            onDelete={handleDeleteFilm}
            viewMode={viewMode}
          />
        )}
      </div>
    </div>
  )
}

export default App
