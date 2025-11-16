import { useState } from 'react'

function FilterBar({ onFilterChange }) {
  const [showMainDropdown, setShowMainDropdown] = useState(false)
  const [openDropdowns, setOpenDropdowns] = useState({
    rating: false,
    year: false,
    rt: false,
    genre: false
  })
  const [activeFilters, setActiveFilters] = useState({
    rating: false,
    year: false,
    rt: false,
    genre: false
  })
  const [selectedFilters, setSelectedFilters] = useState({
    rating: [],
    year: [],
    rt: [],
    genre: []
  })

  const toggleMainDropdown = () => {
    setShowMainDropdown(!showMainDropdown)
  }

  const toggleDropdown = (type) => {
    setOpenDropdowns(prev => ({
      ...prev,
      [type]: !prev[type]
    }))
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
    setSelectedFilters({
      rating: [],
      year: [],
      rt: [],
      genre: []
    })
    setActiveFilters({
      rating: false,
      year: false,
      rt: false,
      genre: false
    })
    onFilterChange({
      rating: [],
      year: [],
      rt: [],
      genre: []
    })
  }

  const hasActiveFilters = () => {
    return selectedFilters.rating.length > 0 ||
           selectedFilters.year.length > 0 ||
           selectedFilters.rt.length > 0 ||
           selectedFilters.genre.length > 0
  }

  // Rating options: A+, A, A-, B+, B, B-, C+, C, C-, D+, D
  const ratingOptions = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']

  // Year ranges
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

  return (
    <div className="filter-bar">
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
          <>
            <div className="filter-dropdown-overlay" onClick={() => setShowMainDropdown(false)}></div>
            <div className="filter-main-dropdown">
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, rating: true }))
                  setOpenDropdowns(prev => ({ ...prev, rating: true }))
                  setShowMainDropdown(false)
                }}
              >
                By J-Rayting
              </button>
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, year: true }))
                  setOpenDropdowns(prev => ({ ...prev, year: true }))
                  setShowMainDropdown(false)
                }}
              >
                By Film Year
              </button>
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, rt: true }))
                  setOpenDropdowns(prev => ({ ...prev, rt: true }))
                  setShowMainDropdown(false)
                }}
              >
                By Rotten Tomatoes
              </button>
              <button
                className="filter-add-option"
                onClick={() => {
                  setActiveFilters(prev => ({ ...prev, genre: true }))
                  setOpenDropdowns(prev => ({ ...prev, genre: true }))
                  setShowMainDropdown(false)
                }}
              >
                By Genre
              </button>
            </div>
          </>
        )}
      </div>

      {/* By J-Rayting Filter - Show if active */}
      {activeFilters.rating && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={() => toggleDropdown('rating')}
          >
            By J-Rayting ({selectedFilters.rating.length})
          </button>

          {openDropdowns.rating && (
            <>
              <div className="filter-dropdown-overlay" onClick={() => toggleDropdown('rating')}></div>
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
            </>
          )}
        </div>
      )}

      {/* By Film Year Filter - Show if active */}
      {activeFilters.year && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={() => toggleDropdown('year')}
          >
            By Film Year ({selectedFilters.year.length})
          </button>

          {openDropdowns.year && (
            <>
              <div className="filter-dropdown-overlay" onClick={() => toggleDropdown('year')}></div>
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
            </>
          )}
        </div>
      )}

      {/* By Rotten Tomatoes Filter - Show if active */}
      {activeFilters.rt && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={() => toggleDropdown('rt')}
          >
            By RT ({selectedFilters.rt.length})
          </button>

          {openDropdowns.rt && (
            <>
              <div className="filter-dropdown-overlay" onClick={() => toggleDropdown('rt')}></div>
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
            </>
          )}
        </div>
      )}

      {/* By Genre Filter - Show if active */}
      {activeFilters.genre && (
        <div className="filter-dropdown">
          <button
            className="filter-type-button active"
            onClick={() => toggleDropdown('genre')}
          >
            By Genre ({selectedFilters.genre.length})
          </button>

          {openDropdowns.genre && (
            <>
              <div className="filter-dropdown-overlay" onClick={() => toggleDropdown('genre')}></div>
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
            </>
          )}
        </div>
      )}

      {hasActiveFilters() && (
        <button className="clear-filter-btn" onClick={handleClear}>
          Clear All Filters
        </button>
      )}
    </div>
  )
}

export default FilterBar
