import { useState, useEffect, useRef } from 'react'

function BookFilterBar({ onFilterChange, activeFilter: propActiveFilter, onActiveFiltersChange }) {
  const [showMainDropdown, setShowMainDropdown] = useState(false)
  const [openDropdowns, setOpenDropdowns] = useState({
    rating: false,
    type: false,
    form: false,
    year: false,
    author: false
  })
  const dropdownRef = useRef(null)
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

  // Notify parent when activeFilters changes
  useEffect(() => {
    if (onActiveFiltersChange) {
      const hasAnyActive = activeFilters.rating ||
                          activeFilters.type ||
                          activeFilters.form ||
                          activeFilters.year ||
                          activeFilters.author
      onActiveFiltersChange(hasAnyActive)
    }
  }, [activeFilters, onActiveFiltersChange])

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
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

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const toggleMainDropdown = () => {
    setShowMainDropdown(!showMainDropdown)
  }

  const toggleDropdown = (type) => {
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

  const hasActiveFilters = () => {
    return activeFilters.rating ||
           activeFilters.type ||
           activeFilters.form ||
           activeFilters.year ||
           activeFilters.author
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
          onClick={toggleMainDropdown}
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
        <div className="filter-buttons-stack">
          {/* By J-Rayting Filter */}
          {activeFilters.rating && (
            <div className="filter-dropdown">
              <button
                className="filter-type-button active"
                onClick={() => toggleDropdown('rating')}
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
                onClick={() => toggleDropdown('type')}
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
                onClick={() => toggleDropdown('form')}
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
                onClick={() => toggleDropdown('year')}
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
                onClick={() => toggleDropdown('author')}
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
        </div>
      )}

      {/* Clear Filters button */}
      {hasSelectedValues() && (
        <button className="clear-all-filters-btn" onClick={handleClear}>
          Clear Filters
        </button>
      )}
    </div>
  )
}

export default BookFilterBar

