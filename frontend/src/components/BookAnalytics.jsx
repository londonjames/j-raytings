import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

function BookAnalytics() {
  const [yearData, setYearData] = useState([])
  const [typeData, setTypeData] = useState([])
  const [formData, setFormData] = useState([])
  const [authorData, setAuthorData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllAnalytics()
  }, [])

  const fetchAllAnalytics = async () => {
    try {
      const [yearResponse, typeResponse, formResponse, authorResponse] = await Promise.all([
        fetch(`${API_URL}/analytics/books/by-year`),
        fetch(`${API_URL}/analytics/books/by-type`),
        fetch(`${API_URL}/analytics/books/by-form`),
        fetch(`${API_URL}/analytics/books/by-author`)
      ])

      // Check for errors
      if (!yearResponse.ok) throw new Error(`Year analytics failed: ${yearResponse.status}`)
      if (!typeResponse.ok) throw new Error(`Type analytics failed: ${typeResponse.status}`)
      if (!formResponse.ok) throw new Error(`Form analytics failed: ${formResponse.status}`)
      if (!authorResponse.ok) throw new Error(`Author analytics failed: ${authorResponse.status}`)

      const yearAnalytics = await yearResponse.json()
      const typeAnalytics = await typeResponse.json()
      const formAnalytics = await formResponse.json()
      const authorAnalytics = await authorResponse.json()

      // Collapse "kindle" variants into "Kindle" for form data
      const normalizedFormData = Array.isArray(formAnalytics) ? formAnalytics.map(item => {
        if (item.form && item.form.toLowerCase() === 'kindle') {
          return { ...item, form: 'Kindle' }
        }
        return item
      }) : []
      
      // Consolidate all form entries (especially Kindle variants)
      const formMap = new Map()
      normalizedFormData.forEach(item => {
        const key = item.form || 'Unknown'
        if (formMap.has(key)) {
          const existing = formMap.get(key)
          const newCount = existing.count + (item.count || 0)
          // Calculate weighted average for avg_score
          const existingTotal = existing.avg_score != null ? existing.avg_score * existing.count : 0
          const itemTotal = item.avg_score != null ? item.avg_score * (item.count || 0) : 0
          const newAvgScore = newCount > 0 ? (existingTotal + itemTotal) / newCount : null
          
          formMap.set(key, {
            ...existing,
            count: newCount,
            avg_score: newAvgScore
          })
        } else {
          formMap.set(key, { ...item })
        }
      })
      const consolidatedFormData = Array.from(formMap.values())

      // Format author names from "Last, First" to "First Last"
      const formattedAuthorData = Array.isArray(authorAnalytics) ? authorAnalytics.map(author => {
        if (author.author && author.author.includes(',')) {
          const parts = author.author.split(',').map(s => s.trim())
          if (parts.length === 2) {
            return { ...author, author: `${parts[1]} ${parts[0]}` }
          }
        }
        return author
      }) : []

      setYearData(Array.isArray(yearAnalytics) ? yearAnalytics : [])
      setTypeData(Array.isArray(typeAnalytics) ? typeAnalytics : [])
      setFormData(consolidatedFormData)
      setAuthorData(formattedAuthorData)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching book analytics:', error)
      setYearData([])
      setTypeData([])
      setFormData([])
      setAuthorData([])
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>
  }

  // Filter books data to start from 1999 (remove 1995 and 1998)
  const filteredYearData = yearData.filter(d => d.year >= 1999)
  
  // Reverse year data order for books (2025 on right, oldest on left)
  const reversedYearData = [...filteredYearData].reverse()

  // Check if any data has scores over 15 to determine if we need to extend range to 16
  const allData = [...reversedYearData, ...typeData, ...formData]
  const maxScore = Math.max(...allData.map(d => d.avg_score || 0).filter(s => s > 0), 15)
  const needsExtendedRange = maxScore > 15
  const scoreTicks = needsExtendedRange ? [10, 11, 12, 13, 14, 15, 16] : [10, 11, 12, 13, 14, 15]
  const scoreMax = needsExtendedRange ? 16 : 15

  // Format category labels for analytics display only (not database)
  const formatCategoryLabel = (val) => {
    const categoryMap = {
      'Non-Fict: Soc.': 'Non-Fict: Society',
      'Non-Fict: Biz': 'Non-Fict: Business',
      'Non-Fict: Pol.': 'Non-Fict: Politics'
    }
    return categoryMap[val] || val
  }

  return (
    <div className="analytics-container">
      <AnalyticsSection
        title="BY YEAR READ"
        data={reversedYearData}
        dataKey="year"
        formatLabel={(val) => val}
        scoreRange={{ min: 10, max: scoreMax, ticks: scoreTicks }}
        countRange="auto"
      />

      <AnalyticsSection
        title="BY TYPE"
        data={typeData}
        dataKey="type"
        formatLabel={formatCategoryLabel}
        scoreRange={{ min: 10, max: scoreMax, ticks: scoreTicks }}
        countRange={{ max: 300, step: 50 }}
      />

      <AnalyticsSection
        title="BY FORM"
        data={formData}
        dataKey="form"
        formatLabel={(val) => val}
        scoreRange={{ min: 10, max: scoreMax, ticks: scoreTicks }}
        countRange={{ max: 400, step: 50 }}
      />

      {/* Top Authors - Simple list */}
      {authorData.length > 0 && (
        <div className="analytics-section">
          <h2 className="analytics-section-title">TOP AUTHORS</h2>
          <div className="author-list">
            {authorData.slice(0, 10).map((author, index) => (
              <div key={author.author} className="author-item">
                <span className="author-rank">{index + 1}.</span>
                <span className="author-name">{author.author}</span>
                <span className="author-count">{author.count} books</span>
                {author.avg_score != null && (
                  <span className="author-score">Avg.: {scoreToGrade(Math.round(author.avg_score))}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Convert numeric score to letter grade for display
const scoreToGrade = (score) => {
  const gradeMap = {
    10: 'B-',
    11: 'B/B-',
    12: 'B',
    13: 'B/B+',
    14: 'B+',
    15: 'B+/A-',
    16: 'A-'
  }
  return gradeMap[score] || score.toString()
}

function AnalyticsSection({ title, data, dataKey, formatLabel, scoreRange, countRange }) {
  if (data.length === 0) {
    return null
  }

  // Chart dimensions
  const width = 1100
  const height = 220
  const bottomPadding = 35
  const padding = { top: 25, right: 30, bottom: bottomPadding, left: 55 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Get data ranges
  const counts = data.map(d => d.count || 0)
  const scores = data.map(d => d.avg_score || 0)

  const maxCount = counts.length > 0 ? Math.max(...counts) : 0
  const totalPoints = data.length

  // Calculate max Y for count
  let maxCountY
  let countStep
  if (countRange === 'auto') {
    maxCountY = maxCount > 0 ? Math.ceil(maxCount / 20) * 20 : 20
    countStep = 20
  } else {
    maxCountY = countRange.max || 20
    countStep = countRange.step || 20
  }

  // Scale functions
  const scaleX = (index) => {
    const spacing = chartWidth / totalPoints
    return padding.left + (spacing * 0.4) + (index * spacing)
  }

  const scaleYCount = (count) => {
    return padding.top + chartHeight - (count / maxCountY) * chartHeight
  }

  const scaleYScore = (score) => {
    if (score == null || isNaN(score)) return padding.top + chartHeight // Default to bottom if null/NaN
    const minScore = scoreRange.min
    const maxScore = scoreRange.max
    return padding.top + chartHeight - ((score - minScore) / (maxScore - minScore)) * chartHeight
  }

  // Generate paths
  const countPath = data.map((d, i) => {
    const x = scaleX(i)
    const y = scaleYCount(d.count || 0)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')

  const scorePath = data
    .filter(d => d.avg_score != null && !isNaN(d.avg_score)) // Filter out null/NaN scores
    .map((d, i, filteredData) => {
      const originalIndex = data.indexOf(d)
      const x = scaleX(originalIndex)
      const y = scaleYScore(d.avg_score)
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
    })
    .join(' ')

  // Generate Y-axis ticks
  const countTicks = []
  for (let i = 0; i <= maxCountY; i += countStep) {
    countTicks.push(i)
  }

  const scoreTicks = scoreRange.ticks

  return (
    <div className="analytics-section">
      <h2 className="analytics-section-title">{title}</h2>

      {/* Chart 1: Total Books */}
      <div 
        className="chart-section"
        onWheel={(e) => {
          // Enable horizontal scrolling with mouse wheel (when holding Shift or on trackpad)
          if (e.shiftKey || Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
            e.preventDefault()
            e.currentTarget.scrollLeft += e.deltaX || e.deltaY
          }
        }}
      >
        <div className="chart-container">
          <svg width={width} height={height} style={{ minWidth: width, overflow: 'visible' }} viewBox={`-20 0 ${width + 20} ${height}`}>
            {/* Grid lines */}
            {countTicks.map(tick => (
              <line
                key={`count-grid-${tick}`}
                x1={padding.left}
                y1={scaleYCount(tick)}
                x2={width - padding.right}
                y2={scaleYCount(tick)}
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth="1"
              />
            ))}

            {/* Axes */}
            <line
              x1={padding.left}
              y1={height - padding.bottom}
              x2={width - padding.right}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />
            <line
              x1={padding.left}
              y1={padding.top}
              x2={padding.left}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />

            {/* X-axis labels */}
            {data.map((d, i) => {
              const x = scaleX(i)
              return (
                <text
                  key={`count-x-${d[dataKey]}`}
                  x={x}
                  y={height - padding.bottom + 20}
                  textAnchor="middle"
                  fill="#999"
                  fontSize="13"
                >
                  {formatLabel(d[dataKey])}
                </text>
              )
            })}

            {/* Y-axis labels */}
            {countTicks.map(tick => (
              <text
                key={`count-y-${tick}`}
                x={padding.left - 10}
                y={scaleYCount(tick)}
                textAnchor="end"
                fill="#999"
                fontSize="12"
                alignmentBaseline="middle"
              >
                {tick}
              </text>
            ))}

            {/* Y-axis title */}
            <text
              x={padding.left - 48}
              y={padding.top + chartHeight / 2}
              textAnchor="middle"
              fill="#999"
              fontSize="13"
              fontWeight="500"
              transform={`rotate(-90, ${padding.left - 48}, ${padding.top + chartHeight / 2})`}
            >
              Total Books Read
            </text>

            {/* Count line */}
            <path
              d={countPath}
              fill="none"
              stroke="#4a9eff"
              strokeWidth="3"
            />

            {/* Data points */}
            {data.map((d, i) => {
              const x = scaleX(i)
              const y = scaleYCount(d.count)
              return (
                <g key={`count-data-${d[dataKey]}`}>
                  <circle cx={x} cy={y} r="4" fill="#4a9eff" />
                  <text
                    x={x}
                    y={y - 10}
                    textAnchor="middle"
                    fill="#4a9eff"
                    fontSize="12"
                    fontWeight="600"
                  >
                    {d.count}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      </div>

      {/* Chart 2: Average Rating */}
      <div 
        className="chart-section"
        onWheel={(e) => {
          // Enable horizontal scrolling with mouse wheel (when holding Shift or on trackpad)
          if (e.shiftKey || Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
            e.preventDefault()
            e.currentTarget.scrollLeft += e.deltaX || e.deltaY
          }
        }}
      >
        <div className="chart-container">
          <svg width={width} height={height} style={{ minWidth: width, overflow: 'visible' }} viewBox={`-20 0 ${width + 20} ${height}`}>
            {/* Grid lines */}
            {scoreTicks.map(tick => (
              <line
                key={`score-grid-${tick}`}
                x1={padding.left}
                y1={scaleYScore(tick)}
                x2={width - padding.right}
                y2={scaleYScore(tick)}
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth="1"
              />
            ))}

            {/* Axes */}
            <line
              x1={padding.left}
              y1={height - padding.bottom}
              x2={width - padding.right}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />
            <line
              x1={padding.left}
              y1={padding.top}
              x2={padding.left}
              y2={height - padding.bottom}
              stroke="#666"
              strokeWidth="2"
            />

            {/* X-axis labels */}
            {data.map((d, i) => {
              const x = scaleX(i)
              return (
                <text
                  key={`score-x-${d[dataKey]}`}
                  x={x}
                  y={height - padding.bottom + 20}
                  textAnchor="middle"
                  fill="#999"
                  fontSize="13"
                >
                  {formatLabel(d[dataKey])}
                </text>
              )
            })}

            {/* Y-axis labels */}
            {scoreTicks.map(tick => (
              <text
                key={`score-y-${tick}`}
                x={padding.left - 10}
                y={scaleYScore(tick)}
                textAnchor="end"
                fill="#999"
                fontSize="12"
                alignmentBaseline="middle"
              >
                {scoreToGrade(tick)}
              </text>
            ))}

            {/* Y-axis title */}
            <text
              x={padding.left - 48}
              y={padding.top + chartHeight / 2}
              textAnchor="middle"
              fill="#999"
              fontSize="13"
              fontWeight="500"
              transform={`rotate(-90, ${padding.left - 48}, ${padding.top + chartHeight / 2})`}
            >
              Average J-Rayting
            </text>

            {/* Score line */}
            <path
              d={scorePath}
              fill="none"
              stroke="#ff6b6b"
              strokeWidth="3"
            />

            {/* Data points */}
            {data.map((d, i) => {
              if (d.avg_score == null || isNaN(d.avg_score)) return null // Skip null/NaN scores
              const x = scaleX(i)
              const y = scaleYScore(d.avg_score)
              return (
                <g key={`score-data-${d[dataKey]}`}>
                  <circle cx={x} cy={y} r="4" fill="#ff6b6b" />
                  <text
                    x={x}
                    y={y - 10}
                    textAnchor="middle"
                    fill="#ff6b6b"
                    fontSize="12"
                    fontWeight="600"
                  >
                    {d.avg_score.toFixed(1)}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      </div>
    </div>
  )
}

export default BookAnalytics

