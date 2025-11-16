# Film Tracker

A personal film tracking website to log and manage all the films you've watched, including ratings, watch dates, and detailed metadata. Import your film history from Google Sheets!

## Features

- **Import from Google Sheets**: Automatically import your entire film collection
- **Rich Metadata**: Track letter ratings (A+, A, etc.), numeric scores (1-20), dates watched, locations, formats, and more
- **Smart Filters**: Search by title, filter by location, format, and minimum score
- **Detailed Stats**: View total films, average score, and filtered results
- **Rotten Tomatoes Integration**: Display RT scores and ratings per minute
- **Beautiful UI**: Clean, responsive design with gradient backgrounds and card layouts

## Tech Stack

- **Frontend**: React (Vite)
- **Backend**: Python Flask
- **Database**: SQLite

## Quick Start

### 1. Backend Setup

Navigate to the backend directory and install dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Import Your Films from Google Sheets

Run the import script to load your film data:
```bash
python import_films.py
```

This will download your film collection from Google Sheets and import all 1,800+ films into the database!

### 3. Start the Backend Server

```bash
python app.py
```

The backend will run on `http://localhost:5000`

### 4. Frontend Setup

In a new terminal, navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173`

### 5. View Your Films!

Open your browser to `http://localhost:5173` and explore your film collection!

## Usage

- **Browse**: See all your films in a beautiful card layout
- **Search**: Type a film title in the search box
- **Filter**: Use location, format, and minimum score filters
- **Stats**: View total films watched and average score
- **Add/Edit**: Click "Add New Film" or "Edit" on any film card
- **Delete**: Remove films with confirmation

## Database Schema

The SQLite database contains a `films` table with the following fields:

- `id`: Primary key
- `order_number`: Original order from spreadsheet
- `date_seen`: Date film was watched (e.g., "1990s", "Oct-10")
- `title`: Film title (required)
- `letter_rating`: Letter grade (A+, A, A-, B+, etc.)
- `score`: Numeric score (1-20)
- `year_watched`: Year watched (e.g., "Pre-2006", "2010")
- `location`: Where the film was seen
- `format`: Viewing format (Theatre, DVD, VHS, Streaming, Blu-ray)
- `release_year`: Original release year
- `rotten_tomatoes`: RT percentage
- `length_minutes`: Film length in minutes
- `rt_per_minute`: RT score per minute metric
- `created_at`: Timestamp

## API Endpoints

- `GET /api/films` - Get all films (supports ?search, ?location, ?format, ?min_score query params)
- `GET /api/films/<id>` - Get a single film
- `POST /api/films` - Add a new film
- `PUT /api/films/<id>` - Update a film
- `DELETE /api/films/<id>` - Delete a film

## Google Sheets Integration

The app is configured to import from your Google Sheets film database. The import script (`backend/import_films.py`) automatically:

- Downloads the CSV export from your Google Sheet
- Parses all columns including ratings, locations, formats, and RT scores
- Handles the spreadsheet's formatting quirks (empty first row/column)
- Imports all 1,800+ films in seconds

**Note**: Make sure your Google Sheet is shared with "Anyone with the link can view" for the import to work.

## Future Enhancements

- Movie poster integration (TMDB API)
- Charts and analytics (viewing trends over time, rating distribution by decade)
- Sync with Google Sheets (bidirectional updates)
- Advanced sorting options
- Export to various formats
- Dark mode toggle
