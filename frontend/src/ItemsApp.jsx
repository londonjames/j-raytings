import { useState, useEffect, useCallback, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import './App.css'
import SearchBar from './components/SearchBar'

// Detect if we're accessing from network IP and use that for API, otherwise use localhost
const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // If accessing from network IP (not localhost), use network IP for API too
  const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:5001/api`
  }
  return 'http://localhost:5001/api'
}
const API_URL = getApiUrl()

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

  // Update meta tags for social sharing (Open Graph and Twitter)
  useEffect(() => {
    const baseUrl = 'https://jamesraybould.me'
    const pageUrl = `${baseUrl}/${config.type}`
    const pageTitle = config.pageTitles.main
    const description = config.type === 'films'
      ? 'Browse my collection of over 1700 films I\'ve watched, each with my own J-Rayting. And if you\'re super geeky, you can filter by Rotten Tomatoes score, Year, genre, and more.'
      : config.type === 'books'
      ? 'Browse my personal collection of over 700 books I\'ve read, each with my own J-Rayting. And if you\'re super geeky, you can skim my short summaries or even dig into my comprehensive Notion pages with all my Amazon Kindle highlights.'
      : 'Browse my collection of TV shows I\'ve watched, each with my own J-Rayting. Filter by IMDB rating, genre, decade, and read my thoughts on each show.'
    const imageUrl = `${baseUrl}/${config.type}-quilt-social.jpg?v2`

    // Helper function to update or create meta tag
    const updateMetaTag = (property, content, isProperty = true) => {
      const attribute = isProperty ? 'property' : 'name'
      let meta = document.querySelector(`meta[${attribute}="${property}"]`)
      if (!meta) {
        meta = document.createElement('meta')
        meta.setAttribute(attribute, property)
        document.head.appendChild(meta)
      }
      meta.setAttribute('content', content)
    }

    // Update Open Graph tags
    updateMetaTag('og:type', 'website')
    updateMetaTag('og:url', pageUrl)
    updateMetaTag('og:title', pageTitle)
    updateMetaTag('og:description', description)
    updateMetaTag('og:image', imageUrl)

    // Update Twitter Card tags
    updateMetaTag('twitter:card', 'summary_large_image', false)
    updateMetaTag('twitter:url', pageUrl, false)
    updateMetaTag('twitter:title', pageTitle, false)
    updateMetaTag('twitter:description', description, false)
    updateMetaTag('twitter:image', imageUrl, false)
  }, [config.type, config.pageTitles, config.titlePlural])

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
  const updateURL = useCallback((search, filters, sortConfig, showAnalytics) => {
    const params = new URLSearchParams()

    if (search && search.trim()) params.set('search', search.trim())

    // Add all filter parameters dynamically
    Object.keys(filters).forEach(key => {
      if (filters[key] && Array.isArray(filters[key]) && filters[key].length > 0) {
        params.set(key, filters[key].join(','))
      }
    })

    if (sortConfig.sortBy) {
      params.set('sortBy', sortConfig.sortBy)
      params.set('sortDirection', sortConfig.direction || 'desc')
    }
    if (showAnalytics) params.set('analytics', 'true')

    const newSearch = params.toString()
    const newURL = newSearch ? `?${newSearch}` : ''
    // Use replace: true to update URL without adding to history
    // This allows sharing URLs with filters/sort/search
    navigate(newURL, { replace: true })
  }, [navigate])

  const [items, setItems] = useState([])
  const [filteredItems, setFilteredItems] = useState([])
  const [editingItem, setEditingItem] = useState(null)
  const [showForm, setShowForm] = useState(false)

  // Initialize state from URL params only (no localStorage for user preferences)
  const urlParams = parseQueryParams()
  const [searchTerm, setSearchTerm] = useState(() => {
    return urlParams.search || ''
  })
  const [activeFilter, setActiveFilter] = useState(() => {
    const hasUrlFilters = Object.keys(urlParams.filters).some(key => urlParams.filters[key].length > 0)
    if (hasUrlFilters) {
      return urlParams.filters
    }
    return config.filterFields // Default empty filters
  })
  const [sortConfig, setSortConfig] = useState(() => {
    if (urlParams.sortBy) {
      return { sortBy: urlParams.sortBy, direction: urlParams.sortDirection }
    }
    return { sortBy: '', direction: 'desc' } // Default
  })
  const [viewMode, setViewMode] = useState(() => {
    // On mobile, always default to list view
    if (window.innerWidth < 500) {
      return 'list'
    }
    return 'grid' // Default, no localStorage
  })
  const [resetKey, setResetKey] = useState(0)
  const [showAnalytics, setShowAnalytics] = useState(() => {
    return urlParams.analytics || false
  })
  const [hasActiveFilters, setHasActiveFilters] = useState(false)
  
  // Calculate initial filter count from activeFilter - dynamic based on config
  const calculateInitialFilterCount = () => {
    let count = 0
    Object.keys(activeFilter).forEach(key => {
      if (activeFilter[key]?.length > 0) count++
    })
    return count
  }

  const [filterCount, setFilterCount] = useState(calculateInitialFilterCount)
  const [filterRows, setFilterRows] = useState(0) // Track actual number of rows when filters wrap

  // Update filterCount when activeFilter changes - dynamic calculation
  useEffect(() => {
    let count = 0
    Object.keys(activeFilter).forEach(key => {
      if (activeFilter[key]?.length > 0) count++
    })
    setFilterCount(count)
  }, [activeFilter])

  const [isLoading, setIsLoading] = useState(true)
  const [hasLoadedOnce, setHasLoadedOnce] = useState(false)

  // Track if we're updating from URL to prevent loops
  const isUpdatingFromURL = useRef(false)

  // Sync state from URL when URL changes (e.g., user navigates to clean URL or removes params)
  // This ensures that when URL is clean, state resets to defaults
  useEffect(() => {
    const currentUrlParams = parseQueryParams()
    
    // Set flag to prevent URL update effect from running
    isUpdatingFromURL.current = true
    
    // Update search term from URL
    setSearchTerm(currentUrlParams.search || '')
    
    // Update filters from URL - if URL has no filters, use defaults
    const hasUrlFilters = Object.keys(currentUrlParams.filters).some(key => currentUrlParams.filters[key].length > 0)
    if (hasUrlFilters) {
      setActiveFilter(currentUrlParams.filters)
    } else {
      // URL has no filters - reset to defaults
      setActiveFilter(config.filterFields)
    }
    
    // Update sort from URL - if URL has no sort, use defaults
    if (currentUrlParams.sortBy) {
      setSortConfig({ sortBy: currentUrlParams.sortBy, direction: currentUrlParams.sortDirection })
    } else {
      // URL has no sort - reset to default
      setSortConfig({ sortBy: '', direction: 'desc' })
    }
    
    // Update analytics from URL
    setShowAnalytics(currentUrlParams.analytics || false)
    
    // Reset flag after state updates complete
    setTimeout(() => {
      isUpdatingFromURL.current = false
    }, 0)
  }, [location.search, config]) // Watch URL changes

  // Update URL when state changes (skip initial mount and when updating from URL)
  const [isInitialMount, setIsInitialMount] = useState(true)
  useEffect(() => {
    if (isInitialMount) {
      setIsInitialMount(false)
      return
    }
    // Don't update URL if we're currently syncing from URL
    if (isUpdatingFromURL.current) {
      return
    }
    updateURL(searchTerm, activeFilter, sortConfig, showAnalytics)
  }, [searchTerm, activeFilter, sortConfig, showAnalytics, updateURL])

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

  // Note: Removed localStorage persistence for user preferences (search, filters, sort, view mode, analytics)
  // Each visitor now gets a clean state. URL params are still used for shareable links.
  // Data cache (cachedFilms/cachedBooks) is still used for performance.

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
          decade: config.applyDecadeFilter,
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
    // applyFiltersAndSearch will be called by useEffect when activeFilter changes
  }

  // Handle sort change
  const handleSortChange = (newSortConfig) => {
    setSortConfig(newSortConfig)
    // applyFiltersAndSearch will be called by useEffect when sortConfig changes
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

    // Clear any old localStorage data (cleanup for legacy data)
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

  // Calculate filter count from activeFilter directly as fallback - dynamic
  const calculateFilterCount = () => {
    let count = 0
    Object.keys(activeFilter).forEach(key => {
      if (activeFilter[key]?.length > 0) count++
    })
    return count
  }

  // Use filterCount from FilterBar, or calculate as fallback
  const actualFilterCount = filterCount > 0 ? filterCount : calculateFilterCount()
  const shouldShowFilters = hasActiveFilters || actualFilterCount > 0
  const filterCountClass = actualFilterCount > 0 ? `filter-count-${Math.min(actualFilterCount, 3)}` : ''

  // Calculate padding based on actual filter rows (when they wrap) or filter count
  // Use rows if available (when wrapping), otherwise use count
  const actualRows = filterRows > 0 ? filterRows : (actualFilterCount > 0 ? 1 : 0)
  
  const getPaddingTop = () => {
    if (actualRows === 0) return undefined
    
    // Calculate padding based on rows: base (75px) + (rows * ~45px per row)
    // Each row is ~36px button height + 8px gap = 44px, plus some spacing
    const basePadding = 75 // Base header height
    const rowHeight = 45 // Height per filter row (button + gap + spacing)
    const padding = basePadding + (actualRows * rowHeight)
    return `${padding}px`
  }
  
  const paddingTop = getPaddingTop()
  const style = paddingTop ? { paddingTop } : undefined

  // Also update header-controls padding-bottom based on rows
  // Add more space below filter buttons (above gray line) when they wrap
  const headerControlsStyle = actualRows > 0 ? {
    paddingBottom: `${0.5 + (actualRows * 2.75)}rem` // 0.5rem base (8px) + 2.75rem per row - reduced base to move gray line up slightly
  } : undefined

  // Reduce space between gray line and films when filters are active
  const containerStyle = actualRows > 0 ? {
    paddingTop: '0.5rem' // 8px - reduced spacing when filters are active
  } : undefined

  return (
    <div 
      className={`app ${shouldShowFilters ? 'filters-active' : ''} ${filterCountClass}`.trim()}
      style={style}
    >
      <div className="sticky-header">
        <div className="container">
          <div className="header-controls" style={headerControlsStyle}>
            {/* SINGLE FIXED ROW: J-RAYTINGS + Search/Sort/Filter/Analytics + View Controls - NEVER CHANGES */}
            <div className="header-top-row">
              <div className="site-title" onClick={handleReset} style={{ cursor: 'pointer' }}>J-RAYTINGS</div>
              <div className="search-and-filter-wrapper">
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
                    onFilterCountChange={setFilterCount}
                    onFilterRowsChange={setFilterRows}
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
                  {/* View controls - on mobile, appears here (where analytics is); on desktop, appears on right */}
                  <div className="view-controls view-controls-mobile">
                <button
                  className="view-btn active"
                  onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                  title={viewMode === 'grid' ? 'Switch to list view' : 'Switch to grid view'}
                >
                  {viewMode === 'grid' ? (
                    // Show grid icon when in grid mode
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <rect x="2" y="2" width="6" height="6" rx="1"/>
                      <rect x="12" y="2" width="6" height="6" rx="1"/>
                      <rect x="2" y="12" width="6" height="6" rx="1"/>
                      <rect x="12" y="12" width="6" height="6" rx="1"/>
                    </svg>
                  ) : (
                    // Show list icon when in list mode
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <rect x="2" y="3" width="16" height="2" rx="1"/>
                      <rect x="2" y="9" width="16" height="2" rx="1"/>
                      <rect x="2" y="15" width="16" height="2" rx="1"/>
                    </svg>
                  )}
                </button>
                  </div>
                </div>
              </div>
              {/* View controls for desktop - hidden on mobile */}
              <div className="view-controls view-controls-desktop">
                <button
                  className="view-btn active"
                  onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                  title={viewMode === 'grid' ? 'Switch to list view' : 'Switch to grid view'}
                >
                  {viewMode === 'grid' ? (
                    // Show grid icon when in grid mode
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <rect x="2" y="2" width="6" height="6" rx="1"/>
                      <rect x="12" y="2" width="6" height="6" rx="1"/>
                      <rect x="2" y="12" width="6" height="6" rx="1"/>
                      <rect x="12" y="12" width="6" height="6" rx="1"/>
                    </svg>
                  ) : (
                    // Show list icon when in list mode
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <rect x="2" y="3" width="16" height="2" rx="1"/>
                      <rect x="2" y="9" width="16" height="2" rx="1"/>
                      <rect x="2" y="15" width="16" height="2" rx="1"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="container" style={containerStyle}>
        {!hasLoadedOnce ? (
          <div className="loading-placeholder" style={{ minHeight: '80vh' }} />
        ) : showAnalytics ? (
          <Analytics />
        ) : filteredItems.length > 0 ? (
          <List
            {...(config.type === 'films' ? { films: filteredItems } : config.type === 'books' ? { books: filteredItems } : { shows: filteredItems })}
            onEdit={handleEditItem}
            onDelete={handleDeleteItem}
            viewMode={viewMode}
          />
        ) : (searchTerm || hasSelectedFilterValues()) ? (
          // Only show empty state message if user is actively filtering or searching
          <div className="empty-state">
            <p>{config.emptyState.message}</p>
            <p className="empty-state-hint">{config.emptyState.hint}</p>
          </div>
        ) : (
          // If no search/filters and no items, show nothing (black screen)
          null
        )}
      </div>
      {showForm && (
        <Form
          {...(config.type === 'films' ? { film: editingItem } : config.type === 'books' ? { book: editingItem } : { show: editingItem })}
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
