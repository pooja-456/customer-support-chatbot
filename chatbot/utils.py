import re

def sanitize_input(user_input):
    """Clean and validate user input"""
    if not isinstance(user_input, str):
        return ""
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', user_input.strip())
    
    # Basic length check (prevent extremely long inputs)
    if len(cleaned) > 1000:
        return cleaned[:1000]
    
    # Remove potentially harmful characters but keep basic punctuation
    cleaned = re.sub(r'[^\w\s\?\!\.\,\'\"\-\@]', '', cleaned)
    
    return cleaned

def is_valid_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_response(response, user_name=None):
    """Format bot response with optional personalization"""
    if user_name and user_name != 'Guest':
        if not any(name in response for name in [user_name, 'you', 'your']):
            return f"{response} Is there anything else I can help you with, {user_name}?"
    return response