import BookList from '../components/BookList'
import BookForm from '../components/BookForm'
import BookSortBar from '../components/BookSortBar'
import BookFilterBar from '../components/BookFilterBar'
import BookAnalytics from '../components/BookAnalytics'

export const booksConfig = {
  // Basic metadata
  type: 'books',
  titleSingular: 'Book',
  titlePlural: 'Books',

  // API configuration
  apiEndpoint: 'books',
  cacheKey: 'cachedBooks',

  // LocalStorage keys
  localStorageKeys: {
    viewMode: 'booksViewMode',
    searchTerm: 'booksSearchTerm',
    activeFilter: 'booksActiveFilter',
    sortConfig: 'booksSortConfig',
    showAnalytics: 'booksShowAnalytics',
  },

  // Page titles
  pageTitles: {
    main: 'Books | James Raybould',
    admin: 'Admin | Books | James Raybould',
  },

  // Components
  components: {
    List: BookList,
    Form: BookForm,
    SortBar: BookSortBar,
    FilterBar: BookFilterBar,
    Analytics: BookAnalytics,
  },

  // Filter configuration
  filterFields: {
    rating: [],
    type: [],
    form: [],
    year: [],
    author: [],
  },

  // Empty state messages
  emptyState: {
    message: 'Nope, nothing here!',
    hint: "Either you're searching wrong or James hasn't read the book :)",
  },

  // Format title function (books don't need special formatting)
  formatTitle: (title) => title || '',

  // Search function
  searchFilter: (item, searchLower) => {
    const bookName = (item.book_name || '').toLowerCase()
    const author = (item.author || '').toLowerCase()
    return bookName.includes(searchLower) || author.includes(searchLower)
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
    const config = booksConfig
    return items.filter(item => {
      if (!item.j_rayting) return false
      
      // Check if exact match
      if (selectedRatings.includes(item.j_rayting)) return true
      
      // Check if combo rating's higher rating matches any selected rating
      if (item.j_rayting.includes('/')) {
        const higherRating = config.getHigherRating(item.j_rayting)
        return selectedRatings.includes(higherRating)
      }
      
      return false
    })
  },

  applyTypeFilter: (items, selectedTypes) => {
    return items.filter(item => selectedTypes.includes(item.type))
  },

  applyFormFilter: (items, selectedForms) => {
    return items.filter(item => selectedForms.includes(item.form))
  },

  applyYearFilter: (items, selectedYears) => {
    return items.filter(item => {
      if (!item.year) return false
      return selectedYears.includes(item.year.toString())
    })
  },

  applyAuthorFilter: (items, selectedAuthors) => {
    return items.filter(item => {
      if (!item.author) return false
      const authorLower = item.author.toLowerCase()
      return selectedAuthors.some(selectedAuthor =>
        authorLower.includes(selectedAuthor.toLowerCase())
      )
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
        // For A-grade books (A+, A/A+, A), use a_grade_rank if available
        const aIsAGrade = a.j_rayting && ['A+', 'A/A+', 'A'].includes(a.j_rayting)
        const bIsAGrade = b.j_rayting && ['A+', 'A/A+', 'A'].includes(b.j_rayting)

        if (aIsAGrade && bIsAGrade) {
          // Both are A-grade: first sort by letter rating (A+ > A/A+ > A), then by rank
          const ratingOrder = { 'A+': 1, 'A/A+': 2, 'A': 3 }
          const aRatingOrder = ratingOrder[a.j_rayting] || 999
          const bRatingOrder = ratingOrder[b.j_rayting] || 999

          // First compare by rating (A+ comes before A/A+, which comes before A)
          if (aRatingOrder !== bRatingOrder) {
            comparison = aRatingOrder - bRatingOrder
          } else {
            // Same rating: use a_grade_rank (lower rank = better, so rank 1 comes before rank 2)
            const aRank = (a.a_grade_rank !== null && a.a_grade_rank !== undefined) ? a.a_grade_rank : 9999
            const bRank = (b.a_grade_rank !== null && b.a_grade_rank !== undefined) ? b.a_grade_rank : 9999
            comparison = aRank - bRank
          }
        } else if (aIsAGrade && !bIsAGrade) {
          comparison = -1
        } else if (!aIsAGrade && bIsAGrade) {
          comparison = 1
        } else {
          // Neither is A-grade: use numeric score field
          const aScore = a.score || 0
          const bScore = b.score || 0
          comparison = bScore - aScore
        }
      } else if (actualSortBy === 'date') {
        // Date read
        const parseDate = (dateStr) => {
          if (!dateStr) return new Date(0)

          if (dateStr.includes('-')) {
            const parts = dateStr.split('-')
            if (parts.length === 3) {
              return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
            }
          }

          if (dateStr.includes('/')) {
            const parts = dateStr.split('/')
            if (parts.length === 3) {
              return new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]))
            }
          }

          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          if (dateStr.includes('-') && dateStr.length <= 7) {
            const parts = dateStr.split('-')
            if (parts.length === 2) {
              const monthIndex = monthNames.indexOf(parts[0])
              if (monthIndex !== -1) {
                const year = 2000 + parseInt(parts[1])
                return new Date(year, monthIndex, 1)
              }
            }
          }

          const parsed = new Date(dateStr)
          return isNaN(parsed.getTime()) ? new Date(0) : parsed
        }

        const aDate = parseDate(a.date_read)
        const bDate = parseDate(b.date_read)
        comparison = bDate - aDate
      } else if (actualSortBy === 'dateWritten') {
        // Date written
        const parseDate = (dateStr) => {
          if (!dateStr) return new Date(0)

          if (dateStr.includes('-')) {
            const parts = dateStr.split('-')
            if (parts.length === 3) {
              return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
            }
          }

          if (dateStr.includes('/')) {
            const parts = dateStr.split('/')
            if (parts.length === 3) {
              return new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]))
            }
          }

          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          if (dateStr.includes('-') && dateStr.length <= 7) {
            const parts = dateStr.split('-')
            if (parts.length === 2) {
              const monthIndex = monthNames.indexOf(parts[0])
              if (monthIndex !== -1) {
                const year = 2000 + parseInt(parts[1])
                return new Date(year, monthIndex, 1)
              }
            }
          }

          if (/^\d{4}$/.test(dateStr)) {
            return new Date(parseInt(dateStr), 0, 1)
          }

          const parsed = new Date(dateStr)
          return isNaN(parsed.getTime()) ? new Date(0) : parsed
        }

        const aDate = parseDate(a.published_date)
        const bDate = parseDate(b.published_date)
        comparison = bDate - aDate
      } else if (actualSortBy === 'pages') {
        const aPages = a.pages || 0
        const bPages = b.pages || 0
        comparison = bPages - aPages
      }

      // If primary sort is equal, sort alphabetically by book name
      if (comparison === 0) {
        comparison = (a.book_name || '').localeCompare(b.book_name || '', undefined, { numeric: true, sensitivity: 'base' })
      }

      return direction === 'desc' ? comparison : -comparison
    })

    return sorted
  },
}
