import { useState, useEffect } from 'react'

function BookForm({ book, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    book_name: '',
    author: '',
    date_read: '',
    year: '',
    year_written: '',
    j_rayting: '',
    score: '',
    type: '',
    pages: '',
    form: '',
    notes_in_notion: '',
    notion_link: '',
    order_number: '',
    cover_url: ''
  })

  useEffect(() => {
    if (book) {
      setFormData({
        book_name: book.book_name || '',
        author: book.author || '',
        date_read: book.date_read || '',
        year: book.year || '',
        year_written: book.year_written || '',
        j_rayting: book.j_rayting || '',
        score: book.score || '',
        type: book.type || '',
        pages: book.pages || '',
        form: book.form || '',
        notes_in_notion: book.notes_in_notion || '',
        notion_link: book.notion_link || '',
        order_number: book.order_number || '',
        cover_url: book.cover_url || ''
      })
    }
  }, [book])

  const handleSubmit = (e) => {
    e.preventDefault()

    // Convert empty strings to null for numeric fields
    const dataToSave = {
      ...formData,
      order_number: formData.order_number ? parseInt(formData.order_number) : null,
      score: formData.score ? parseInt(formData.score) : null,
      year: formData.year ? parseInt(formData.year) : null,
      year_written: formData.year_written ? parseInt(formData.year_written) : null,
      pages: formData.pages ? parseInt(formData.pages) : null
    }

    onSave(dataToSave)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <div className="film-form-overlay">
      <div className="film-form">
        <div className="film-form-header">
          <h2>{book ? 'Edit Book' : 'Add New Book'}</h2>
          <button
            type="button"
            className="film-form-close-btn"
            onClick={onCancel}
            title="Close"
            aria-label="Close form"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form onSubmit={handleSubmit}>

          {/* Primary Fields */}
          <div className="form-section">
            <h3>Primary Info (Fill These In)</h3>

            <div className="form-group">
              <label htmlFor="book_name">Book Name *</label>
              <input
                type="text"
                id="book_name"
                name="book_name"
                value={formData.book_name}
                onChange={handleChange}
                required
                placeholder="e.g., The Great Gatsby"
              />
            </div>

            <div className="form-group">
              <label htmlFor="author">Author *</label>
              <input
                type="text"
                id="author"
                name="author"
                value={formData.author}
                onChange={handleChange}
                required
                placeholder="e.g., F. Scott Fitzgerald"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="date_read">Date Read</label>
                <input
                  type="date"
                  id="date_read"
                  name="date_read"
                  value={formData.date_read}
                  onChange={handleChange}
                  placeholder="Leave blank if unknown"
                />
              </div>

              <div className="form-group">
                <label htmlFor="year">Year Read</label>
                <input
                  type="number"
                  id="year"
                  name="year"
                  min="1900"
                  max={new Date().getFullYear()}
                  value={formData.year}
                  onChange={handleChange}
                  placeholder="e.g., 2024"
                />
              </div>

              <div className="form-group">
                <label htmlFor="year_written">Year Written</label>
                <input
                  type="number"
                  id="year_written"
                  name="year_written"
                  min="0"
                  max={new Date().getFullYear()}
                  value={formData.year_written}
                  onChange={handleChange}
                  placeholder="e.g., 1979"
                />
              </div>

              <div className="form-group">
                <label htmlFor="j_rayting">Grade *</label>
                <select
                  id="j_rayting"
                  name="j_rayting"
                  value={formData.j_rayting}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Grade</option>
                  <option value="A+">A+</option>
                  <option value="A/A+">A/A+</option>
                  <option value="A">A</option>
                  <option value="A-/A">A-/A</option>
                  <option value="A-">A-</option>
                  <option value="B+/A-">B+/A-</option>
                  <option value="B+">B+</option>
                  <option value="B/B+">B/B+</option>
                  <option value="B">B</option>
                  <option value="B-/B">B-/B</option>
                  <option value="B-">B-</option>
                  <option value="C+/B-">C+/B-</option>
                  <option value="C+">C+</option>
                  <option value="C/C+">C/C+</option>
                  <option value="C">C</option>
                  <option value="C-">C-</option>
                  <option value="D+">D+</option>
                  <option value="D">D</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="type">Type</label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                >
                  <option value="">Select Type</option>
                  <option value="Fiction">Fiction</option>
                  <option value="Non-fiction: Business">Non-fiction: Business</option>
                  <option value="Non-fiction: Social">Non-fiction: Social</option>
                  <option value="Non-fiction: Sport">Non-fiction: Sport</option>
                  <option value="Non-fiction: Bio">Non-fiction: Bio</option>
                  <option value="Non-fiction: Politics">Non-fiction: Politics</option>
                  <option value="Non-fiction: True Crime">Non-fiction: True Crime</option>
                  <option value="Non-fiction">Non-fiction</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="form">Form</label>
                <select
                  id="form"
                  name="form"
                  value={formData.form}
                  onChange={handleChange}
                >
                  <option value="">Select Form</option>
                  <option value="Kindle">Kindle</option>
                  <option value="Book">Book</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="pages">Pages</label>
                <input
                  type="number"
                  id="pages"
                  name="pages"
                  min="1"
                  value={formData.pages}
                  onChange={handleChange}
                  placeholder="Number of pages"
                />
              </div>
            </div>
          </div>

          {/* Additional Fields */}
          <div className="form-section">
            <h3>Additional Info (Optional)</h3>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="score">Score (0-20)</label>
                <input
                  type="number"
                  id="score"
                  name="score"
                  min="0"
                  max="20"
                  value={formData.score}
                  onChange={handleChange}
                  placeholder="Auto-calculated from grade"
                />
              </div>

              <div className="form-group">
                <label htmlFor="order_number">Order #</label>
                <input
                  type="number"
                  id="order_number"
                  name="order_number"
                  value={formData.order_number}
                  onChange={handleChange}
                  placeholder="Sequence number"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="notes_in_notion">Notes in Notion</label>
              <input
                type="text"
                id="notes_in_notion"
                name="notes_in_notion"
                value={formData.notes_in_notion}
                onChange={handleChange}
                placeholder="YES or NO"
              />
            </div>

            <div className="form-group">
              <label htmlFor="notion_link">Notion Link</label>
              <input
                type="url"
                id="notion_link"
                name="notion_link"
                value={formData.notion_link}
                onChange={handleChange}
                placeholder="https://www.notion.so/..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="cover_url">Cover URL / Image URL</label>
              <input
                type="url"
                id="cover_url"
                name="cover_url"
                value={formData.cover_url}
                onChange={handleChange}
                placeholder="Paste image URL here (e.g., https://example.com/cover.jpg)"
              />
              {formData.cover_url && (
                <div style={{ marginTop: '10px' }}>
                  <img 
                    src={formData.cover_url} 
                    alt="Preview" 
                    style={{ 
                      maxWidth: '200px', 
                      maxHeight: '300px', 
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div style={{ display: 'none', color: '#999', fontSize: '0.85rem', marginTop: '5px' }}>
                    Image failed to load. Check URL.
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              {book ? 'Update Book' : 'Add Book'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default BookForm

