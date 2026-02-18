# chatbot/ui.py - Fixed Help and Statistics Button Functions

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
from .core import CustomerSupportBot

class ChatbotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.bot = CustomerSupportBot()
        self.setup_ui()
        self.add_bot_message("👋 Welcome to Customer Support! I'm here to help you with any questions or issues you may have. How can I assist you today?")
    
    def setup_ui(self):
        # Main window configuration
        self.root.title("Customer Support Chatbot")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.configure(bg='#f0f0f0')
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🤖 Customer Support Chat", 
            font=('Segoe UI', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 10))
        
        # Chat display area
        chat_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=('Segoe UI', 10),
            bg='white',
            fg='black',
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input section
        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input field
        self.user_input = tk.Entry(
            input_frame,
            font=('Segoe UI', 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind('<Return>', self.send_message_event)
        self.user_input.focus()
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=('Segoe UI', 10),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            padx=20,
            cursor='hand2'
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Button section
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        # Help button - FIXED
        self.help_button = tk.Button(
            button_frame,
            text="Help",
            command=self.show_help,  # Fixed: was missing command
            font=('Segoe UI', 9),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            padx=15,
            cursor='hand2'
        )
        self.help_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Statistics button - FIXED
        self.stats_button = tk.Button(
            button_frame,
            text="Statistics",
            command=self.show_statistics,  # Fixed: was missing command
            font=('Segoe UI', 9),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            padx=15,
            cursor='hand2'
        )
        self.stats_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear Chat button
        self.clear_button = tk.Button(
            button_frame,
            text="Clear Chat",
            command=self.clear_chat,
            font=('Segoe UI', 9),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            padx=15,
            cursor='hand2'
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Exit button
        self.exit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.exit_application,
            font=('Segoe UI', 9),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            padx=15,
            cursor='hand2'
        )
        self.exit_button.pack(side=tk.RIGHT)
    
    def add_message(self, sender, message, sender_emoji=""):
        """Add a message to the chat display with different colors"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Configure text tags for different colors
        self.chat_display.tag_configure("user_msg", foreground="#0066cc", font=('Segoe UI', 10, 'normal'))
        self.chat_display.tag_configure("bot_msg", foreground="#006600", font=('Segoe UI', 10, 'normal'))
        self.chat_display.tag_configure("timestamp", foreground="#666666", font=('Segoe UI', 9))
        
        # Add timestamp
        timestamp = datetime.now().strftime("[%H:%M] ")
        
        if sender == "user":
            # Insert timestamp in gray
            self.chat_display.insert(tk.END, timestamp, "timestamp")
            # Insert user message in blue
            self.chat_display.insert(tk.END, f"👤 You: {message}\n", "user_msg")
        else:
            # Insert timestamp in gray
            self.chat_display.insert(tk.END, timestamp, "timestamp")
            # Insert bot message in green
            self.chat_display.insert(tk.END, f"🤖 Bot: {message}\n", "bot_msg")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_bot_message(self, message):
        """Add a bot message to the chat"""
        self.add_message("bot", message)
    
    def add_user_message(self, message):
        """Add a user message to the chat"""
        self.add_message("user", message)
    
    def send_message_event(self, event):
        """Handle Enter key press"""
        self.send_message()
        return 'break'
    
    def send_message(self):
        """Send user message and get bot response"""
        user_text = self.user_input.get().strip()
        
        if not user_text:
            return
        
        # Add user message to chat
        self.add_user_message(user_text)
        
        # Clear input field
        self.user_input.delete(0, tk.END)
        
        # Disable send button temporarily
        self.send_button.config(state=tk.DISABLED)
        
        # Get bot response in separate thread to prevent UI blocking
        def get_response():
            try:
                bot_response = self.bot.get_response(user_text)
                
                # Schedule UI update in main thread
                self.root.after(0, lambda: self.display_bot_response(bot_response))
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                self.root.after(0, lambda: self.display_bot_response(error_msg))
        
        # Start response thread
        threading.Thread(target=get_response, daemon=True).start()
    
    def display_bot_response(self, response):
        """Display bot response and re-enable send button"""
        self.add_bot_message(response)
        self.send_button.config(state=tk.NORMAL)
        self.user_input.focus()
    
    def show_help(self):
        """Show help dialog - FIXED FUNCTION"""
        help_text = """🔧 Customer Support Help

Available Commands:
• Type your question naturally
• Ask about account issues, passwords, billing
• Get product information and pricing
• Report technical problems
• Request subscription changes

Example Questions:
• "I forgot my password"
• "How do I cancel my subscription?"
• "The app is crashing"
• "What are your pricing plans?"
• "My payment was declined"

Quick Actions:
• Help - Show this help
• Statistics - View chat statistics
• Clear Chat - Start fresh conversation
• Exit - Close the application

Just type your question and I'll help you! 🤖"""
        
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Customer Support")
        help_window.geometry("500x600")
        help_window.configure(bg='white')
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the help window
        help_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Help text display
        help_display = scrolledtext.ScrolledText(
            help_window,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            bg='white',
            fg='black',
            padx=15,
            pady=15
        )
        help_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_display.insert(tk.END, help_text)
        help_display.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(
            help_window,
            text="Close",
            command=help_window.destroy,
            font=('Segoe UI', 10),
            bg='white',
            fg='black',
            relief=tk.SOLID,
            bd=1,
            padx=20
        )
        close_button.pack(pady=10)
    
    def show_statistics(self):
        """Show conversation statistics - FIXED FUNCTION"""
        stats = self.bot.get_conversation_stats()
        
        stats_text = f"""📊 Chat Statistics

Total Messages: {stats['total_messages']}
Your Messages: {stats['user_messages']}
Bot Responses: {stats['bot_messages']}

Available Topics:
{chr(10).join(f"• {topic.replace('_', ' ').title()}" for topic in self.bot.get_help_topics())}

Session Info:
• Chat started: {datetime.now().strftime('%Y-%m-%d %H:%M')}
• Bot Status: Online ✅
• Response Time: < 1 second

Thank you for using Customer Support! 🤖"""
        
        # Show statistics in message box
        messagebox.showinfo("Chat Statistics", stats_text)
    
    def clear_chat(self):
        """Clear the chat display"""
        result = messagebox.askyesno(
            "Clear Chat", 
            "Are you sure you want to clear the chat history?"
        )
        
        if result:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # Clear bot's conversation history
            self.bot.clear_history()
            
            # Add welcome message back
            self.add_bot_message("👋 Welcome to Customer Support! I'm here to help you with any questions or issues you may have. How can I assist you today?")
    
    def exit_application(self):
        """Exit the application"""
        result = messagebox.askyesno(
            "Exit Application", 
            "Are you sure you want to exit the Customer Support Chat?"
        )
        
        if result:
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        self.root.mainloop()


if __name__ == "__main__":
    app = ChatbotGUI()
    app.run()