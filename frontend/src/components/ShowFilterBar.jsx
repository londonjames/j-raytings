import { useState, useEffect, useRef } from 'react'

function ShowFilterBar({ onFilterChange, activeFilter: propActiveFilter, onActiveFiltersChange, onFilterCountChange, onFilterRowsChange }) {
  const [showMainDropdown, setShowMainDropdown] = useState(false)
  const [openDropdowns, setOpenDropdowns] = useState({
    rating: false,
    genre: false,
    decade: false
  })
  const dropdownRef = useRef(null)
  const filterWrapperRef = useRef(null)
  const filterStackRef = useRef(null)
  const [activeFilters, setActiveFilters] = useState({
    rating: false,
    genre: false,
    decade: false
  })
  const [selectedFilters, setSelectedFilters] = useState(() => {
    const saved = localStorage.getItem('showsActiveFilter')
    if (saved) {
      const parsedFilters = JSON.parse(saved)
      return {
        rating: parsedFilters.rating || [],
        genre: parsedFilters.genre || [],
        decade: parsedFilters.decade || []
      }
    }
    return {
      rating: [],
      genre: [],
      decade: []
    }
  })

  useEffect(() => {
    if (propActiveFilter) {
      setSelectedFilters(propActiveFilter)
      setActiveFilters({
        rating: propActiveFilter.rating?.length > 0 || false,
        genre: propActiveFilter.genre?.length > 0 || false,
        decade: propActiveFilter.decade?.length > 0 || false
      })
    }
  }, [propActiveFilter])

  useEffect(() => {
    const saved = localStorage.getItem('showsActiveFilter')
    if (saved) {
      const parsedFilters = JSON.parse(saved)
      const fullFilters = {
        rating: parsedFilters.rating || [],
        genre: parsedFilters.genre || [],
        decade: parsedFilters.decade || []
      }
      setSelectedFilters(fullFilters)
      setActiveFilters({
        rating: fullFilters.rating.length > 0,
        genre: fullFilters.genre.length > 0,
        decade: fullFilters.decade.length > 0
      })
    }
  }, [])

  const hasActiveFilters = () => {
    return activeFilters.rating || activeFilters.genre || activeFilters.decade
  }

  const countActiveFilters = () => {
    let count = 0
    if (activeFilters.rating) count++
    if (activeFilters.genre) count++
    if (activeFilters.decade) count++
    return count
  }

  const calculateFilterRows = () => {
    if (!filterStackRef.current) return 0
    const stack = filterStackRef.current
    const height = stack.offsetHeight
    const singleRowHeight = 36 + 8
    const rows = Math.ceil(height / singleRowHeight)
    return Math.max(1, Math.min(rows, 3))
  }

  useEffect(() => {
    if (onActiveFiltersChange) {
      const hasAnyActive = hasActiveFilters()
      onActiveFiltersChange(hasAnyActive)
    }
    if (onFilterCountChange) {
      const count = countActiveFilters()
      onFilterCountChange(count)
    }
  }, [activeFilters, onActiveFiltersChange, onFilterCountChange])

  useEffect(() => {
    if (!onFilterRowsChange) return
    if (!hasActiveFilters()) {
      onFilterRowsChange(0)
      return
    }
    const timeoutId = setTimeout(() => {
      const rows = calculateFilterRows()
      if (onFilterRowsChange) {
        onFilterRowsChange(rows)
      }
    }, 100)
    return () => clearTimeout(timeoutId)
  }, [activeFilters, onFilterRowsChange])

  useEffect(() => {
    const handleClickOutside = (event) => {
      const mainDropdown = document.querySelector('.filter-main-dropdown')
      const checkboxDropdowns = document.querySelectorAll('.filter-checkbox-dropdown')
      const hasVisibleDropdown = mainDropdown || checkboxDropdowns.length > 0

      if (!hasVisibleDropdown) return

      const target = event.target
      const clickedOnFilterElement =
        target.closest('.filter-button') ||
        target.closest('.filter-type-button') ||
        target.closest('.filter-main-dropdown') ||
        target.closest('.filter-checkbox-dropdown') ||
        target.closest('.filter-add-option') ||
        target.closest('.filter-checkbox-label') ||
        target.closest('.filter-checkbox') ||
        target.closest('input[type="checkbox"]') ||
        target.closest('.clear-all-filters-btn')

      if (!clickedOnFilterElement) {
        setOpenDropdowns({ rating: false, genre: false, decade: false })
        setShowMainDropdown(false)
      }
    }

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
    if (e) e.stopPropagation()
    setShowMainDropdown(!showMainDropdown)
  }

  const toggleDropdown = (type, e) => {
    if (e) e.stopPropagation()
    setOpenDropdowns(prev => {
      const isCurrentlyOpen = prev[type]
      const allClosed = { rating: false, genre: false, decade: false }
      return { ...allClosed, [type]: !isCurrentlyOpen }
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

  const handleClear = () => {
    setSelectedFilters({ rating: [], genre: [], decade: [] })
    setActiveFilters({ rating: false, genre: false, decade: false })
    onFilterChange({ rating: [], genre: [], decade: [] })
  }

  const hasSelectedValues = () => {
    return selectedFilters.rating.length > 0 ||
           selectedFilters.genre.length > 0 ||
           selectedFilters.decade.length > 0
  }

  const ratingOptions = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']

  const genreOptions = [
    'Drama', 'Comedy', 'Crime', 'Action & Adventure', 'Sci-Fi & Fantasy',
    'Mystery', 'Documentary', 'Animation', 'Family', 'Reality', 'War & Politics'
  ]

  const decadeOptions = ['2020s', '2010s', '2000s', '1990s', 'Pre-1990']

  return (
    <div ref={dropdownRef} style={{ display: 'contents' }}>
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

        {showMainDropdown && (
          <div className="filter-main-dropdown">
            <button
              className="filter-add-option"
              onClick={() => {
                setActiveFilters(prev => ({ ...prev, rating: true }))
                setOpenDropdowns({ rating: true, genre: false, decade: false })
                setShowMainDropdown(false)
              }}
            >
              By J-Rayting
            </button>
            <button
              className="filter-add-option"
              onClick={() => {
                setActiveFilters(prev => ({ ...prev, genre: true }))
                setOpenDropdowns({ rating: false, genre: true, decade: false })
                setShowMainDropdown(false)
              }}
            >
              By Genre
            </button>
            <button
              className="filter-add-option"
              onClick={() => {
                setActiveFilters(prev => ({ ...prev, decade: true }))
                setOpenDropdowns({ rating: false, genre: false, decade: true })
                setShowMainDropdown(false)
              }}
            >
              By Decade
            </button>
          </div>
        )}
      </div>

      {hasActiveFilters() && (
        <div ref={filterWrapperRef} className={`filter-buttons-stack-wrapper filter-count-${Math.min(countActiveFilters(), 3)}`}>
          <div ref={filterStackRef} className="filter-buttons-stack">
            {activeFilters.rating && (
              <div className="filter-dropdown">
                <button className="filter-type-button active" onClick={(e) => toggleDropdown('rating', e)}>
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

            {activeFilters.genre && (
              <div className="filter-dropdown">
                <button className="filter-type-button active" onClick={(e) => toggleDropdown('genre', e)}>
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

            {activeFilters.decade && (
              <div className="filter-dropdown">
                <button className="filter-type-button active" onClick={(e) => toggleDropdown('decade', e)}>
                  By Decade ({selectedFilters.decade.length})
                </button>
                {openDropdowns.decade && (
                  <div className="filter-checkbox-dropdown">
                    {decadeOptions.map(decade => (
                      <label key={decade} className="filter-checkbox-label">
                        <input
                          type="checkbox"
                          checked={selectedFilters.decade.includes(decade)}
                          onChange={() => handleValueToggle('decade', decade)}
                          className="filter-checkbox"
                        />
                        <span>{decade}</span>
                      </label>
                    ))}
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

export default ShowFilterBar
