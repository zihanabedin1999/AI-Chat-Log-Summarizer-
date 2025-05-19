# AI Chat Log Summarizer

A Python-based tool that analyzes AI-user chat logs to generate statistical summaries and extract keywords.

## Project Description

AI Chat Log Summarizer is a web application that reads `.txt` chat logs between a user and an AI, parses the conversation, and produces a simple summary including message counts and frequently used keywords. The application showcases basic NLP (Natural Language Processing) capabilities using Python, with TF-IDF-based keyword extraction.

## Features

### 1. Chat Log Parsing
- Separates messages by speaker (User: and AI:)
- Stores messages in appropriate structures for further analysis

### 2. Message Statistics
- Counts total messages
- Counts messages from User vs. AI

### 3. Keyword Analysis
- Extracts the top 5 most frequently used words
- Excludes common stop words (e.g., "the", "is", "and")

### 4. Generated Summary
The application outputs a clear summary that includes:
- Total number of exchanges
- Nature of the conversation (based on keyword topics)
- Most common keywords

Example of the summary:
```
Summary:
- The conversation had 15 exchanges.
- The user asked mainly about Python and its uses.
- Most common keywords: Python, use, data, AI, language.
```

## Technologies Used

- **Backend**: Python, Flask
- **Database**: PostgreSQL
- **NLP Libraries**: NLTK, scikit-learn
- **Frontend**: HTML, CSS, Bootstrap

## How to Run

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/ai-chat-log-summarizer.git
cd ai-chat-log-summarizer
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Set up environment variables:
```
export DATABASE_URL=your_postgresql_database_url
export SESSION_SECRET=your_secret_key
```

4. Run the application:
```
python main.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Upload a `.txt` file containing a chat between a user and an AI, formatted like:
```
User: Hi, can you tell me about Python?
AI: Sure! Python is a popular programming language known for its readability.
User: What can I use it for?
AI: You can use Python for web development, data analysis, AI, and more.
```

2. Click "Analyze Chat Log" to process the file

3. View the generated summary and statistics

4. Alternatively, click on "Try Sample" to see an analysis of a pre-loaded example chat

## Project Structure

- `app.py`: Main Flask application
- `main.py`: Entry point for the application
- `chat_analyzer.py`: Core functionality for analyzing chat logs
- `models.py`: Database models
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files

## Screenshots

1. Home Page
![Home Page](screenshots/home.png)

2. Analysis Results
![Analysis Results](screenshots/results.png)

3. How It Works
![How It Works](screenshots/how_it_works.png)

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

[Your Name]