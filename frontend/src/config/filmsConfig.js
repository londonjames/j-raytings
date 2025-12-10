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

  // Filter functions
  applyRatingFilter: (items, selectedRatings) => {
    return items.filter(item => selectedRatings.includes(item.letter_rating))
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

  applyYearSeenFilter: (items, selectedYears) => {
    return items.filter(item => {
      if (!item.year_watched) return false

      return selectedYears.some(selectedYear => {
        if (selectedYear === 'Pre-2006') {
          return item.year_watched === 'Pre-2006'
        } else {
          return item.year_watched === selectedYear
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
            const aScore = a.score || 0
            const bScore = b.score || 0
            comparison = bScore - aScore
          }
        } else {
          // Not both A-grade: use numeric score field (20 = A+, 19 = A/A+, etc.)
          const aScore = a.score || 0
          const bScore = b.score || 0
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
