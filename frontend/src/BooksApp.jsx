import { useState, useEffect, useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import './App.css'
import BookList from './components/BookList'
import BookForm from './components/BookForm'
import SearchBar from './components/SearchBar'
import BookSortBar from './components/BookSortBar'
import BookFilterBar from './components/BookFilterBar'
import BookAnalytics from './components/BookAnalytics'

// Use environment variable for production API URL (Railway backend)
// In development, use local backend
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

function BooksApp() {
  const location = useLocation()
  const navigate = useNavigate()
  
  // Helper function to parse URL query parameters
  const parseQueryParams = () => {
    const params = new URLSearchParams(location.search)
    const search = params.get('search') || ''
    const filters = {
      rating: params.get('rating') ? params.get('rating').split(',') : [],
      type: params.get('type') ? params.get('type').split(',') : [],
      form: params.get('form') ? params.get('form').split(',') : [],
      year: params.get('year') ? params.get('year').split(',') : [],
      author: params.get('author') ? params.get('author').split(',') : [],
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
    if (filters.type.length > 0) params.set('type', filters.type.join(','))
    if (filters.form.length > 0) params.set('form', filters.form.join(','))
    if (filters.year.length > 0) params.set('year', filters.year.join(','))
    if (filters.author.length > 0) params.set('author', filters.author.join(','))
    if (sortConfig.sortBy) {
      params.set('sortBy', sortConfig.sortBy)
      params.set('sortDirection', sortConfig.direction)
    }
    if (showAnalytics) params.set('analytics', 'true')
    
    const newSearch = params.toString()
    const newURL = newSearch ? `?${newSearch}` : ''
    navigate(newURL, { replace: true })
  }
  
  const [books, setBooks] = useState([])
  const [filteredBooks, setFilteredBooks] = useState([])
  const [editingBook, setEditingBook] = useState(null)
  const [showForm, setShowForm] = useState(false)
  
  // Initialize state from URL params or localStorage
  const urlParams = parseQueryParams()
  const [searchTerm, setSearchTerm] = useState(() => {
    return urlParams.search || localStorage.getItem('booksSearchTerm') || ''
  })
  const [activeFilter, setActiveFilter] = useState(() => {
    const hasUrlFilters = urlParams.filters.rating.length > 0 || 
                         urlParams.filters.type.length > 0 ||
                         urlParams.filters.form.length > 0 ||
                         urlParams.filters.year.length > 0 ||
                         urlParams.filters.author.length > 0
    if (hasUrlFilters) {
      return urlParams.filters
    }
    const saved = localStorage.getItem('booksActiveFilter')
    return saved ? JSON.parse(saved) : { rating: [], type: [], form: [], year: [], author: [] }
  })
  const [sortConfig, setSortConfig] = useState(() => {
    if (urlParams.sortBy) {
      return { sortBy: urlParams.sortBy, direction: urlParams.sortDirection }
    }
    const saved = localStorage.getItem('booksSortConfig')
    return saved ? JSON.parse(saved) : { sortBy: '', direction: 'desc' }
  })
  const [viewMode, setViewMode] = useState(() => {
    return localStorage.getItem('booksViewMode') || 'grid'
  })
  const [resetKey, setResetKey] = useState(0)
  const [showAnalytics, setShowAnalytics] = useState(() => {
    return urlParams.analytics || localStorage.getItem('booksShowAnalytics') === 'true'
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

  // Fetch all books
  const fetchBooks = async () => {
    try {
      setIsLoading(true)
      // Add cache-busting to ensure fresh data
      const response = await fetch(`${API_URL}/books?_t=${Date.now()}`, {
        cache: 'no-store'
      })
      const data = await response.json()
      // Debug: log the three books we're tracking
      const trackedBooks = data.filter(b => 
        ['The Right Stuff', 'Animal Farm', 'Confessions of an Advertising Man'].includes(b.book_name)
      )
      if (trackedBooks.length > 0) {
        console.log('Fetched books with updated URLs:', trackedBooks.map(b => ({
          name: b.book_name,
          cover_url: b.cover_url
        })))
      }
      setBooks(data)
      setFilteredBooks(data)
    } catch (error) {
      console.error('Error fetching books:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchBooks()
  }, [])

  // Save state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('booksViewMode', viewMode)
  }, [viewMode])

  useEffect(() => {
    localStorage.setItem('booksSearchTerm', searchTerm)
  }, [searchTerm])

  useEffect(() => {
    localStorage.setItem('booksActiveFilter', JSON.stringify(activeFilter))
  }, [activeFilter])

  useEffect(() => {
    localStorage.setItem('booksSortConfig', JSON.stringify(sortConfig))
  }, [sortConfig])

  useEffect(() => {
    localStorage.setItem('booksShowAnalytics', showAnalytics)
  }, [showAnalytics])

  // Add or update book
  const handleSaveBook = async (bookData) => {
    try {
      const url = editingBook
        ? `${API_URL}/books/${editingBook.id}`
        : `${API_URL}/books`

      const method = editingBook ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookData)
      })

      if (response.ok) {
        fetchBooks()
        setShowForm(false)
        setEditingBook(null)
      }
    } catch (error) {
      console.error('Error saving book:', error)
    }
  }

  // Delete book
  const handleDeleteBook = async (id) => {
    if (!confirm('Are you sure you want to delete this book?')) return

    try {
      const response = await fetch(`${API_URL}/books/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchBooks()
      }
    } catch (error) {
      console.error('Error deleting book:', error)
    }
  }

  // Edit book
  const handleEditBook = (book) => {
    setEditingBook(book)
    setShowForm(true)
  }

  // Apply filters and search
  const applyFiltersAndSearch = useCallback((searchValue, filterConfig) => {
    let filtered = [...books]

    // Apply search (by book name and author)
    if (searchValue) {
      const searchLower = searchValue.toLowerCase()
      filtered = filtered.filter(book => {
        const bookName = (book.book_name || '').toLowerCase()
        const author = (book.author || '').toLowerCase()
        return bookName.includes(searchLower) || author.includes(searchLower)
      })
    }

    // Apply rating filter
    if (filterConfig.rating && filterConfig.rating.length > 0) {
      filtered = filtered.filter(book => {
        return filterConfig.rating.includes(book.j_rayting)
      })
    }

    // Apply type filter
    if (filterConfig.type && filterConfig.type.length > 0) {
      filtered = filtered.filter(book => {
        return filterConfig.type.includes(book.type)
      })
    }

    // Apply form filter
    if (filterConfig.form && filterConfig.form.length > 0) {
      filtered = filtered.filter(book => {
        return filterConfig.form.includes(book.form)
      })
    }

    // Apply year filter (year read)
    if (filterConfig.year && filterConfig.year.length > 0) {
      filtered = filtered.filter(book => {
        if (!book.year) return false
        return filterConfig.year.includes(book.year.toString())
      })
    }

    // Apply author filter
    if (filterConfig.author && filterConfig.author.length > 0) {
      filtered = filtered.filter(book => {
        if (!book.author) return false
        const authorLower = book.author.toLowerCase()
        return filterConfig.author.some(selectedAuthor => {
          return authorLower.includes(selectedAuthor.toLowerCase())
        })
      })
    }

    // Apply sorting
    filtered = sortBooks(filtered, sortConfig)

    setFilteredBooks(filtered)
  }, [books, sortConfig])

  // Sort books based on configuration
  const sortBooks = (booksToSort, config) => {
    const sorted = [...booksToSort]
    const { sortBy, direction } = config

    sorted.sort((a, b) => {
      let comparison = 0

      // Default to rating if no sort is selected
      const actualSortBy = sortBy || 'rating'

      if (actualSortBy === 'rating') {
        // Use numeric score field (higher score = better rating)
        const aScore = a.score || 0
        const bScore = b.score || 0
        comparison = bScore - aScore // Higher score first
      } else if (actualSortBy === 'date') {
        // Date read - parse date_read field and sort by actual date
        const parseDate = (dateStr) => {
          if (!dateStr) return new Date(0) // Put missing dates at the end
          
          // Try YYYY-MM-DD format first
          if (dateStr.includes('-')) {
            const parts = dateStr.split('-')
            if (parts.length === 3) {
              return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
            }
          }
          
          // Try MM/DD/YYYY format
          if (dateStr.includes('/')) {
            const parts = dateStr.split('/')
            if (parts.length === 3) {
              return new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]))
            }
          }
          
          // Try Month-YY format (e.g., "Jan-24")
          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          if (dateStr.includes('-') && dateStr.length <= 7) {
            const parts = dateStr.split('-')
            if (parts.length === 2) {
              const monthIndex = monthNames.indexOf(parts[0])
              if (monthIndex !== -1) {
                const year = 2000 + parseInt(parts[1]) // Assume 20XX
                return new Date(year, monthIndex, 1)
              }
            }
          }
          
          // Fallback: try to parse as-is
          const parsed = new Date(dateStr)
          return isNaN(parsed.getTime()) ? new Date(0) : parsed
        }
        
        const aDate = parseDate(a.date_read)
        const bDate = parseDate(b.date_read)
        comparison = bDate - aDate // Most recent first
      } else if (actualSortBy === 'dateWritten') {
        // Date written - parse published_date field and sort by actual date
        const parseDate = (dateStr) => {
          if (!dateStr) return new Date(0) // Put missing dates at the end
          
          // Try YYYY-MM-DD format first
          if (dateStr.includes('-')) {
            const parts = dateStr.split('-')
            if (parts.length === 3) {
              return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
            }
          }
          
          // Try MM/DD/YYYY format
          if (dateStr.includes('/')) {
            const parts = dateStr.split('/')
            if (parts.length === 3) {
              return new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]))
            }
          }
          
          // Try Month-YY format (e.g., "Jan-24")
          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          if (dateStr.includes('-') && dateStr.length <= 7) {
            const parts = dateStr.split('-')
            if (parts.length === 2) {
              const monthIndex = monthNames.indexOf(parts[0])
              if (monthIndex !== -1) {
                const year = 2000 + parseInt(parts[1]) // Assume 20XX
                return new Date(year, monthIndex, 1)
              }
            }
          }
          
          // If it's just a year (4 digits), use January 1st of that year
          if (/^\d{4}$/.test(dateStr)) {
            return new Date(parseInt(dateStr), 0, 1)
          }
          
          // Fallback: try to parse as-is
          const parsed = new Date(dateStr)
          return isNaN(parsed.getTime()) ? new Date(0) : parsed
        }
        
        const aDate = parseDate(a.published_date)
        const bDate = parseDate(b.published_date)
        comparison = bDate - aDate // Most recent first
      } else if (actualSortBy === 'pages') {
        // Pages
        const aPages = a.pages || 0
        const bPages = b.pages || 0
        comparison = bPages - aPages // More pages first
      }

      // If primary sort is equal, sort alphabetically by book name
      if (comparison === 0) {
        comparison = (a.book_name || '').localeCompare(b.book_name || '', undefined, { numeric: true, sensitivity: 'base' })
      }

      // For desc (best first): keep comparison as is
      // For asc (worst first): reverse it
      return direction === 'desc' ? comparison : -comparison
    })

    return sorted
  }

  // Search books
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

  // Re-apply filters when books data changes
  useEffect(() => {
    applyFiltersAndSearch(searchTerm, activeFilter)
  }, [books, sortConfig, searchTerm, activeFilter, applyFiltersAndSearch])

  // Reset to home experience
  const handleReset = () => {
    // Clear all filters and search
    const newFilters = { rating: [], type: [], form: [], year: [], author: [] }
    setSearchTerm('')
    setActiveFilter(newFilters)
    setSortConfig({ sortBy: '', direction: 'desc' })
    setShowAnalytics(false)

    // Clear localStorage
    localStorage.removeItem('booksSearchTerm')
    localStorage.removeItem('booksActiveFilter')
    localStorage.removeItem('booksSortConfig')
    localStorage.removeItem('booksShowAnalytics')

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
  }
  
  // Check URL for analytics route
  useEffect(() => {
    if (location.pathname === '/books/analytics' || location.pathname === '/analytics') {
      setShowAnalytics(true)
    }
  }, [location.pathname])

  // Check if any filter values are selected
  const hasSelectedFilterValues = () => {
    return activeFilter.rating.length > 0 ||
           activeFilter.type.length > 0 ||
           activeFilter.form.length > 0 ||
           activeFilter.year.length > 0 ||
           activeFilter.author.length > 0
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
                  totalFilms={books.length}
                  filteredFilms={filteredBooks.length}
                  initialSearchTerm={searchTerm}
                  hasActiveFilters={hasSelectedFilterValues()}
                  itemName="books"
                />
                <BookSortBar key={`sort-${resetKey}`} onSortChange={handleSortChange} initialSortConfig={sortConfig} />
                <BookFilterBar
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
            Loading books...
          </div>
        ) : showAnalytics ? (
          <BookAnalytics />
        ) : (
          <BookList
            books={filteredBooks}
            onEdit={handleEditBook}
            onDelete={handleDeleteBook}
            viewMode={viewMode}
          />
        )}
      </div>
      {showForm && (
        <BookForm
          book={editingBook}
          onSave={handleSaveBook}
          onCancel={() => {
            setShowForm(false)
            setEditingBook(null)
          }}
        />
      )}
    </div>
  )
}

export default BooksApp

