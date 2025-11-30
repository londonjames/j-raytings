import { useState, useEffect, useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import './App.css'
import FilmList from './components/FilmList'
import FilmForm from './components/FilmForm'
import SearchBar from './components/SearchBar'
import SortBar from './components/SortBar'
import FilterBar from './components/FilterBar'
import Analytics from './components/Analytics'

// Use environment variable for production API URL (Railway backend)
// In development, use local backend
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

function App() {
  const location = useLocation()
  const navigate = useNavigate()
  
  // Update page title based on route
  useEffect(() => {
    if (location.pathname.includes('/admin')) {
      document.title = 'Admin | Films | James Raybould'
    } else {
      document.title = 'Films | James Raybould'
    }
  }, [location.pathname])
  
  // Helper function to parse URL query parameters
  const parseQueryParams = () => {
    const params = new URLSearchParams(location.search)
    const search = params.get('search') || ''
    const filters = {
      rating: params.get('rating') ? params.get('rating').split(',') : [],
      rt: params.get('rt') ? params.get('rt').split(',') : [],
      year: params.get('year') ? params.get('year').split(',') : [],
      yearSeen: params.get('yearSeen') ? params.get('yearSeen').split(',') : [],
      genre: params.get('genre') ? params.get('genre').split(',') : [],
    }
    const sortBy = params.get('sortBy') || ''
    const sortDirection = params.get('sortDirection') || 'desc'
    const analytics = params.get('analytics') === 'true'
    
    return { search, filters, sortBy, sortDirection, analytics }
  }
  
  // Helper function to update URL with current state
  const updateURL = (search, filters, sortConfig, showAnalytics) => {
    const params = new URLSearchParams()
    
    if (search) params.set('search', search)
    if (filters.rating.length > 0) params.set('rating', filters.rating.join(','))
    if (filters.rt.length > 0) params.set('rt', filters.rt.join(','))
    if (filters.year.length > 0) params.set('year', filters.year.join(','))
    if (filters.yearSeen.length > 0) params.set('yearSeen', filters.yearSeen.join(','))
    if (filters.genre.length > 0) params.set('genre', filters.genre.join(','))
    if (sortConfig.sortBy) {
      params.set('sortBy', sortConfig.sortBy)
      params.set('sortDirection', sortConfig.direction)
    }
    if (showAnalytics) params.set('analytics', 'true')
    
    const newSearch = params.toString()
    const newURL = newSearch ? `?${newSearch}` : ''
    navigate(newURL, { replace: true })
  }
  
  const [films, setFilms] = useState([])
  const [filteredFilms, setFilteredFilms] = useState([])
  const [editingFilm, setEditingFilm] = useState(null)
  const [showForm, setShowForm] = useState(false)
  
  // Initialize state from URL params or localStorage
  const urlParams = parseQueryParams()
  const [searchTerm, setSearchTerm] = useState(() => {
    return urlParams.search || localStorage.getItem('searchTerm') || ''
  })
  const [activeFilter, setActiveFilter] = useState(() => {
    const hasUrlFilters = urlParams.filters.rating.length > 0 || 
                         urlParams.filters.rt.length > 0 ||
                         urlParams.filters.year.length > 0 ||
                         urlParams.filters.yearSeen.length > 0 ||
                         urlParams.filters.genre.length > 0
    if (hasUrlFilters) {
      return urlParams.filters
    }
    const saved = localStorage.getItem('activeFilter')
    return saved ? JSON.parse(saved) : { rating: [], rt: [], year: [], yearSeen: [], genre: [] }
  })
  const [sortConfig, setSortConfig] = useState(() => {
    if (urlParams.sortBy) {
      return { sortBy: urlParams.sortBy, direction: urlParams.sortDirection }
    }
    const saved = localStorage.getItem('sortConfig')
    // Default to empty sortBy so UI doesn't show as selected, but sorting still defaults to rating
    return saved ? JSON.parse(saved) : { sortBy: '', direction: 'desc' }
  })
  const [viewMode, setViewMode] = useState(() => {
    // Load from localStorage or default to 'grid'
    return localStorage.getItem('viewMode') || 'grid'
  })
  const [resetKey, setResetKey] = useState(0)
  const [showAnalytics, setShowAnalytics] = useState(() => {
    return urlParams.analytics || localStorage.getItem('showAnalytics') === 'true'
  })
  const [isLoading, setIsLoading] = useState(true)
  const [hasActiveFilters, setHasActiveFilters] = useState(false)
  
  // Update URL when state changes (but skip initial mount to avoid overwriting URL params)
  const [isInitialMount, setIsInitialMount] = useState(true)
  useEffect(() => {
    if (isInitialMount) {
      setIsInitialMount(false)
      return
    }
    updateURL(searchTerm, activeFilter, sortConfig, showAnalytics)
  }, [searchTerm, activeFilter, sortConfig, showAnalytics])

  // Fetch all films
  const fetchFilms = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${API_URL}/films`)
      const data = await response.json()
      setFilms(data)
      // Don't set filteredFilms here - let useEffect handle sorting first
    } catch (error) {
      console.error('Error fetching films:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchFilms()
  }, [])

  // Save state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('viewMode', viewMode)
  }, [viewMode])

  useEffect(() => {
    localStorage.setItem('searchTerm', searchTerm)
  }, [searchTerm])

  useEffect(() => {
    localStorage.setItem('activeFilter', JSON.stringify(activeFilter))
  }, [activeFilter])

  useEffect(() => {
    localStorage.setItem('sortConfig', JSON.stringify(sortConfig))
  }, [sortConfig])

  useEffect(() => {
    localStorage.setItem('showAnalytics', showAnalytics)
  }, [showAnalytics])

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

    // Apply year seen filter
    if (filterConfig.yearSeen && filterConfig.yearSeen.length > 0) {
      filtered = filtered.filter(film => {
        if (!film.year_watched) return false

        return filterConfig.yearSeen.some(selectedYear => {
          if (selectedYear === 'Pre-2006') {
            return film.year_watched === 'Pre-2006'
          } else {
            // Match exact year (as string since year_watched can be "Pre-2006")
            return film.year_watched === selectedYear
          }
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
        // Special handling for A-grade movies: use custom ranking if available
        const aIsA = a.letter_rating === 'A'
        const bIsA = b.letter_rating === 'A'
        
        if (aIsA && bIsA) {
          // Both are A-grade: use custom ranking
          const aRank = a.a_grade_rank
          const bRank = b.a_grade_rank
          
          if (aRank !== null && aRank !== undefined && bRank !== null && bRank !== undefined) {
            // Both have ranks: lower rank number = better (rank 1 is best)
            comparison = aRank - bRank
          } else if (aRank !== null && aRank !== undefined) {
            // Only a has rank: a comes first
            comparison = -1
          } else if (bRank !== null && bRank !== undefined) {
            // Only b has rank: b comes first
            comparison = 1
          } else {
            // Neither has rank: fall back to score, then alphabetical
            const aScore = a.score || 0
            const bScore = b.score || 0
            comparison = bScore - aScore
          }
        } else {
          // Not both A-grade: use numeric score field (20 = A+, 19 = A/A+, etc.)
          // Higher score = better rating
          const aScore = a.score || 0
          const bScore = b.score || 0
          comparison = bScore - aScore // Higher score first
        }
      } else if (actualSortBy === 'year') {
        const aYear = parseInt(a.release_year) || 0
        const bYear = parseInt(b.release_year) || 0
        comparison = bYear - aYear // Newer first
      } else if (actualSortBy === 'rt') {
        const aRT = parseInt(a.rotten_tomatoes?.replace('%', '')) || 0
        const bRT = parseInt(b.rotten_tomatoes?.replace('%', '')) || 0
        comparison = bRT - aRT // Higher RT first
      }

      // If primary sort is equal, sort alphabetically by title (numbers before letters)
      if (comparison === 0) {
        comparison = (a.title || '').localeCompare(b.title || '', undefined, { numeric: true, sensitivity: 'base' })
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
    // URL will be updated by useEffect
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
    const newFilters = { rating: [], rt: [], year: [], yearSeen: [], genre: [] }
    setSearchTerm('')
    setActiveFilter(newFilters)
    setSortConfig({ sortBy: '', direction: 'desc' })
    setShowAnalytics(false)

    // Clear localStorage
    localStorage.removeItem('searchTerm')
    localStorage.removeItem('activeFilter')
    localStorage.removeItem('sortConfig')
    localStorage.removeItem('showAnalytics')

    // Clear URL parameters
    navigate('', { replace: true })

    // Apply the reset immediately
    applyFiltersAndSearch('', newFilters)

    // Force child components to remount
    setResetKey(prev => prev + 1)
  }

  // Toggle analytics view
  const handleAnalyticsToggle = () => {
    setShowAnalytics(!showAnalytics)
    // URL will be updated by useEffect
  }
  
  // Check URL for analytics route
  useEffect(() => {
    if (location.pathname === '/analytics') {
      setShowAnalytics(true)
    }
  }, [location.pathname])

  // Check if any filter values are selected
  const hasSelectedFilterValues = () => {
    return activeFilter.rating.length > 0 ||
           activeFilter.rt.length > 0 ||
           activeFilter.year.length > 0 ||
           activeFilter.yearSeen.length > 0 ||
           activeFilter.genre.length > 0
  }

  return (
    <div className="app">
      <div className="sticky-header">
        <div className="container">
          <div className="header-controls">
            <div className={`header-top-row ${hasActiveFilters ? 'filters-active' : ''}`}>
              {!hasActiveFilters && (
                <div className="site-title" onClick={handleReset} style={{ cursor: 'pointer' }}>J-RAYTINGS</div>
              )}
              <div className="search-and-filter">
                <SearchBar
                  key={`search-${resetKey}`}
                  onSearch={handleSearch}
                  totalFilms={films.length}
                  filteredFilms={filteredFilms.length}
                  initialSearchTerm={searchTerm}
                  hasActiveFilters={hasSelectedFilterValues()}
                />
                <SortBar key={`sort-${resetKey}`} onSortChange={handleSortChange} initialSortConfig={sortConfig} />
                <FilterBar
                  key={`filter-${resetKey}`}
                  onFilterChange={handleFilterChange}
                  activeFilter={activeFilter}
                  onActiveFiltersChange={setHasActiveFilters}
                />
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
      </div>
      <div className="container">
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '100px 20px', color: '#666' }}>
            Loading films...
          </div>
        ) : showAnalytics ? (
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
