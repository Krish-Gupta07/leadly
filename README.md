# Leadly - Reddit Lead Finder

Leadly is an automated tool that scans specified subreddits on Reddit to find potential leads for your business or services. It uses AI to analyze posts and comments, identifying opportunities that match your service description.

## Features

1. **Central Controller**: Orchestrates the entire lead finding process
2. **AI-Powered Analysis**: Uses Google's Gemini AI to identify leads from Reddit content
3. **Database Storage**: Stores lead IDs and scanned subreddits to avoid duplicates
4. **Scheduled Scanning**: Automatically scans subreddits every 6 hours
5. **Duplicate Prevention**: Checks database before adding new leads
6. **Frontend-Friendly**: Designed with frontend integration in mind
7. **Async PRAW Integration**: Uses Async PRAW for efficient Reddit data extraction

## Project Structure

```
leadly/
├── controller.py          # Central controller orchestrating all functions
├── reddit_data_extractor.py  # Extracts data from Reddit using Async PRAW
├── leadFinderAi.py        # AI-powered lead identification
├── url_mapper.py          # Maps AI output to URL-description pairs
├── db.py                  # Database operations
├── models.py              # Database models
├── scheduler.py           # Scheduled scanning (every 6 hours)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   GOOGLE_API_KEY=your_google_api_key
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=your_user_agent
   ```

3. **Initialize Database**:
   ```bash
   python db.py
   ```

## Usage

### Manual Run
```bash
python test_controller.py
```

### Scheduled Run (every 6 hours)
```bash
python scheduler.py
```

### Retrieve Leads
```bash
python get_leads.py
```

## How It Works

1. **Data Extraction**: The `reddit_data_extractor.py` module fetches posts and comments from specified subreddits using Async PRAW
2. **AI Analysis**: The `leadFinderAi.py` module uses Google's Gemini AI to analyze content and identify leads
3. **Processing**: The `url_mapper.py` module processes AI output into a usable format
4. **Storage**: The `db.py` module stores leads and scanned subreddits in the database
5. **Scheduling**: The `scheduler.py` module runs the process every 6 hours

## Frontend Integration

The system is designed to be frontend-friendly:
- All lead data is stored in a structured database
- URL-description mapping makes it easy to display leads
- Duplicate checking ensures clean data for frontend display
- Scheduled runs keep data fresh

## Customization

You can customize the subreddits to scan by modifying the list in `reddit_data_extractor.py` or by adding entries to the `subreddits_to_scan` table in the database.

To change the user query (your service description), modify the `USER_QUERY` variable in `scheduler.py`.

## Implementation Status

✅ **Task 1**: Created a central controller for all functions (`controller.py`)

✅ **Task 2**: Created a new file with function to process AI output and create URL-description mapping (`url_mapper.py`)

✅ **Task 3**: Implemented database storage for lead IDs and scanned subreddits (`db.py`, `models.py`)

✅ **Task 4**: Set up cron job to scan subreddits every 6 hours with duplicate checking (`scheduler.py`)

✅ **Task 5**: Ensured all implementations are frontend-friendly with structured data storage and retrieval

✅ **Task 6**: Replaced PRAW with Async PRAW for better performance and async compatibility

## Testing

The system has been tested and verified to work correctly:
- Data extraction from Reddit works properly with Async PRAW
- AI analysis correctly identifies leads
- URL mapping converts AI output to usable format
- Database storage saves leads without duplicates
- Lead retrieval works as expected