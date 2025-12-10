import { useState, useEffect, useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import './App.css'
import SearchBar from './components/SearchBar'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

// Consolidated component for both films and books
function ItemsApp({ config }) {
  const location = useLocation()
  const navigate = useNavigate()

  // Extract components from config
  const { List, Form, SortBar, FilterBar, Analytics } = config.components

  // Update page title based on route
  useEffect(() => {
    if (location.pathname.includes('/admin')) {
      document.title = config.pageTitles.admin
    } else {
      document.title = config.pageTitles.main
    }
  }, [location.pathname, config.pageTitles])

  // Helper function to parse URL query parameters
  const parseQueryParams = () => {
    const params = new URLSearchParams(location.search)
    const search = params.get('search') || ''

    // Build filters dynamically from config
    const filters = {}
    Object.keys(config.filterFields).forEach(key => {
      filters[key] = params.get(key) ? params.get(key).split(',') : []
    })

    const sortBy = params.get('sortBy') || ''
    const sortDirection = params.get('sortDirection') || 'desc'
    const analytics = params.get('analytics') === 'true'

    return { search, filters, sortBy, sortDirection, analytics }
  }

  // Helper function to update URL with current state
  const updateURL = (search, filters, sortConfig, showAnalytics) => {
    const params = new URLSearchParams()

    if (search) params.set('search', search)

    // Add all filter parameters dynamically
    Object.keys(filters).forEach(key => {
      if (filters[key].length > 0) {
        params.set(key, filters[key].join(','))
      }
    })

    if (sortConfig.sortBy) {
      params.set('sortBy', sortConfig.sortBy)
      params.set('sortDirection', sortConfig.direction)
    }
    if (showAnalytics) params.set('analytics', 'true')

    const newSearch = params.toString()
    const newURL = newSearch ? `?${newSearch}` : ''
    navigate(newURL, { replace: true })
  }

  const [items, setItems] = useState([])
  const [filteredItems, setFilteredItems] = useState([])
  const [editingItem, setEditingItem] = useState(null)
  const [showForm, setShowForm] = useState(false)

  // Initialize state from URL params or localStorage
  const urlParams = parseQueryParams()
  const [searchTerm, setSearchTerm] = useState(() => {
    return urlParams.search || localStorage.getItem(config.localStorageKeys.searchTerm) || ''
  })
  const [activeFilter, setActiveFilter] = useState(() => {
    const hasUrlFilters = Object.keys(urlParams.filters).some(key => urlParams.filters[key].length > 0)
    if (hasUrlFilters) {
      return urlParams.filters
    }
    const saved = localStorage.getItem(config.localStorageKeys.activeFilter)
    return saved ? JSON.parse(saved) : config.filterFields
  })
  const [sortConfig, setSortConfig] = useState(() => {
    if (urlParams.sortBy) {
      return { sortBy: urlParams.sortBy, direction: urlParams.sortDirection }
    }
    const saved = localStorage.getItem(config.localStorageKeys.sortConfig)
    return saved ? JSON.parse(saved) : { sortBy: '', direction: 'desc' }
  })
  const [viewMode, setViewMode] = useState(() => {
    // On mobile, always default to list view
    if (window.innerWidth < 500) {
      return 'list'
    }

    const savedViewMode = localStorage.getItem(config.localStorageKeys.viewMode)
    if (savedViewMode) {
      return savedViewMode
    }

    return 'grid'
  })
  const [resetKey, setResetKey] = useState(0)
  const [showAnalytics, setShowAnalytics] = useState(() => {
    return urlParams.analytics || localStorage.getItem(config.localStorageKeys.showAnalytics) === 'true'
  })
  const [hasActiveFilters, setHasActiveFilters] = useState(false)

  const [isLoading, setIsLoading] = useState(true)
  const [hasLoadedOnce, setHasLoadedOnce] = useState(false)

  // Update URL when state changes (skip initial mount)
  const [isInitialMount, setIsInitialMount] = useState(true)
  useEffect(() => {
    if (isInitialMount) {
      setIsInitialMount(false)
      return
    }
    updateURL(searchTerm, activeFilter, sortConfig, showAnalytics)
  }, [searchTerm, activeFilter, sortConfig, showAnalytics])

  // Fetch all items
  const fetchItems = async () => {
    try {
      // Try to load from cache first
      const cached = localStorage.getItem(config.cacheKey)
      if (cached) {
        try {
          const cachedData = JSON.parse(cached)
          if (cachedData && Array.isArray(cachedData) && cachedData.length > 0) {
            setItems(cachedData)
            setIsLoading(false)
          }
        } catch (e) {
          console.error(`Error parsing cached ${config.type}:`, e)
        }
      }

      // Fetch fresh data
      const cacheParam = config.type === 'books' ? `?_t=${Date.now()}` : ''
      const fetchOptions = config.type === 'books' ? { cache: 'no-store' } : {}

      const response = await fetch(`${API_URL}/${config.apiEndpoint}${cacheParam}`, fetchOptions)
      const data = await response.json()

      if (data && Array.isArray(data) && data.length > 0) {
        setItems(data)
        setIsLoading(false)
        setHasLoadedOnce(true)

        try {
          localStorage.setItem(config.cacheKey, JSON.stringify(data))
        } catch (e) {
          console.error(`Error caching ${config.type}:`, e)
        }
      }
    } catch (error) {
      console.error(`Error fetching ${config.type}:`, error)
      setIsLoading(false)
      setHasLoadedOnce(true)
    }
  }

  useEffect(() => {
    fetchItems()
  }, [])

  // Save state to localStorage
  useEffect(() => {
    localStorage.setItem(config.localStorageKeys.viewMode, viewMode)
  }, [viewMode])

  useEffect(() => {
    localStorage.setItem(config.localStorageKeys.searchTerm, searchTerm)
  }, [searchTerm])

  useEffect(() => {
    localStorage.setItem(config.localStorageKeys.activeFilter, JSON.stringify(activeFilter))
  }, [activeFilter])

  useEffect(() => {
    localStorage.setItem(config.localStorageKeys.sortConfig, JSON.stringify(sortConfig))
  }, [sortConfig])

  useEffect(() => {
    localStorage.setItem(config.localStorageKeys.showAnalytics, showAnalytics)
  }, [showAnalytics])

  // Add or update item
  const handleSaveItem = async (itemData) => {
    try {
      const url = editingItem
        ? `${API_URL}/${config.apiEndpoint}/${editingItem.id}`
        : `${API_URL}/${config.apiEndpoint}`

      const method = editingItem ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(itemData)
      })

      if (response.ok) {
        fetchItems()
        setShowForm(false)
        setEditingItem(null)
      }
    } catch (error) {
      console.error(`Error saving ${config.type}:`, error)
    }
  }

  // Delete item
  const handleDeleteItem = async (id) => {
    if (!confirm(`Are you sure you want to delete this ${config.titleSingular.toLowerCase()}?`)) return

    try {
      const response = await fetch(`${API_URL}/${config.apiEndpoint}/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchItems()
      }
    } catch (error) {
      console.error(`Error deleting ${config.type}:`, error)
    }
  }

  // Edit item
  const handleEditItem = (item) => {
    setEditingItem(item)
    setShowForm(true)
  }

  // Apply filters and search
  const applyFiltersAndSearch = useCallback((searchValue, filterConfig) => {
    let filtered = [...items]

    // Apply search
    if (searchValue) {
      const searchLower = searchValue.toLowerCase()
      filtered = filtered.filter(item =>
        config.searchFilter(item, searchLower, config.formatTitle)
      )
    }

    // Apply each filter type dynamically
    Object.keys(filterConfig).forEach(filterType => {
      if (filterConfig[filterType] && filterConfig[filterType].length > 0) {
        // Map filter types to their config functions
        const filterFunctionMap = {
          rating: config.applyRatingFilter,
          rt: config.applyRtFilter,
          year: config.applyYearFilter,
          yearSeen: config.applyYearSeenFilter,
          genre: config.applyGenreFilter,
          type: config.applyTypeFilter,
          form: config.applyFormFilter,
          author: config.applyAuthorFilter,
        }

        const filterFunction = filterFunctionMap[filterType]
        if (filterFunction) {
          filtered = filterFunction(filtered, filterConfig[filterType])
        }
      }
    })

    // Apply sorting
    filtered = config.sortItems(filtered, sortConfig.sortBy, sortConfig.direction)

    setFilteredItems(filtered)
  }, [items, sortConfig, config])

  // Search items
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

  // Re-apply filters when items data changes
  useEffect(() => {
    applyFiltersAndSearch(searchTerm, activeFilter)
  }, [items, sortConfig, searchTerm, activeFilter, applyFiltersAndSearch])

  // Reset to home experience
  const handleReset = () => {
    const newFilters = config.filterFields
    setSearchTerm('')
    setActiveFilter(newFilters)
    setSortConfig({ sortBy: '', direction: 'desc' })
    setShowAnalytics(false)

    // Clear localStorage
    Object.values(config.localStorageKeys).forEach(key => {
      localStorage.removeItem(key)
    })

    navigate('', { replace: true })
    applyFiltersAndSearch('', newFilters)
    setResetKey(prev => prev + 1)
  }

  // Toggle analytics view
  const handleAnalyticsToggle = () => {
    setShowAnalytics(!showAnalytics)
  }

  // Check URL for analytics route
  useEffect(() => {
    if (location.pathname.includes('/analytics')) {
      setShowAnalytics(true)
    }
  }, [location.pathname])

  // Check if any filter values are selected
  const hasSelectedFilterValues = () => {
    return Object.keys(activeFilter).some(key => activeFilter[key].length > 0)
  }

  return (
    <div className="app">
      <div className="sticky-header">
        <div className="container">
          <div className="header-controls">
            <div className={`header-top-row ${hasActiveFilters ? 'filters-active' : ''}`}>
              <div className="site-title" onClick={handleReset} style={{ cursor: 'pointer' }}>J-RAYTINGS</div>
              <div className="search-and-filter">
                <SearchBar
                  key={`search-${resetKey}`}
                  onSearch={handleSearch}
                  totalFilms={items.length}
                  filteredFilms={filteredItems.length}
                  initialSearchTerm={searchTerm}
                  hasActiveFilters={hasSelectedFilterValues()}
                  itemName={config.type}
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
        {!hasLoadedOnce ? (
          <div className="loading-placeholder" style={{ minHeight: '80vh' }} />
        ) : showAnalytics ? (
          <Analytics />
        ) : filteredItems.length > 0 ? (
          <List
            {...(config.type === 'films' ? { films: filteredItems } : { books: filteredItems })}
            onEdit={handleEditItem}
            onDelete={handleDeleteItem}
            viewMode={viewMode}
          />
        ) : (
          <div className="empty-state">
            <p>{config.emptyState.message}</p>
            <p className="empty-state-hint">{config.emptyState.hint}</p>
          </div>
        )}
      </div>
      {showForm && (
        <Form
          {...(config.type === 'films' ? { film: editingItem } : { book: editingItem })}
          onSave={handleSaveItem}
          onCancel={() => {
            setShowForm(false)
            setEditingItem(null)
          }}
        />
      )}
    </div>
  )
}

export default ItemsApp
