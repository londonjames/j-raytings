import { useState } from 'react'

function SearchBar({ onSearch, totalFilms, filteredFilms }) {
  const [searchTerm, setSearchTerm] = useState('')

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
