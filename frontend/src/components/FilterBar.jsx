import { useState, useEffect, useRef } from 'react'

function FilterBar({ onFilterChange, activeFilter: propActiveFilter, onActiveFiltersChange, onFilterCountChange, onFilterRowsChange }) {
  const [showMainDropdown, setShowMainDropdown] = useState(false)
  const [openDropdowns, setOpenDropdowns] = useState({
    rating: false,
    rt: false,
    year: false,
    yearSeen: false,
    genre: false
  })
  const dropdownRef = useRef(null)
  const filterWrapperRef = useRef(null)
  const filterStackRef = useRef(null)
  const showMainDropdownRef = useRef(showMainDropdown)
  const openDropdownsRef = useRef(openDropdowns)
  
  // Keep refs in sync with state
  useEffect(() => {
    showMainDropdownRef.current = showMainDropdown
  }, [showMainDropdown])
  
  useEffect(() => {
    openDropdownsRef.current = openDropdowns
  }, [openDropdowns])
  const [activeFilters, setActiveFilters] = useState({
    rating: false,
    rt: false,
    year: false,
    yearSeen: false,
    genre: false
  })
  const [selectedFilters, setSelectedFilters] = useState(() => {
    if (propActiveFilter) {
      return {
        rating: propActiveFilter.rating || [],
        rt: propActiveFilter.rt || [],
        year: propActiveFilter.year || [],
        yearSeen: propActiveFilter.yearSeen || [],
        genre: propActiveFilter.genre || []
      }
    }
    return {
      rating: [],
      rt: [],
      year: [],
      yearSeen: [],
      genre: []
    }
  })

  // On mount and when propActiveFilter changes, set activeFilters
  useEffect(() => {
    if (propActiveFilter) {
      const newActiveFilters = {
        rating: (propActiveFilter.rating?.length || 0) > 0,
        rt: (propActiveFilter.rt?.length || 0) > 0,
        year: (propActiveFilter.year?.length || 0) > 0,
        yearSeen: (propActiveFilter.yearSeen?.length || 0) > 0,
        genre: (propActiveFilter.genre?.length || 0) > 0
      }
      setActiveFilters(newActiveFilters)
      // Immediately notify about count
      if (onFilterCountChange) {
        const count = Object.values(newActiveFilters).filter(Boolean).length
        onFilterCountChange(count)
      }
    }
  }, [propActiveFilter, onFilterCountChange])

  // Check if any filters are active
  const hasActiveFilters = () => {
    return activeFilters.rating ||
           activeFilters.rt ||
           activeFilters.year ||
           activeFilters.yearSeen ||
           activeFilters.genre
  }

  // Count active filters
  const countActiveFilters = () => {
    let count = 0
    if (activeFilters.rating) count++
    if (activeFilters.rt) count++
    if (activeFilters.year) count++
    if (activeFilters.yearSeen) count++
    if (activeFilters.genre) count++
    return count
  }

  // Calculate number of rows based on actual height
  const calculateFilterRows = () => {
    if (!filterStackRef.current) return 0
    const stack = filterStackRef.current
    const height = stack.offsetHeight
    const singleRowHeight = 36 + 8 // button height (36px) + gap (0.5rem = 8px)
    const rows = Math.ceil(height / singleRowHeight)
    return Math.max(1, Math.min(rows, 3)) // At least 1 row, max 3 rows
  }

  // Notify parent when activeFilters changes
  useEffect(() => {
    if (onActiveFiltersChange) {
      const hasAnyActive = activeFilters.rating ||
                          activeFilters.rt ||
                          activeFilters.year ||
                          activeFilters.yearSeen ||
                          activeFilters.genre
      onActiveFiltersChange(hasAnyActive)
    }
    // Also notify about filter count
    if (onFilterCountChange) {
      const count = countActiveFilters()
      onFilterCountChange(count)
    }
  }, [activeFilters, onActiveFiltersChange, onFilterCountChange])

  // Measure filter rows and notify parent when they change
  useEffect(() => {
    if (!onFilterRowsChange) return
    
    if (!hasActiveFilters()) {
      // Reset to 0 when no filters
      onFilterRowsChange(0)
      return
    }
    
    // Use setTimeout to ensure DOM has updated
    const timeoutId = setTimeout(() => {
      const rows = calculateFilterRows()
      if (onFilterRowsChange) {
        onFilterRowsChange(rows)
      }
    }, 100) // Small delay to ensure layout has settled

    return () => clearTimeout(timeoutId)
  }, [activeFilters, onFilterRowsChange, hasActiveFilters])

  // Also measure on window resize
  useEffect(() => {
    if (!onFilterRowsChange) return
    
    let resizeTimeout
    const handleResize = () => {
      if (!hasActiveFilters()) {
        onFilterRowsChange(0)
        return
      }
      
      // Debounce resize
      clearTimeout(resizeTimeout)
      resizeTimeout = setTimeout(() => {
        const rows = calculateFilterRows()
        if (onFilterRowsChange) {
          onFilterRowsChange(rows)
        }
      }, 150)
    }

    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      clearTimeout(resizeTimeout)
    }
  }, [activeFilters, onFilterRowsChange, hasActiveFilters])

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Check if any dropdown is actually visible in the DOM
      const mainDropdown = document.querySelector('.filter-main-dropdown')
      const checkboxDropdowns = document.querySelectorAll('.filter-checkbox-dropdown')
      const hasVisibleDropdown = mainDropdown || checkboxDropdowns.length > 0
      
      if (!hasVisibleDropdown) return
      
      const target = event.target
      
      // Check if click is on an ACTUAL filter element (button, dropdown, checkbox)
      // NOT on empty space within container divs
      // This is important: clicking empty space in the filter row should close the dropdown
      const clickedOnFilterElement = 
        // Main filter button (icon)
        target.closest('.filter-button') ||
        // Filter type buttons (By J-Rayting, By RT, etc.)
        target.closest('.filter-type-button') ||
        // Dropdown menus themselves
        target.closest('.filter-main-dropdown') ||
        target.closest('.filter-checkbox-dropdown') ||
        // Options inside dropdowns
        target.closest('.filter-add-option') ||
        // Checkboxes and labels
        target.closest('.filter-checkbox-label') ||
        target.closest('.filter-checkbox') ||
        target.closest('input[type="checkbox"]') ||
        // Clear filters button
        target.closest('.clear-all-filters-btn') ||
        // Only check dropdownRef if clicking on actual button/dropdown inside it
        (dropdownRef.current && dropdownRef.current.contains(target) && 
         (target.closest('.filter-button') || target.closest('.filter-main-dropdown')))
      
      // Simple rule: if NOT clicked on an actual filter element, close ALL dropdowns
      // This includes clicks on empty space in the filter row, navbar elements, or anywhere else
      if (!clickedOnFilterElement) {
        setOpenDropdowns({
          rating: false,
          rt: false,
          year: false,
          yearSeen: false,
          genre: false
        })
        setShowMainDropdown(false)
      }
    }

    // Listen for mouse, touch, and click events
    // Use capture phase to catch events early
    document.addEventListener('mousedown', handleClickOutside, true)
    document.addEventListener('touchstart', handleClickOutside, true)
    document.addEventListener('click', handleClickOutside, true)
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside, true)
      document.removeEventListener('touchstart', handleClickOutside, true)
      document.removeEventListener('click', handleClickOutside, true)
    }
  }, []) // Empty deps - check DOM directly

  const toggleMainDropdown = (e) => {
    if (e) {
      e.stopPropagation() // Prevent event from bubbling to document
    }
    setShowMainDropdown(!showMainDropdown)
  }

  const toggleDropdown = (type, e) => {
    if (e) {
      e.stopPropagation() // Prevent event from bubbling to document
    }
    setOpenDropdowns(prev => {
      const isCurrentlyOpen = prev[type]
      // Close all dropdowns
      const allClosed = {
        rating: false,
        rt: false,
        year: false,
        yearSeen: false,
        genre: false
      }
      // If the clicked one was closed, open it. If it was open, keep all closed.
      return {
        ...allClosed,
        [type]: !isCurrentlyOpen
      }
    })
  }

  const handleValueToggle = (type, value) => {
    console.log('FilterBar handleValueToggle called:', type, value, selectedFilters)
    const newSelectedFilters = { ...selectedFilters }

    if (newSelectedFilters[type].includes(value)) {
      newSelectedFilters[type] = newSelectedFilters[type].filter(v => v !== value)
    } else {
      newSelectedFilters[type] = [...newSelectedFilters[type], value]
    }

    setSelectedFilters(newSelectedFilters)
    onFilterChange(newSelectedFilters)
  }

  const handleClear = () => {
    setSelectedFilters({
      rating: [],
      rt: [],
      year: [],
      yearSeen: [],
      genre: []
    })
    setActiveFilters({
      rating: false,
      rt: false,
      year: false,
      yearSeen: false,
      genre: false
    })
    onFilterChange({
      rating: [],
      rt: [],
      year: [],
      yearSeen: [],
      genre: []
    })
  }

  const handleRemoveFilter = (type, value) => {
    const newSelectedFilters = { ...selectedFilters }
    newSelectedFilters[type] = newSelectedFilters[type].filter(v => v !== value)
    setSelectedFilters(newSelectedFilters)
    onFilterChange(newSelectedFilters)
  }

  const hasSelectedValues = () => {
    return selectedFilters.rating.length > 0 ||
           selectedFilters.rt.length > 0 ||
           selectedFilters.year.length > 0 ||
           selectedFilters.yearSeen.length > 0 ||
           selectedFilters.genre.length > 0
  }

  // Rating options: A+, A, A-, B+, B, B-, C+, C, C-, D+, D
  const ratingOptions = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']

  // Year ranges (for film release year)
  const yearRanges = [
    '2020s',
    '2010s',
    '2000s',
    '1990s',
    '1980s',
    '1970s',
    '1960s',
    '1950s',
    'Pre-1950'
  ]

  // Year seen ranges (for year watched)
  const yearSeenRanges = [
    '2025',
    '2024',
    '2023',
    '2022',
    '2021',
    '2020',
    '2019',
    '2018',
    '2017',
    '2016',
    '2015',
    '2014',
    '2013',
    '2012',
    '2011',
    '2010',
    '2009',
    '2008',
    '2007',
    '2006',
    'Pre-2006'
  ]

  // RT score ranges
  const rtRanges = [
    { label: '90-100% (Fresh)', value: '90-100' },
    { label: '80-89%', value: '80-89' },
    { label: '70-79%', value: '70-79' },
    { label: '60-69%', value: '60-69' },
    { label: '50-59% (Rotten)', value: '50-59' },
    { label: '40-49%', value: '40-49' },
    { label: '30-39%', value: '30-39' },
    { label: '20-29%', value: '20-29' },
    { label: '10-19%', value: '10-19' },
    { label: '0-9%', value: '0-9' }
  ]

  // Genre options
  const genreOptions = [
    'Action',
    'Adventure',
    'Animation',
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Family',
    'Fantasy',
    'History',
    'Horror',
    'Music',
    'Mystery',
    'Romance',
    'Science Fiction',
    'Thriller',
    'War',
    'Western'
  ]

  const getFilterLabel = (type, value) => {
    if (type === 'rt') {
      const range = rtRanges.find(r => r.value === value)
      return range ? range.label : value
    }
    return value
  }

  return (
    <>
      {/* Filter icon button - stays on top row */}
      <div ref={dropdownRef} className="filter-dropdown">
        <button
          className={`filter-button ${hasActiveFilters() ? 'active' : ''}`}
          title="Filter"
          onClick={(e) => toggleMainDropdown(e)}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="4" y1="6" x2="8" y2="6"></line>
            <line x1="14" y1="6" x2="20" y2="6"></line>
            <circle cx="11" cy="6" r="2" fill="currentColor"></circle>
            <line x1="4" y1="12" x2="16" y2="12"></line>
            <line x1="20" y1="12" x2="20" y2="12"></line>
            <circle cx="18" cy="12" r="2" fill="currentColor"></circle>
            <line x1="4" y1="18" x2="10" y2="18"></line>
            <line x1="16" y1="18" x2="20" y2="18"></line>
            <circle cx="13" cy="18" r="2" fill="currentColor"></circle>
          </svg>
        </button>

        {/* Main dropdown to add filters */}
        {showMainDropdown && (
            <div className="filter-main-dropdown">
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, rating: true }))
                  setOpenDropdowns({
                    rating: true,
                    rt: false,
                    year: false,
                    yearSeen: false,
                    genre: false
                  })
                  setShowMainDropdown(false)
                }}
              >
                By J-Rayting
              </button>
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, rt: true }))
                  setOpenDropdowns({
                    rating: false,
                    rt: true,
                    year: false,
                    yearSeen: false,
                    genre: false
                  })
                  setShowMainDropdown(false)
                }}
              >
                By Rotten Tomatoes
              </button>
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, year: true }))
                  setOpenDropdowns({
                    rating: false,
                    rt: false,
                    year: true,
                    yearSeen: false,
                    genre: false
                  })
                  setShowMainDropdown(false)
                }}
              >
                By Film Year
              </button>
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, yearSeen: true }))
                  setOpenDropdowns({
                    rating: false,
                    rt: false,
                    year: false,
                    yearSeen: true,
                    genre: false
                  })
                  setShowMainDropdown(false)
                }}
              >
                By Year Seen
              </button>
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, genre: true }))
                  setOpenDropdowns({
                    rating: false,
                    rt: false,
                    year: false,
                    yearSeen: false,
                    genre: true
                  })
                  setShowMainDropdown(false)
                }}
              >
                By Genre
              </button>
            </div>
        )}
      </div>

      {/* All active filter buttons - stacked vertically */}
      {hasActiveFilters() && (
        <div ref={filterWrapperRef} className={`filter-buttons-stack-wrapper filter-count-${Math.min(countActiveFilters(), 3)}`}>
          <div ref={filterStackRef} className="filter-buttons-stack">
          {/* By J-Rayting Filter - Show if active */}
          {activeFilters.rating && (
            <div className="filter-dropdown">
              <button
                className="filter-type-button active"
                onClick={(e) => toggleDropdown('rating', e)}
              >
                By J-Rayting ({selectedFilters.rating.length})
              </button>

              {openDropdowns.rating && (
                  <div className="filter-checkbox-dropdown">
                    {ratingOptions.map(rating => (
                      <label key={rating} className="filter-checkbox-label">
                        <input
                          type="checkbox"
                          checked={selectedFilters.rating.includes(rating)}
                          onChange={() => handleValueToggle('rating', rating)}
                          className="filter-checkbox"
                        />
                        <span>{rating}</span>
                      </label>
                    ))}
                  </div>
              )}
            </div>
          )}

          {/* By Rotten Tomatoes Filter - Show if active */}
          {activeFilters.rt && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={(e) => toggleDropdown('rt', e)}
          >
            By RT ({selectedFilters.rt.length})
          </button>

          {openDropdowns.rt && (
              <div className="filter-checkbox-dropdown">
                {rtRanges.map(range => (
                  <label key={range.value} className="filter-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedFilters.rt.includes(range.value)}
                      onChange={() => handleValueToggle('rt', range.value)}
                      className="filter-checkbox"
                    />
                    <span>{range.label}</span>
                  </label>
                ))}
              </div>
          )}
        </div>
      )}

      {/* By Film Year Filter - Show if active */}
      {activeFilters.year && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={(e) => toggleDropdown('year', e)}
          >
            By Film Year ({selectedFilters.year.length})
          </button>

          {openDropdowns.year && (
              <div className="filter-checkbox-dropdown">
                {yearRanges.map(range => (
                  <label key={range} className="filter-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedFilters.year.includes(range)}
                      onChange={() => handleValueToggle('year', range)}
                      className="filter-checkbox"
                    />
                    <span>{range}</span>
                  </label>
                ))}
              </div>
          )}
        </div>
      )}

      {/* By Year Seen Filter - Show if active */}
      {activeFilters.yearSeen && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={(e) => toggleDropdown('yearSeen', e)}
          >
            By Year Seen ({selectedFilters.yearSeen.length})
          </button>

          {openDropdowns.yearSeen && (
              <div className="filter-checkbox-dropdown">
                {yearSeenRanges.map(range => (
                  <label key={range} className="filter-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedFilters.yearSeen.includes(range)}
                      onChange={() => handleValueToggle('yearSeen', range)}
                      className="filter-checkbox"
                    />
                    <span>{range}</span>
                  </label>
                ))}
              </div>
          )}
        </div>
      )}

      {/* By Genre Filter - Show if active */}
      {activeFilters.genre && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={(e) => toggleDropdown('genre', e)}
          >
            By Genre ({selectedFilters.genre.length})
          </button>

          {openDropdowns.genre && (
              <div className="filter-checkbox-dropdown">
                {genreOptions.map(genre => (
                  <label key={genre} className="filter-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedFilters.genre.includes(genre)}
                      onChange={() => handleValueToggle('genre', genre)}
                      className="filter-checkbox"
                    />
                    <span>{genre}</span>
                  </label>
                ))}
              </div>
          )}
        </div>
      )}

      {/* Clear Filters button - on same row as filters */}
      {hasSelectedValues() && (
        <button className="clear-all-filters-btn" onClick={handleClear}>
          Clear Filters
        </button>
      )}
          </div>
        </div>
      )}
    </>
  )
}

export default FilterBar
