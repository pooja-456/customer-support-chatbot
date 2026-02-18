# chatbot/core.py - Fixed to work with simplified data.py

import re
import difflib
from .data import responses, keyword_variations, category_responses

class CustomerSupportBot:
    def __init__(self):
        self.responses = responses
        self.keyword_variations = keyword_variations
        self.category_responses = category_responses
        self.conversation_history = []
    
    def preprocess_input(self, user_input):
        """Clean and normalize user input"""
        # Convert to lowercase and remove extra spaces
        cleaned = user_input.lower().strip()
        # Remove punctuation except apostrophes
        cleaned = re.sub(r'[^\w\s\']', ' ', cleaned)
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def find_keyword_matches(self, user_input):
        """Find matching keywords using variations"""
        matches = []
        words = user_input.split()
        
        for word in words:
            for key, variations in self.keyword_variations.items():
                for variation in variations:
                    if variation in user_input or word == variation:
                        matches.append(key)
                        break
        
        return list(set(matches))  # Remove duplicates
    
    def calculate_pattern_score(self, user_input, pattern):
        """Calculate how well user input matches a pattern"""
        user_words = set(user_input.split())
        pattern_words = set(pattern.split())
        
        # Direct word matches
        direct_matches = len(user_words.intersection(pattern_words))
        
        # Check for partial matches and similarities
        similarity_score = 0
        for user_word in user_words:
            for pattern_word in pattern_words:
                # Check if words are similar (for typos)
                similarity = difflib.SequenceMatcher(None, user_word, pattern_word).ratio()
                if similarity > 0.8:  # 80% similarity threshold
                    similarity_score += similarity
                # Check if one word contains another
                elif user_word in pattern_word or pattern_word in user_word:
                    similarity_score += 0.7
        
        # Calculate final score
        total_score = direct_matches * 2 + similarity_score
        
        # Normalize by pattern length to favor more specific matches
        if len(pattern_words) > 0:
            total_score = total_score / len(pattern_words)
        
        return total_score
    
    def find_best_response(self, user_input):
        """Find the best matching response using scoring"""
        best_score = 0
        best_response = None
        best_pattern = None
        
        # Try exact pattern matching first
        for pattern, response in self.responses.items():
            score = self.calculate_pattern_score(user_input, pattern)
            
            if score > best_score:
                best_score = score
                best_response = response
                best_pattern = pattern
        
        # If we found a good match (score > 0.5), return it
        if best_score > 0.5:
            return best_response
        
        # Otherwise, try keyword-based category fallback
        keywords = self.find_keyword_matches(user_input)
        
        if keywords:
            # Determine category based on keywords
            if any(kw in ['password', 'login', 'account', 'locked'] for kw in keywords):
                return self.category_responses['account']
            elif any(kw in ['app', 'crash', 'slow', 'sync'] for kw in keywords):
                return self.category_responses['technical']
            elif any(kw in ['payment', 'billing', 'refund', 'subscription'] for kw in keywords):
                return self.category_responses['billing']
        
        # Final fallback
        return self.category_responses['general']
    
    def get_response(self, user_input):
        """Main method to get bot response"""
        if not user_input or not user_input.strip():
            return "I'm here to help! What can I assist you with today?"
        
        # Preprocess the input
        processed_input = self.preprocess_input(user_input)
        
        # Store in conversation history
        self.conversation_history.append(('user', user_input))
        
        # Find and return the best response
        response = self.find_best_response(processed_input)
        
        # Store bot response in history
        self.conversation_history.append(('bot', response))
        
        return response
    
    def get_conversation_stats(self):
        """Get conversation statistics"""
        total_messages = len(self.conversation_history)
        user_messages = len([msg for msg in self.conversation_history if msg[0] == 'user'])
        bot_messages = len([msg for msg in self.conversation_history if msg[0] == 'bot'])
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'bot_messages': bot_messages
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_help_topics(self):
        """Get available help topics"""
        topics = list(self.responses.keys())
        # Filter out greeting and exit patterns for cleaner help display
        filtered_topics = [topic for topic in topics if topic not in ['hello', 'hi', 'hey', 'quit', 'bye', 'exit', 'goodbye']]
        return filtered_topics[:10]  # Return top 10 topics