# Leadly - Reddit Lead Finder

Leadly is an automated tool that scans specified subreddits on Reddit to find potential leads for your business or services. It uses AI to analyze posts and comments, identifying opportunities that match your service description.

## Features

1. **Central Controller**: Orchestrates the entire lead finding process
2. **AI-Powered Analysis**: Uses Google's Gemini AI to identify leads from Reddit content
3. **Database Storage**: Stores lead IDs and scanned subreddits to avoid duplicates
4. **Scheduled Scanning**: Automatically scans subreddits every 5 minutes
5. **Duplicate Prevention**: Checks database before adding new leads
6. **Frontend-Friendly**: Designed with frontend integration in mind
7. **Async PRAW Integration**: Uses Async PRAW for efficient Reddit data extraction
8. **Cold Lead Identification**: AI now identifies indirect expressions of need
9. **Timer Display**: Shows when the next automatic scan will occur
10. **Subreddit Tracking**: Properly records and displays subreddit names for leads
11. **Lead Categorization**: Classifies leads as Hot, Cold, or Neutral

## Project Structure

```
leadly/
├── controller.py          # Central controller orchestrating all functions
├── reddit_data_extractor.py  # Extracts data from Reddit using Async PRAW
├── leadFinderAi.py        # AI-powered lead identification
├── url_mapper.py          # Maps AI output to URL-description pairs
├── db.py                  # Database operations
├── models.py              # Database models
├── scheduler.py           # Scheduled scanning (every 5 minutes)
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
   ```env
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

### Scheduled Run (every 5 minutes)
```bash
python scheduler.py
```

### Retrieve Leads
```bash
python get_leads.py
```

### Clear Database
```bash
python clear_database.py
```

### Update Database Schema
```bash
python update_schema.py
```

## How It Works

1. **Data Extraction**: The `reddit_data_extractor.py` module fetches posts and comments from specified subreddits using Async PRAW
2. **AI Analysis**: The `leadFinderAi.py` module uses Google's Gemini AI to analyze content and identify leads
3. **Processing**: The `url_mapper.py` module processes AI output into a usable format
4. **Storage**: The `db.py` module stores leads and scanned subreddits in the database
5. **Scheduling**: The `scheduler.py` module runs the process every 5 minutes

## Frontend Integration

The system is designed to be frontend-friendly:
- All lead data is stored in a structured database
- URL-description mapping makes it easy to display leads
- Duplicate checking ensures clean data for frontend display
- Scheduled runs keep data fresh
- Timer API endpoint shows next scan time
- Subreddit information is properly tracked and displayed
- Lead categorization allows for prioritized outreach

## Customization

You can customize the subreddits to scan by modifying the list in `reddit_data_extractor.py` or by adding entries to the `subreddits_to_scan` table in the database.

To change the user query (your service description), modify the `USER_QUERY` variable in `scheduler.py`.

## AI Lead Identification Improvements

The AI system has been enhanced to identify both direct and indirect leads:

1. **Direct Leads**: Explicit requests for services (e.g., "Looking for a video editor")
2. **Cold Leads**: Implicit expressions of need (e.g., "I spend 5 hours a week on inventory tracking")
3. **Pain Points**: Complaints about current processes (e.g., "Our inventory system is a mess")
4. **Desire for Improvement**: Expressions of wanting better solutions (e.g., "There has to be a better way")

## Lead Categorization

Leads are now categorized into three types:

1. **Hot Leads**: Explicit requests for services, clear buying intent
2. **Cold Leads**: Implicit needs, pain points, expressions of desire for improvement
3. **Neutral Leads**: General discussions that might be relevant but less actionable

## Implementation Status

✅ **Task 1**: Created a central controller for all functions (`controller.py`)

✅ **Task 2**: Created a new file with function to process AI output and create URL-description mapping (`url_mapper.py`)

✅ **Task 3**: Implemented database storage for lead IDs and scanned subreddits (`db.py`, `models.py`)

✅ **Task 4**: Set up cron job to scan subreddits every 5 minutes with duplicate checking (`scheduler.py`)

✅ **Task 5**: Ensured all implementations are frontend-friendly with structured data storage and retrieval

✅ **Task 6**: Replaced PRAW with Async PRAW for better performance and async compatibility

✅ **Task 7**: Enhanced AI to identify cold/indirect leads

✅ **Task 8**: Added timer display functionality

✅ **Task 9**: Fixed subreddit name recording and display

✅ **Task 10**: Implemented lead categorization (hot, cold, neutral)

✅ **Task 11**: Fixed comment URL generation to include proper subreddit and post information

## Testing

The system has been tested and verified to work correctly:
- Data extraction from Reddit works properly with Async PRAW
- AI analysis correctly identifies both direct and cold leads
- URL mapping converts AI output to usable format
- Database storage saves leads without duplicates
- Lead retrieval works as expected
- Scheduled scans run every 5 minutes
- Timer display shows next execution time
- Subreddit names are properly recorded and displayed
- Comment URLs are properly formatted with subreddit and post information
- Lead categorization works correctly (hot, cold, neutral)

## Troubleshooting

### AI API Overload (503 Error)
If you see "503 UNAVAILABLE" errors, the AI model is temporarily overloaded. This is normal and the system will continue to function, but may not find leads until the API is available again.

### Database Schema Issues
If you've updated the code but are seeing database errors, run `python update_schema.py` to update your database schema to match the latest model changes.

### Clearing Data
To start fresh, run `python clear_database.py` to remove all leads and reset the database.