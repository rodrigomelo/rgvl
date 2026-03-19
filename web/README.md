# RGVL Web

Dashboard to visualize data from the RGVL Data API.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

Open http://localhost:5004

## Requirements

- Python 3.8+
- Flask
- Requests
- RGVL Data API running on localhost:5003

## Project Structure

```
rgvl-web/
├── server.py       # Flask backend
├── index.html      # Frontend dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

## API Endpoints

The dashboard consumes the following RGVL Data API endpoints:

- `/api/stats` - User statistics
- `/api/profiles` - Profile information
- `/api/repositories` - GitHub repositories
- `/api/activities` - GitHub activity timeline
- `/api/contacts` - Contact list
- `/api/notes` - Notes
- `/api/documents` - Documents

## Features

- 📊 Stats overview (repos, gists, followers, following)
- 👤 Profile summary
- 📚 GitHub repositories with stars, language, forks
- 📊 Activity timeline
- 👥 Contacts
- 📝 Notes
- 📄 Documents
- 🌙 Dark theme UI
- 🔄 Real-time API status
