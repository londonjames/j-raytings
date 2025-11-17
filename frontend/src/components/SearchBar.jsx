import { useState, useEffect } from 'react'

function SearchBar({ onSearch, totalFilms, filteredFilms, initialSearchTerm = '' }) {
  const [searchTerm, setSearchTerm] = useState(initialSearchTerm)

  // Update local state when initialSearchTerm changes (e.g., from localStorage)
  useEffect(() => {
    setSearchTerm(initialSearchTerm)
  }, [initialSearchTerm])

  const handleSearchChange = (value) => {
    setSearchTerm(value)
    onSearch(value)
  }

  const handleClear = () => {
    setSearchTerm('')
    onSearch('')
  }

  // Determine placeholder text
  const getPlaceholder = () => {
    if (filteredFilms === totalFilms) {
      return `Search ${totalFilms.toLocaleString()} films...`
    } else {
      return `${filteredFilms.toLocaleString()} films selected`
    }
  }

  const isFiltered = filteredFilms !== totalFilms

  return (
    <div className="search-bar">
      <div className="search-input-container">
        <input
          type="text"
          placeholder={getPlaceholder()}
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
          className={`search-input ${isFiltered ? 'search-input-filtered' : ''}`}
        />
        {searchTerm && (
          <button className="clear-search-btn" onClick={handleClear}>
            ✕
          </button>
        )}
      </div>
    </div>
  )
}

export default SearchBar
