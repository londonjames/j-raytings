import ShowList from '../components/ShowList'
import ShowForm from '../components/ShowForm'
import ShowSortBar from '../components/ShowSortBar'
import ShowFilterBar from '../components/ShowFilterBar'
import ShowAnalytics from '../components/ShowAnalytics'

export const showsConfig = {
  // Basic metadata
  type: 'shows',
  titleSingular: 'Show',
  titlePlural: 'Shows',

  // API configuration
  apiEndpoint: 'shows',
  cacheKey: 'cachedShows',

  // LocalStorage keys
  localStorageKeys: {
    viewMode: 'showsViewMode',
    searchTerm: 'showsSearchTerm',
    activeFilter: 'showsActiveFilter',
    sortConfig: 'showsSortConfig',
    showAnalytics: 'showsShowAnalytics',
  },

  // Page titles
  pageTitles: {
    main: 'Shows | James Raybould',
    admin: 'Admin | Shows | James Raybould',
  },

  // Components
  components: {
    List: ShowList,
    Form: ShowForm,
    SortBar: ShowSortBar,
    FilterBar: ShowFilterBar,
    Analytics: ShowAnalytics,
  },

  // Filter configuration
  filterFields: {
    rating: [],
    genre: [],
    decade: [],
    imdb: [],
  },

  // Empty state messages
  emptyState: {
    message: 'Nope, nothing here!',
    hint: "Either you're searching wrong or James hasn't watched the show :)",
  },

  // Format title function (shows don't need special formatting)
  formatTitle: (title) => title || '',

  // Search function
  searchFilter: (item, searchLower) => {
    const showTitle = (item.title || '').toLowerCase()
    return showTitle.includes(searchLower)
  },

  // Helper function to get the higher rating from a combo rating
  getHigherRating: (rating) => {
    if (!rating) return null
    if (!rating.includes('/')) return rating

    const parts = rating.split('/').map(r => r.trim())
    if (parts.length !== 2) return rating

    const ratingOrder = {
      'A+': 20, 'A/A+': 19, 'A': 18, 'A-/A': 17, 'A-': 16,
      'B+/A-': 15, 'B+': 14, 'B/B+': 13, 'B': 12, 'B-/B': 11, 'B-': 10,
      'C+/B-': 9, 'C+': 8, 'C/C+': 7, 'C': 6, 'C-': 5,
      'D+': 4, 'D': 3
    }

    const part1Order = ratingOrder[parts[0]] || 0
    const part2Order = ratingOrder[parts[1]] || 0

    return part1Order > part2Order ? parts[0] : parts[1]
  },

  // Filter functions
  applyRatingFilter: (items, selectedRatings) => {
    const config = showsConfig
    return items.filter(item => {
      if (!item.j_rayting) return false

      if (selectedRatings.includes(item.j_rayting)) return true

      if (item.j_rayting.includes('/')) {
        const higherRating = config.getHigherRating(item.j_rayting)
        return selectedRatings.includes(higherRating)
      }

      return false
    })
  },

  applyGenreFilter: (items, selectedGenres) => {
    return items.filter(item => {
      if (!item.genres) return false
      const itemGenres = item.genres.split(', ')
      return selectedGenres.some(selectedGenre => itemGenres.includes(selectedGenre))
    })
  },

  applyDecadeFilter: (items, selectedDecades) => {
    return items.filter(item => {
      if (!item.start_year) return false
      const year = parseInt(item.start_year)

      return selectedDecades.some(selectedDecade => {
        if (selectedDecade === 'Pre-1990') {
          return year < 1990
        } else {
          const decade = selectedDecade.replace('s', '')
          const decadeStart = parseInt(decade)
          return year >= decadeStart && year < decadeStart + 10
        }
      })
    })
  },

  applyImdbFilter: (items, selectedImdbRanges) => {
    return items.filter(item => {
      if (!item.imdb_rating) return false
      const rating = parseFloat(item.imdb_rating)
      if (isNaN(rating)) return false

      return selectedImdbRanges.some(range => {
        if (range === '≥9.0') return rating >= 9.0
        if (range === '8.0-8.9') return rating >= 8.0 && rating < 9.0
        if (range === '7.0-7.9') return rating >= 7.0 && rating < 8.0
        if (range === '6.0-6.9') return rating >= 6.0 && rating < 7.0
        if (range === '5.0-5.9') return rating >= 5.0 && rating < 6.0
        if (range === '<5.0') return rating < 5.0
        return false
      })
    })
  },

  // Sort function
  sortItems: (items, sortBy, direction) => {
    const sorted = [...items]

    sorted.sort((a, b) => {
      let comparison = 0

      const actualSortBy = sortBy || 'rating'

      if (actualSortBy === 'rating') {
        // For A-grade shows, use a_grade_rank if available
        const aIsAGrade = a.j_rayting && ['A+', 'A/A+', 'A'].includes(a.j_rayting)
        const bIsAGrade = b.j_rayting && ['A+', 'A/A+', 'A'].includes(b.j_rayting)

        if (aIsAGrade && bIsAGrade) {
          const ratingOrder = { 'A+': 1, 'A/A+': 2, 'A': 3 }
          const aRatingOrder = ratingOrder[a.j_rayting] || 999
          const bRatingOrder = ratingOrder[b.j_rayting] || 999

          if (aRatingOrder !== bRatingOrder) {
            comparison = aRatingOrder - bRatingOrder
          } else {
            const aRank = (a.a_grade_rank !== null && a.a_grade_rank !== undefined) ? a.a_grade_rank : 9999
            const bRank = (b.a_grade_rank !== null && b.a_grade_rank !== undefined) ? b.a_grade_rank : 9999
            comparison = aRank - bRank
          }
        } else if (aIsAGrade && !bIsAGrade) {
          comparison = -1
        } else if (!aIsAGrade && bIsAGrade) {
          comparison = 1
        } else {
          const aScore = a.score || 0
          const bScore = b.score || 0
          comparison = bScore - aScore
        }
      } else if (actualSortBy === 'year') {
        const aYear = parseInt(a.start_year) || 0
        const bYear = parseInt(b.start_year) || 0
        comparison = bYear - aYear // Newer first
      } else if (actualSortBy === 'imdb') {
        const aIMDB = parseFloat(a.imdb_rating) || 0
        const bIMDB = parseFloat(b.imdb_rating) || 0
        comparison = bIMDB - aIMDB // Higher IMDB first
      } else if (actualSortBy === 'seasons') {
        const aSeasons = a.seasons || 0
        const bSeasons = b.seasons || 0
        comparison = bSeasons - aSeasons // More seasons first
      }

      // If primary sort is equal, sort alphabetically by title
      if (comparison === 0) {
        comparison = (a.title || '').localeCompare(b.title || '', undefined, { numeric: true, sensitivity: 'base' })
      }

      return direction === 'desc' ? comparison : -comparison
    })

    return sorted
  },
}
