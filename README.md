# Customer Support Chatbot

## Overview
This project is a desktop-based Customer Support Chatbot built using Python and Tkinter.  
It uses pattern matching and keyword-based logic to generate responses and simulate customer support conversations.

## Features
- Desktop GUI built with Tkinter
- Pattern-based response matching
- Fuzzy word similarity handling (typo tolerance)
- Keyword-based category fallback (Account, Billing, Technical, General)
- Conversation history tracking
- Chat statistics display
- Multi-threaded response handling for smooth UI experience
- Help and Clear Chat functionality

## Project Structure
Chatbot_Task4/
│
├── main.py              # Application entry point
├── chatbot/
│   ├── core.py          # Response matching and chatbot logic
│   ├── data.py          # Response patterns and categories
│   ├── ui.py            # Graphical user interface
│   ├── utils.py         # Helper utilities
│   └── __init__.py

## How It Works
1. User enters a message in the GUI.
2. Input is preprocessed (lowercased, cleaned).
3. Pattern similarity scoring is applied.
4. Best matching response is selected.
5. If no strong match is found, keyword-based fallback logic is used.
6. Conversation is stored for statistics tracking.

## Matching Logic
- Direct word matching
- Similarity scoring using difflib (80% threshold)
- Keyword variation detection
- Category-based fallback responses

## Technologies Used
- Python
- Tkinter
- Regular Expressions (re)
- difflib (SequenceMatcher)
- Threading

## Future Improvements
- Replace rule-based matching with ML-based intent classification
- Add database logging
- Convert to web-based deployment
