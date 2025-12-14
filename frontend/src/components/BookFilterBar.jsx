import { useState, useEffect, useRef } from 'react'

function BookFilterBar({ onFilterChange, activeFilter: propActiveFilter, onActiveFiltersChange, onFilterCountChange, onFilterRowsChange }) {
  const [showMainDropdown, setShowMainDropdown] = useState(false)
  const [openDropdowns, setOpenDropdowns] = useState({
    rating: false,
    type: false,
    form: false,
    year: false,
    author: false
  })
  const dropdownRef = useRef(null)
  const filterWrapperRef = useRef(null)
  const filterStackRef = useRef(null)
  const [activeFilters, setActiveFilters] = useState({
    rating: false,
    type: false,
    form: false,
    year: false,
    author: false
  })
  const [selectedFilters, setSelectedFilters] = useState(() => {
    const saved = localStorage.getItem('booksActiveFilter')
    if (saved) {
      const parsedFilters = JSON.parse(saved)
      return {
        rating: parsedFilters.rating || [],
        type: parsedFilters.type || [],
        form: parsedFilters.form || [],
        year: parsedFilters.year || [],
        author: parsedFilters.author || []
      }
    }
    return {
      rating: [],
      type: [],
      form: [],
      year: [],
      author: []
    }
  })

  // Sync with prop if provided
  useEffect(() => {
    if (propActiveFilter) {
      setSelectedFilters(propActiveFilter)
      setActiveFilters({
        rating: propActiveFilter.rating?.length > 0 || false,
        type: propActiveFilter.type?.length > 0 || false,
        form: propActiveFilter.form?.length > 0 || false,
        year: propActiveFilter.year?.length > 0 || false,
        author: propActiveFilter.author?.length > 0 || false
      })
    }
  }, [propActiveFilter])

  // On mount, restore active filters from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('booksActiveFilter')
    if (saved) {
      const parsedFilters = JSON.parse(saved)
      const fullFilters = {
        rating: parsedFilters.rating || [],
        type: parsedFilters.type || [],
        form: parsedFilters.form || [],
        year: parsedFilters.year || [],
        author: parsedFilters.author || []
      }
      setSelectedFilters(fullFilters)

      setActiveFilters({
        rating: fullFilters.rating.length > 0,
        type: fullFilters.type.length > 0,
        form: fullFilters.form.length > 0,
        year: fullFilters.year.length > 0,
        author: fullFilters.author.length > 0
      })
    }
  }, [])

  // Check if any filters are active
  const hasActiveFilters = () => {
    return activeFilters.rating ||
           activeFilters.type ||
           activeFilters.form ||
           activeFilters.year ||
           activeFilters.author
  }

  const countActiveFilters = () => {
    let count = 0
    if (activeFilters.rating) count++
    if (activeFilters.type) count++
    if (activeFilters.form) count++
    if (activeFilters.year) count++
    if (activeFilters.author) count++
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
      const hasAnyActive = hasActiveFilters()
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

    const timeoutId = setTimeout(() => {
      const rows = calculateFilterRows()
      if (onFilterRowsChange) {
        onFilterRowsChange(rows)
      }
    }, 100) // Small delay to ensure layout has settled

    return () => clearTimeout(timeoutId)
  }, [activeFilters, onFilterRowsChange])

  // Also measure on window resize
  useEffect(() => {
    if (!onFilterRowsChange) return

    let resizeTimeout
    const handleResize = () => {
      if (!hasActiveFilters()) {
        onFilterRowsChange(0)
        return
      }
      clearTimeout(resizeTimeout)
      resizeTimeout = setTimeout(() => {
        const rows = calculateFilterRows()
        if (onFilterRowsChange) {
          onFilterRowsChange(rows)
        }
      }, 150)
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [activeFilters, onFilterRowsChange])

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
        // Filter type buttons (By J-Rayting, By Type, etc.)
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
          type: false,
          form: false,
          year: false,
          author: false
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
  }, [])

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
      const allClosed = {
        rating: false,
        type: false,
        form: false,
        year: false,
        author: false
      }
      return {
        ...allClosed,
        [type]: !isCurrentlyOpen
      }
    })
  }

  const handleValueToggle = (type, value) => {
    const newSelectedFilters = { ...selectedFilters }

    if (newSelectedFilters[type].includes(value)) {
      newSelectedFilters[type] = newSelectedFilters[type].filter(v => v !== value)
    } else {
      newSelectedFilters[type] = [...newSelectedFilters[type], value]
    }

    setSelectedFilters(newSelectedFilters)
    onFilterChange(newSelectedFilters)
  }

  const handleAuthorInput = (value) => {
    // For author, we'll use a simple text input approach
    // Store as array with single value for consistency
    const newSelectedFilters = {
      ...selectedFilters,
      author: value ? [value] : []
    }
    setSelectedFilters(newSelectedFilters)
    onFilterChange(newSelectedFilters)
  }

  const handleClear = () => {
    setSelectedFilters({
      rating: [],
      type: [],
      form: [],
      year: [],
      author: []
    })
    setActiveFilters({
      rating: false,
      type: false,
      form: false,
      year: false,
      author: false
    })
    onFilterChange({
      rating: [],
      type: [],
      form: [],
      year: [],
      author: []
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
           selectedFilters.type.length > 0 ||
           selectedFilters.form.length > 0 ||
           selectedFilters.year.length > 0 ||
           selectedFilters.author.length > 0
  }

  // Rating options
  const ratingOptions = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']

  // Type options
  const typeOptions = [
    'Fiction',
    'Non-fiction: Business',
    'Non-fiction: Social',
    'Non-fiction: Sport',
    'Non-fiction: Bio',
    'Non-fiction: Politics',
    'Non-fiction: True Crime',
    'Non-fiction'
  ]

  // Form options
  const formOptions = ['Kindle', 'Book']

  // Year read ranges
  const yearRanges = []
  const currentYear = new Date().getFullYear()
  for (let year = currentYear; year >= 2000; year--) {
    yearRanges.push(year.toString())
  }
  yearRanges.push('Pre-2000')

  return (
    <div ref={dropdownRef} style={{ display: 'contents' }}>
      {/* Filter icon button */}
      <div className="filter-dropdown">
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
                  type: false,
                  form: false,
                  year: false,
                  author: false
                })
                setShowMainDropdown(false)
              }}
            >
              By J-Rayting
            </button>
            <button
              className="filter-add-option"
              onClick={() => {
                setActiveFilters(prev => ({ ...prev, type: true }))
                setOpenDropdowns({
                  rating: false,
                  type: true,
                  form: false,
                  year: false,
                  author: false
                })
                setShowMainDropdown(false)
              }}
            >
              By Type
            </button>
            <button
              className="filter-add-option"
              onClick={() => {
                setActiveFilters(prev => ({ ...prev, form: true }))
                setOpenDropdowns({
                  rating: false,
                  type: false,
                  form: true,
                  year: false,
                  author: false
                })
                setShowMainDropdown(false)
              }}
            >
              By Form
            </button>
            <button
              className="filter-add-option"
              onClick={() => {
                setActiveFilters(prev => ({ ...prev, year: true }))
                setOpenDropdowns({
                  rating: false,
                  type: false,
                  form: false,
                  year: true,
                  author: false
                })
                setShowMainDropdown(false)
              }}
            >
              By Year Read
            </button>
            <button
              className="filter-add-option"
              onClick={() => {
                setActiveFilters(prev => ({ ...prev, author: true }))
                setOpenDropdowns({
                  rating: false,
                  type: false,
                  form: false,
                  year: false,
                  author: true
                })
                setShowMainDropdown(false)
              }}
            >
              By Author
            </button>
          </div>
        )}
      </div>

      {/* All active filter buttons */}
      {hasActiveFilters() && (
        <div ref={filterWrapperRef} className={`filter-buttons-stack-wrapper filter-count-${Math.min(countActiveFilters(), 3)}`}>
          <div ref={filterStackRef} className="filter-buttons-stack">
          {/* By J-Rayting Filter */}
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

          {/* By Type Filter */}
          {activeFilters.type && (
            <div className="filter-dropdown">
              <button
                className="filter-type-button active"
                onClick={(e) => toggleDropdown('type', e)}
              >
                By Type ({selectedFilters.type.length})
              </button>

              {openDropdowns.type && (
                <div className="filter-checkbox-dropdown">
                  {typeOptions.map(type => (
                    <label key={type} className="filter-checkbox-label">
                      <input
                        type="checkbox"
                        checked={selectedFilters.type.includes(type)}
                        onChange={() => handleValueToggle('type', type)}
                        className="filter-checkbox"
                      />
                      <span>{type}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* By Form Filter */}
          {activeFilters.form && (
            <div className="filter-dropdown">
              <button
                className="filter-type-button active"
                onClick={(e) => toggleDropdown('form', e)}
              >
                By Form ({selectedFilters.form.length})
              </button>

              {openDropdowns.form && (
                <div className="filter-checkbox-dropdown">
                  {formOptions.map(form => (
                    <label key={form} className="filter-checkbox-label">
                      <input
                        type="checkbox"
                        checked={selectedFilters.form.includes(form)}
                        onChange={() => handleValueToggle('form', form)}
                        className="filter-checkbox"
                      />
                      <span>{form}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* By Year Read Filter */}
          {activeFilters.year && (
            <div className="filter-dropdown">
              <button
                className="filter-type-button active"
                onClick={(e) => toggleDropdown('year', e)}
              >
                By Year Read ({selectedFilters.year.length})
              </button>

              {openDropdowns.year && (
                <div className="filter-checkbox-dropdown">
                  {yearRanges.map(year => (
                    <label key={year} className="filter-checkbox-label">
                      <input
                        type="checkbox"
                        checked={selectedFilters.year.includes(year)}
                        onChange={() => handleValueToggle('year', year)}
                        className="filter-checkbox"
                      />
                      <span>{year}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* By Author Filter */}
          {activeFilters.author && (
            <div className="filter-dropdown">
              <button
                className="filter-type-button active"
                onClick={(e) => toggleDropdown('author', e)}
              >
                By Author {selectedFilters.author.length > 0 && `(${selectedFilters.author.length})`}
              </button>

              {openDropdowns.author && (
                <div className="filter-checkbox-dropdown">
                  <input
                    type="text"
                    placeholder="Search author name..."
                    value={selectedFilters.author[0] || ''}
                    onChange={(e) => handleAuthorInput(e.target.value)}
                    className="filter-author-input"
                    style={{
                      width: '100%',
                      padding: '8px',
                      margin: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              )}
            </div>
          )}
          
          {hasSelectedValues() && (
            <button className="clear-all-filters-btn" onClick={handleClear}>
              Clear Filters
            </button>
          )}
        </div>
      </div>
      )}
    </div>
  )
}

export default BookFilterBar

