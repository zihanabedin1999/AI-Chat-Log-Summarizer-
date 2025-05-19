import re
import logging
from collections import Counter
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')

def analyze_chat_log(file_path):
    """
    Analyze a chat log file and return statistics and keyword analysis.
    
    Args:
        file_path (str): Path to the chat log file
        
    Returns:
        dict: Dictionary containing analysis results
    """
    try:
        # Read the chat log file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Parse the chat log
        user_messages, ai_messages, all_messages = parse_chat_log(content)
        
        # Calculate message statistics
        total_messages = len(user_messages) + len(ai_messages)
        
        # Extract keywords using TF-IDF
        keywords = extract_keywords_tfidf(user_messages, ai_messages)
        
        # Generate conversation nature based on keywords
        conversation_nature = generate_conversation_nature(keywords)
        
        # Return the analysis results
        return {
            'total_messages': total_messages,
            'user_message_count': len(user_messages),
            'ai_message_count': len(ai_messages),
            'keywords': keywords,
            'conversation_nature': conversation_nature,
            'exchanges': min(len(user_messages), len(ai_messages))
        }
    
    except Exception as e:
        logger.error(f"Error analyzing chat log: {str(e)}")
        raise

def parse_chat_log(content):
    """
    Parse a chat log and separate messages by speaker.
    
    Args:
        content (str): Chat log content
        
    Returns:
        tuple: (user_messages, ai_messages, all_messages)
    """
    # Split the content into lines
    lines = content.strip().split('\n')
    
    user_pattern = re.compile(r'^User:\s*(.*?)$', re.IGNORECASE)
    ai_pattern = re.compile(r'^AI:\s*(.*?)$', re.IGNORECASE)
    
    user_messages = []
    ai_messages = []
    all_messages = []
    
    current_speaker = None
    current_message = []
    
    for line in lines:
        line = line.strip()
        
        # Check if this is a new message from the user
        user_match = user_pattern.match(line)
        if user_match:
            # Save the previous message if there was one
            if current_message and current_speaker:
                message_text = ' '.join(current_message).strip()
                all_messages.append((current_speaker, message_text))
                if current_speaker.lower() == 'user':
                    user_messages.append(message_text)
                else:
                    ai_messages.append(message_text)
            
            # Start a new user message
            current_speaker = 'User'
            current_message = [user_match.group(1)]
            continue
        
        # Check if this is a new message from the AI
        ai_match = ai_pattern.match(line)
        if ai_match:
            # Save the previous message if there was one
            if current_message and current_speaker:
                message_text = ' '.join(current_message).strip()
                all_messages.append((current_speaker, message_text))
                if current_speaker.lower() == 'user':
                    user_messages.append(message_text)
                else:
                    ai_messages.append(message_text)
            
            # Start a new AI message
            current_speaker = 'AI'
            current_message = [ai_match.group(1)]
            continue
        
        # If it's not a new speaker, append to the current message
        if current_speaker:
            current_message.append(line)
    
    # Add the last message
    if current_message and current_speaker:
        message_text = ' '.join(current_message).strip()
        all_messages.append((current_speaker, message_text))
        if current_speaker.lower() == 'user':
            user_messages.append(message_text)
        else:
            ai_messages.append(message_text)
    
    return user_messages, ai_messages, all_messages

def extract_keywords_simple(user_messages, ai_messages):
    """
    Extract top keywords using a simple frequency-based approach.
    
    Args:
        user_messages (list): List of user messages
        ai_messages (list): List of AI messages
        
    Returns:
        list: Top 5 keywords
    """
    # Combine all messages
    all_text = ' '.join(user_messages + ai_messages).lower()
    
    # Tokenize words
    words = re.findall(r'\b\w+\b', all_text)
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    stop_words.update(['sure', 'can', 'would', 'also', 'well', 'many', 'much', 'one', 'two', 'three'])
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_counts = Counter(filtered_words)
    
    # Return top 5 keywords
    return [word for word, count in word_counts.most_common(5)]

def extract_keywords_tfidf(user_messages, ai_messages):
    """
    Extract top keywords using TF-IDF.
    
    Args:
        user_messages (list): List of user messages
        ai_messages (list): List of AI messages
        
    Returns:
        list: Top 5 keywords
    """
    # Combine all messages
    all_messages = user_messages + ai_messages
    
    if not all_messages:
        return []
    
    # Create a TF-IDF vectorizer
    stop_words = set(stopwords.words('english'))
    stop_words.update(['sure', 'can', 'would', 'also', 'well', 'many', 'much', 'one', 'two', 'three'])
    
    tfidf_vectorizer = TfidfVectorizer(
        stop_words=list(stop_words),
        min_df=1,
        max_df=0.9,
        ngram_range=(1, 1),
        token_pattern=r'\b\w+\b'
    )
    
    # Fit and transform the messages
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_messages)
    
    # Get feature names
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    # Sum TF-IDF scores for each word across all documents
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    
    # Create a list of (word, score) tuples
    word_scores = [(feature_names[i], tfidf_sums[i]) for i in range(len(feature_names))]
    
    # Sort by score and get top 5 keywords
    top_keywords = sorted(word_scores, key=lambda x: x[1], reverse=True)[:5]
    
    return [word for word, score in top_keywords]

def generate_conversation_nature(keywords):
    """
    Generate a description of the conversation nature based on keywords.
    
    Args:
        keywords (list): List of top keywords
        
    Returns:
        str: Description of the conversation nature
    """
    if not keywords:
        return "No clear topic could be determined."
    
    # Join keywords into a sentence
    return f"The conversation primarily focused on {', '.join(keywords[:-1])} and {keywords[-1]}." if len(keywords) > 1 else f"The conversation primarily focused on {keywords[0]}."
