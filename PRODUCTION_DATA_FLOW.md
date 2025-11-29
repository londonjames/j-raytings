# Production Data Flow - Source of Truth

## ✅ CONFIRMED: Production (PostgreSQL) is the Source of Truth

### Backend Configuration

**How it works:**
- The backend (`backend/app.py`) automatically detects the database type:
  - If `DATABASE_URL` environment variable is set → Uses **PostgreSQL** (production)
  - If `DATABASE_URL` is not set → Uses **SQLite** (local development)

**In Production (Railway):**
- `DATABASE_URL` is set → Backend uses PostgreSQL
- All API endpoints (`POST /api/films`, `POST /api/books`, `PUT`, `DELETE`) write directly to PostgreSQL
- All edits made through the admin panel (`/films/admin`, `/books/admin`) are saved to PostgreSQL

**In Local Development:**
- `DATABASE_URL` is not set → Backend uses SQLite (`films.db`)
- Local edits are saved to SQLite only

### Sync Scripts (Fixed)

**Both sync scripts now preserve production data:**

1. **`backend/sync_to_postgres.py`** (Films)
   - ✅ Merges data instead of replacing
   - ✅ Preserves films added in production
   - ✅ Updates existing films from SQLite
   - ✅ Inserts new films from SQLite

2. **`backend/sync_books_to_postgres.py`** (Books)
   - ✅ Merges data instead of replacing
   - ✅ Preserves books added in production
   - ✅ Updates existing books from SQLite
   - ✅ Inserts new books from SQLite

### Workflow

**For all edits going forward:**
1. ✅ Make edits in production via admin panel (`/films/admin` or `/books/admin`)
2. ✅ Edits are saved directly to PostgreSQL (production database)
3. ✅ Production data is preserved and never overwritten
4. ✅ Sync scripts can be run safely - they will merge, not replace

### Verification

**To confirm production is working:**
- Check Railway environment variables: `DATABASE_URL` should be set
- Check backend logs: Should show "Using PostgreSQL" or similar
- Test: Add a film/book in production admin → It should persist

**Important Notes:**
- ⚠️ Never run sync scripts that DELETE from production
- ✅ All sync scripts now use UPDATE/INSERT merge pattern
- ✅ Production entries are always preserved

