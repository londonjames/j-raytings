import FilmList from '../components/FilmList'
import FilmForm from '../components/FilmForm'
import SortBar from '../components/SortBar'
import FilterBar from '../components/FilterBar'
import Analytics from '../components/Analytics'

export const filmsConfig = {
  // Basic metadata
  type: 'films',
  titleSingular: 'Film',
  titlePlural: 'Films',

  // API configuration
  apiEndpoint: 'films',
  cacheKey: 'cachedFilms',

  // LocalStorage keys
  localStorageKeys: {
    viewMode: 'viewMode',
    searchTerm: 'searchTerm',
    activeFilter: 'activeFilter',
    sortConfig: 'sortConfig',
    showAnalytics: 'showAnalytics',
  },

  // Page titles
  pageTitles: {
    main: 'Films | James Raybould',
    admin: 'Admin | Films | James Raybould',
  },

  // Components
  components: {
    List: FilmList,
    Form: FilmForm,
    SortBar: SortBar,
    FilterBar: FilterBar,
    Analytics: Analytics,
  },

  // Filter configuration
  filterFields: {
    rating: [],
    rt: [],
    year: [],
    yearSeen: [],
    genre: [],
  },

  // Empty state messages
  emptyState: {
    message: 'Nope, nothing here!',
    hint: "Either you're searching wrong or James hasn't seen the film :)",
  },

  // Format title function
  formatTitle: (title) => {
    if (!title) return ''
    if (title.includes(',')) {
      const parts = title.split(',').map(s => s.trim())
      if (parts.length === 2) {
        return `${parts[1]} ${parts[0]}`
      }
    }
    return title
  },

  // Search function
  searchFilter: (item, searchLower, formatTitle) => {
    const originalTitle = item.title.toLowerCase()
    const formattedTitle = formatTitle(item.title).toLowerCase()
    return originalTitle.includes(searchLower) || formattedTitle.includes(searchLower)
  },

  // Helper function to get the higher rating from a combo rating
  // E.g., "A/A+" -> "A+", "A-/A" -> "A", "B+/A-" -> "A-"
  getHigherRating: (rating) => {
    if (!rating) return null
    // If it's not a combo (no slash), return as-is
    if (!rating.includes('/')) return rating
    
    // Split combo rating (e.g., "A/A+" -> ["A", "A+"])
    const parts = rating.split('/').map(r => r.trim())
    if (parts.length !== 2) return rating // Not a valid combo, return as-is
    
    // Rating order from highest to lowest (higher number = better rating)
    const ratingOrder = {
      'A+': 20, 'A/A+': 19, 'A': 18, 'A-/A': 17, 'A-': 16,
      'B+/A-': 15, 'B+': 14, 'B/B+': 13, 'B': 12, 'B-/B': 11, 'B-': 10,
      'C+/B-': 9, 'C+': 8, 'C/C+': 7, 'C': 6, 'C-': 5,
      'D+': 4, 'D': 3
    }
    
    // Compare the two parts and return the one with higher order (higher number = better rating)
    const part1Order = ratingOrder[parts[0]] || 0
    const part2Order = ratingOrder[parts[1]] || 0
    
    // Higher order number = better rating, so return the one with higher order
    return part1Order > part2Order ? parts[0] : parts[1]
  },

  // Filter functions
  applyRatingFilter: (items, selectedRatings) => {
    // Get reference to config for helper function
    const config = filmsConfig
    return items.filter(item => {
      if (!item.letter_rating) return false
      
      // Check if exact match
      if (selectedRatings.includes(item.letter_rating)) return true
      
      // Check if combo rating's higher rating matches any selected rating
      if (item.letter_rating.includes('/')) {
        const higherRating = config.getHigherRating(item.letter_rating)
        return selectedRatings.includes(higherRating)
      }
      
      return false
    })
  },

  applyYearFilter: (items, selectedYears) => {
    return items.filter(item => {
      if (!item.release_year) return false
      const year = parseInt(item.release_year)

      return selectedYears.some(selectedDecade => {
        if (selectedDecade === 'Pre-1950') {
          return year < 1950
        } else {
          const decade = selectedDecade.replace('s', '')
          const decadeStart = parseInt(decade)
          return year >= decadeStart && year < decadeStart + 10
        }
      })
    })
  },

  applyRtFilter: (items, selectedRanges) => {
    return items.filter(item => {
      if (!item.rotten_tomatoes) return false
      const rtScore = parseInt(item.rotten_tomatoes.replace('%', ''))

      return selectedRanges.some(selectedRange => {
        const [min, max] = selectedRange.split('-').map(n => parseInt(n))
        return rtScore >= min && rtScore <= max
      })
    })
  },

  applyGenreFilter: (items, selectedGenres) => {
    return items.filter(item => {
      if (!item.genres) return false
      const itemGenres = item.genres.split(', ')

      return selectedGenres.some(selectedGenre => itemGenres.includes(selectedGenre))
    })
  },

  // Helper to extract year from date_seen (supports YYYY-MM-DD and MM/DD/YYYY formats)
  getYearFromDateSeen: (dateSeen) => {
    if (!dateSeen) return null
    // YYYY-MM-DD format
    if (dateSeen.match(/^\d{4}-\d{2}-\d{2}/)) {
      return dateSeen.substring(0, 4)
    }
    // MM/DD/YYYY format
    if (dateSeen.includes('/')) {
      const parts = dateSeen.split('/')
      if (parts.length === 3 && parts[2].length === 4) {
        return parts[2]
      }
    }
    return null
  },

  applyYearSeenFilter: (items, selectedYears) => {
    return items.filter(item => {
      // Use year_watched if available, otherwise derive from date_seen
      let yearValue = item.year_watched
      if (!yearValue && item.date_seen) {
        yearValue = filmsConfig.getYearFromDateSeen(item.date_seen)
      }
      if (!yearValue) return false

      return selectedYears.some(selectedYear => {
        if (selectedYear === 'Pre-2006') {
          return yearValue === 'Pre-2006'
        } else {
          return yearValue === selectedYear
        }
      })
    })
  },

  // Sort function
  sortItems: (items, sortBy, direction) => {
    const sorted = [...items]

    sorted.sort((a, b) => {
      let comparison = 0

      // Default to rating if no sort is selected
      const actualSortBy = sortBy || 'rating'

      if (actualSortBy === 'rating') {
        // Helper to get score, calculating from letter_rating if score is missing
        const getScore = (item) => {
          if (item.score !== null && item.score !== undefined) {
            return item.score
          }
          // If score is missing, calculate from letter_rating
          if (item.letter_rating) {
            const ratingMap = {
              'A+': 20, 'A/A+': 19, 'A': 18, 'A-/A': 17, 'A-': 16,
              'B+/A-': 15, 'B+': 14, 'B/B+': 13, 'B': 12, 'B-/B': 11, 'B-': 10,
              'C+/B-': 9, 'C+': 8, 'C/C+': 7, 'C': 6, 'C-': 5,
              'D+': 4, 'D': 3
            }
            return ratingMap[item.letter_rating] || 0
          }
          return 0
        }

        // Special handling for A-grade movies: use custom ranking if available
        const aIsA = a.letter_rating === 'A'
        const bIsA = b.letter_rating === 'A'

        if (aIsA && bIsA) {
          // Both are A-grade: use custom ranking
          const aRank = a.a_grade_rank
          const bRank = b.a_grade_rank

          if (aRank !== null && aRank !== undefined && bRank !== null && bRank !== undefined) {
            // Both have ranks: lower rank number = better (rank 1 is best)
            comparison = aRank - bRank
          } else if (aRank !== null && aRank !== undefined) {
            // Only a has rank: a comes first
            comparison = -1
          } else if (bRank !== null && bRank !== undefined) {
            // Only b has rank: b comes first
            comparison = 1
          } else {
            // Neither has rank: fall back to score, then alphabetical
            const aScore = getScore(a)
            const bScore = getScore(b)
            comparison = bScore - aScore
          }
        } else {
          // Not both A-grade: use numeric score field (20 = A+, 19 = A/A+, etc.)
          const aScore = getScore(a)
          const bScore = getScore(b)
          comparison = bScore - aScore // Higher score first
        }
      } else if (actualSortBy === 'year') {
        const aYear = parseInt(a.release_year) || 0
        const bYear = parseInt(b.release_year) || 0
        comparison = bYear - aYear // Newer first
      } else if (actualSortBy === 'rt') {
        const aRT = parseInt(a.rotten_tomatoes?.replace('%', '')) || 0
        const bRT = parseInt(b.rotten_tomatoes?.replace('%', '')) || 0
        comparison = bRT - aRT // Higher RT first
      }

      // If primary sort is equal, sort alphabetically by title (numbers before letters)
      if (comparison === 0) {
        comparison = (a.title || '').localeCompare(b.title || '', undefined, { numeric: true, sensitivity: 'base' })
      }

      // For desc (best first): keep comparison as is
      // For asc (worst first): reverse it
      return direction === 'desc' ? comparison : -comparison
    })

    return sorted
  },
}
