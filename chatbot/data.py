# chatbot/data.py - Enhanced with More Technical Patterns

# Core response patterns - focused on essential customer support
responses = {
    # Greeting patterns
    'hello': "Welcome! I'm here to provide quick and helpful support. Whether you need help with your account, have questions about our products, or need technical assistance - just ask!",
    'hi': "Hello! I'm your customer support assistant. How can I help you today?",
    'hey': "Hi there! What can I assist you with today?",
    'good morning': "Good morning! How can I help you today?",
    'good afternoon': "Good afternoon! What can I assist you with?",
    
    # Password and login issues
    'forgot password': """To reset your password:
✅ Visit the login page and click 'Forgot Password'
✅ Enter the email associated with your account
✅ You'll receive a reset link within 5 minutes
✅ Create a new strong password
Need the direct link? I can provide that too!""",
    
    'reset password': """Password Reset Help:
• Go to: [Login Page] → 'Forgot Password'
• Enter your registered email
• Check email (including spam folder)
• Click the reset link
• Choose a strong new password
The reset link expires in 24 hours!""",
    
    'login issue': """Password Reset Help:
• Go to: [Login Page] → 'Forgot Password'
• Enter your registered email
• Check email (including spam folder)
• Click the reset link
• Choose a strong new password
The reset link expires in 24 hours!""",
    
    'cant login': """Login Troubleshooting:
🔧 Try these steps:
• Clear browser cache and cookies
• Try incognito/private browsing mode
• Check caps lock is off
• Reset your password if needed
• Try a different browser
Still having issues? Let me know!""",
    
    # Account management
    'account locked': """🔒 Account Unlock Help:
• Wait 15 minutes - auto unlock after failed attempts
• Use 'Forgot Password' to reset credentials
• Clear browser data and try again
• Check if account needs email verification
Need immediate access? I can escalate this!""",
    
    'change password': """To change your password:
✅ Log into your account
✅ Go to Settings → Security
✅ Click 'Change Password'
✅ Enter current password, then new password
✅ Save changes
Your new password should be strong and unique!""",
    
    'logout all devices': """🔐 Security Logout:
• Go to Settings → Security → Active Sessions
• Click 'End All Other Sessions'
• Your current device stays logged in
• All other devices will be logged out immediately
This helps secure your account!""",
    
    # Product information
    'products': """Our Product Lineup:
• Cloud-based software solutions
• Mobile and desktop applications
• 99.9% uptime guarantee
• Scalable for any business size
Want to know more about a specific plan or feature?""",
    
    'features': """Key Features:
✨ Cloud Storage & Sync
✨ Multi-platform access (Web, Mobile, Desktop)
✨ Real-time collaboration
✨ Advanced security encryption
✨ 24/7 automated backups
✨ API integrations
Which feature interests you most?""",
    
    # Pricing information
    'pricing': """💰 Pricing Plans:
🥉 Basic Plan: $9.99/month
• Up to 5 users
• 10GB storage
• Email support

🥈 Professional: $19.99/month
• Up to 25 users
• 100GB storage
• Priority support
• Advanced features

🥇 Enterprise: $49.99/month
• Unlimited users
• 1TB storage
• 24/7 phone support
• Custom integrations

💡 All plans include 14-day free trial!""",
    
    'cost': """💰 Pricing Plans:
🥉 Basic Plan: $9.99/month
• Up to 5 users
• 10GB storage
• Email support

🥈 Professional: $19.99/month
• Up to 25 users
• 100GB storage
• Priority support
• Advanced features

🥇 Enterprise: $49.99/month
• Unlimited users
• 1TB storage
• 24/7 phone support
• Custom integrations

💡 All plans include 14-day free trial!""",
    
    'plans': """💰 Pricing Plans:
🥉 Basic Plan: $9.99/month
• Up to 5 users
• 10GB storage
• Email support

🥈 Professional: $19.99/month
• Up to 25 users
• 100GB storage
• Priority support
• Advanced features

🥇 Enterprise: $49.99/month
• Unlimited users
• 1TB storage
• 24/7 phone support
• Custom integrations

💡 All plans include 14-day free trial!""",
    
    # Subscription management
    'cancel subscription': """📋 Subscription Cancellation:
• Log into your account
• Go to Settings → Billing → Manage Subscription
• Click 'Cancel Subscription'
• Confirm cancellation
• Access continues until billing period ends
Need help with the process? I can guide you!""",
    
    'upgrade plan': """📈 Plan Upgrade:
• Go to Settings → Billing → Current Plan
• Click 'Upgrade Plan'
• Choose your new plan level
• Payment will be prorated automatically
• Upgrade takes effect immediately
Which plan are you interested in upgrading to?""",
    
    'downgrade plan': """📉 Plan Downgrade:
• Go to Settings → Billing → Current Plan
• Click 'Change Plan'
• Select lower tier plan
• Changes take effect at next billing cycle
• You keep current features until then
Need help choosing the right plan?""",
    
    # Payment and billing
    'payment declined': """💳 Payment Troubleshooting:
🔧 Try these solutions:
• Check card expiration date
• Verify billing address matches card
• Ensure sufficient funds available
• Try a different payment method
• Contact your bank about international charges
• Update payment info in Settings → Billing
Still having issues? I can help!""",
    
    'billing issue': """💳 Billing Support:
I can help with:
• Payment method updates
• Invoice questions
• Refund requests
• Billing address changes
• Payment history
What specific billing issue are you experiencing?""",
    
    'refund': """💰 Refund Process:
• Refunds available within 30 days of purchase
• Go to Settings → Billing → Invoice History
• Click 'Request Refund' next to relevant charge
• Refunds processed within 5-7 business days
• Partial refunds available for downgrades
Need help with a specific charge?""",
    
    # Technical support - Enhanced with more patterns
    'app crashing': """🔧 App Crash Troubleshooting:
• Force close and restart the app
• Check for app updates in your app store
• Clear app cache and data
• Restart your device
• Ensure you have the latest OS version
Still crashing? Send crash logs to: tech@company.com""",
    
    'app not working': """🔧 App Troubleshooting:
Try these steps:
1. Force close and reopen the app
2. Check your internet connection
3. Update to latest app version
4. Restart your device
5. Clear app cache/data
6. Reinstall if necessary
Which device are you using?""",
    
    'link not working': """🔗 Link Troubleshooting:
• Try copying and pasting the link directly into your browser
• Clear browser cache and cookies
• Try opening in incognito/private mode
• Check if link has expired or requires login
• Try a different browser
• Disable browser extensions temporarily
Is this a submission link or access link?""",
    
    'unable to open': """🔗 Access Troubleshooting:
• Check your internet connection
• Try refreshing the page (F5 or Ctrl+R)
• Clear browser cache and cookies
• Try incognito/private browsing mode
• Disable ad blockers temporarily
• Try a different browser
What exactly are you trying to open?""",
    
    'submission problem': """📝 Submission Issues:
• Check if you're logged into the correct account
• Verify the submission deadline hasn't passed
• Try submitting from a different browser
• Clear cache and cookies
• Check file size and format requirements
• Contact your instructor if deadline related
What type of submission are you having trouble with?""",
    
    'sync problem': """🔄 Sync Issues:
• Check internet connection
• Log out and log back in
• Go to Settings → Sync → Force Sync
• Clear app cache
• Ensure you're on the latest version
Data not syncing between which devices?""",
    
    'slow performance': """⚡ Performance Optimization:
• Close unnecessary background apps
• Check available storage space
• Update to latest app version
• Restart your device
• Clear browser cache (web version)
• Check internet connection speed
Which platform are you experiencing slowness on?""",
    
    # General help
    'help': """🔧 Available Topics:
Product Information
Technical Support
Pricing & Plans
Account Help

FAQ Topics:
Free Trial • Warranty • Refunds

Commands: help, quit""",
    
    'support': """I'm here to help! I can assist with:
✅ Account and login issues
✅ Product and pricing information
✅ Technical troubleshooting
✅ Billing and subscription questions
✅ Order and shipping inquiries
What would you like help with specifically?""",
    
    # Exit patterns
    'quit': "Thank you for using our support chat! Have a great day! 👋",
    'bye': "Goodbye! Feel free to return if you need more help! 👋",
    'exit': "Thanks for chatting! Have a wonderful day! 👋",
    'goodbye': "Take care! I'm here whenever you need support! 👋"
}

# Enhanced keyword variations for flexible matching
keyword_variations = {
    'password': ['password', 'passwd', 'pass', 'login', 'signin', 'sign in'],
    'forgot': ['forgot', 'forgotten', 'lost', 'dont remember', "don't remember", 'cant remember', "can't remember"],
    'reset': ['reset', 'change', 'update', 'modify'],
    'account': ['account', 'profile', 'user'],
    'locked': ['locked', 'blocked', 'suspended', 'disabled'],
    'login': ['login', 'log in', 'signin', 'sign in', 'access'],
    'cancel': ['cancel', 'stop', 'end', 'terminate', 'quit'],
    'subscription': ['subscription', 'plan', 'service', 'membership'],
    'upgrade': ['upgrade', 'increase', 'enhance', 'improve'],
    'downgrade': ['downgrade', 'reduce', 'lower', 'decrease'],
    'payment': ['payment', 'billing', 'charge', 'transaction'],
    'declined': ['declined', 'rejected', 'failed', 'error'],
    'refund': ['refund', 'money back', 'return'],
    'app': ['app', 'application', 'software', 'program'],
    'crash': ['crash', 'crashing', 'freeze', 'freezing', 'stopped'],
    'slow': ['slow', 'sluggish', 'laggy', 'performance'],
    'sync': ['sync', 'synchronize', 'syncing'],
    'products': ['products', 'services', 'features', 'offerings'],
    'pricing': ['pricing', 'price', 'cost', 'plans', 'fees'],
    'help': ['help', 'support', 'assist', 'assistance'],
    'link': ['link', 'url', 'address', 'connection'],
    'open': ['open', 'access', 'load', 'view'],
    'unable': ['unable', 'cant', "can't", 'cannot', 'wont', "won't"],
    'submission': ['submission', 'submit', 'assignment', 'upload', 'file']
}

# Category-based fallback responses
category_responses = {
    'account': """Account Help Available:
🔧 Profile Updates: Change name, email, phone
🔐 Security: Password, 2FA, login history
💳 Billing: Payment methods, invoices, subscriptions
🔔 Preferences: Notifications, privacy, language

To modify your account:
Settings → Account → [Choose category]
What specifically would you like to change?""",
    
    'technical': """🔧 Technical Support:
I can help troubleshoot:
• App crashes and freezing
• Sync and connectivity issues
• Performance problems
• Installation issues
• Error messages
• Link and access problems

What technical issue are you experiencing?""",
    
    'billing': """💳 Billing & Payments:
I can assist with:
• Payment method updates
• Subscription changes
• Refund requests
• Invoice questions
• Billing history

What billing matter can I help with?""",
    
    'general': """I understand you have a question! I can help with:
✅ Account and login issues
✅ Product and pricing information  
✅ Technical troubleshooting
✅ Billing and subscription questions
✅ Order and shipping inquiries

Could you be more specific about what you need help with?"""
}