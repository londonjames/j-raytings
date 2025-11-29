import { useState, useEffect } from 'react'

function BookSortBar({ onSortChange, initialSortConfig }) {
  // Initialize from prop or localStorage, defaulting to empty (no visual selection)
  const getInitialSort = () => {
    if (initialSortConfig) {
      return initialSortConfig
    }
    const saved = localStorage.getItem('booksSortConfig')
    return saved ? JSON.parse(saved) : { sortBy: '', direction: 'desc' }
  }

  const initialSort = getInitialSort()
  const initialSortBy = initialSort.sortBy || ''
  const [sortBy, setSortBy] = useState(initialSortBy)
  const [sortDirection, setSortDirection] = useState(initialSort.direction || 'desc')
  const [showDirectionToggle, setShowDirectionToggle] = useState(!!initialSortBy)

  // Sync with prop changes
  useEffect(() => {
    if (initialSortConfig) {
      const newSortBy = initialSortConfig.sortBy || ''
      setSortBy(newSortBy)
      setSortDirection(initialSortConfig.direction || 'desc')
      setShowDirectionToggle(!!newSortBy)
    }
  }, [initialSortConfig])

  const handleSortChange = (newSortBy) => {
    if (!newSortBy) {
      setSortBy('')
      setShowDirectionToggle(false)
      onSortChange({ sortBy: '', direction: sortDirection })
    } else {
      setSortBy(newSortBy)
      setShowDirectionToggle(true)
      onSortChange({ sortBy: newSortBy, direction: sortDirection })
    }
  }

  const toggleDirection = () => {
    const newDirection = sortDirection === 'desc' ? 'asc' : 'desc'
    setSortDirection(newDirection)
    onSortChange({ sortBy, direction: newDirection })
  }

  const getSortLabel = () => {
    switch(sortBy) {
      case 'rating': return 'By J-Rayting'
      case 'date': return 'By Date Read'
      case 'year': return 'By Year Read'
      case 'published': return 'By Year Written'
      case 'dateWritten': return 'By Date Written'
      case 'pages': return 'By Pages'
      default: return ''
    }
  }

  return (
    <div className="sort-bar">
      <div className="sort-dropdown">
        <button className={`sort-button ${sortBy ? 'active' : ''}`} title="Sort">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="11" y1="5" x2="11" y2="19"></line>
            <polyline points="18 12 11 19 4 12"></polyline>
          </svg>
        </button>
        <select
          value={sortBy}
          onChange={(e) => handleSortChange(e.target.value)}
          className="sort-select"
        >
          <option value="">[CLEAR SORT ORDER]</option>
          <option value="rating">By J-Rayting</option>
          <option value="date">By Date Read</option>
          <option value="year">By Year Read</option>
          <option value="published">By Year Written</option>
          <option value="dateWritten">By Date Written</option>
          <option value="pages">By Pages</option>
        </select>
      </div>

      {showDirectionToggle && (
        <>
          <span className="sort-label">{getSortLabel()}</span>
          <button
            className="sort-direction-btn"
            onClick={toggleDirection}
            title={sortDirection === 'desc' ? 'Best first' : 'Worst first'}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {sortDirection === 'desc' ? (
                <>
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <polyline points="19 12 12 19 5 12"></polyline>
                </>
              ) : (
                <>
                  <line x1="12" y1="19" x2="12" y2="5"></line>
                  <polyline points="5 12 12 5 19 12"></polyline>
                </>
              )}
            </svg>
          </button>
        </>
      )}
    </div>
  )
}

export default BookSortBar

