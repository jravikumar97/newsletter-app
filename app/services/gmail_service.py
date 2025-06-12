import os
import json
import base64
import email
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

from app.core.config import settings

class GmailService:
    """Enhanced Gmail service for newsletter processing"""
    
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/userinfo.email'
        ]
        self.service = None
        self.credentials = None
    
    def create_oauth_flow(self, redirect_uri: str = None) -> Flow:
        """Create OAuth2 flow for Gmail authentication"""
        if not redirect_uri:
            redirect_uri = f"{settings.BASE_URL}/api/v1/email/oauth/callback"
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = redirect_uri
        return flow
    
    def get_authorization_url(self, redirect_uri: str = None) -> str:
        """Get OAuth authorization URL"""
        flow = self.create_oauth_flow(redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url
    
    def exchange_code_for_tokens(self, code: str, redirect_uri: str = None) -> Dict:
        """Exchange authorization code for access tokens"""
        flow = self.create_oauth_flow(redirect_uri)
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'expires_at': credentials.expiry.isoformat() if credentials.expiry else None,
            'email': self.get_user_email(credentials)
        }
    
    def get_user_email(self, credentials: Credentials) -> str:
        """Get user's email address"""
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info.get('email')
        except Exception:
            return None
    
    def authenticate_with_tokens(self, access_token: str, refresh_token: str = None, expires_at: str = None) -> bool:
        """Authenticate with stored tokens"""
        try:
            # Create credentials from tokens
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET,
                scopes=self.scopes
            )
            
            if expires_at:
                credentials.expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            
            # Refresh if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            self.credentials = credentials
            self.service = build('gmail', 'v1', credentials=credentials)
            return True
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get Gmail user profile"""
        if not self.service:
            return None
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile
        except HttpError as error:
            print(f"Error getting profile: {error}")
            return None
    
    def list_messages(self, query: str = '', max_results: int = 100, days_back: int = 7) -> List[Dict]:
        """List Gmail messages with optional filtering"""
        if not self.service:
            return []
        
        try:
            # Add date filter
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            if query:
                query = f"{query} after:{date_filter}"
            else:
                query = f"after:{date_filter}"
            
            messages = []
            page_token = None
            
            while len(messages) < max_results:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token,
                    maxResults=min(500, max_results - len(messages))
                ).execute()
                
                batch_messages = results.get('messages', [])
                messages.extend(batch_messages)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            return messages[:max_results]
            
        except HttpError as error:
            print(f"Error listing messages: {error}")
            return []
    
    def get_message_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed information about a specific message"""
        if not self.service:
            return None
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return self.parse_message(message)
            
        except HttpError as error:
            print(f"Error getting message {message_id}: {error}")
            return None
    
    def parse_message(self, message: Dict) -> Dict:
        """Parse Gmail message into structured data"""
        # Extract headers
        headers = message['payload'].get('headers', [])
        header_dict = {header['name']: header['value'] for header in headers}
        
        # Extract body content
        text_content, html_content = self.extract_message_body(message['payload'])
        
        # Parse date
        date_str = header_dict.get('Date', '')
        received_at = self.parse_email_date(date_str)
        
        # Extract sender info
        sender_email, sender_name = self.parse_sender(header_dict.get('From', ''))
        
        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'labels': message.get('labelIds', []),
            'snippet': message.get('snippet', ''),
            'received_at': received_at,
            'sender_email': sender_email,
            'sender_name': sender_name,
            'subject': header_dict.get('Subject', ''),
            'content_text': text_content,
            'content_html': html_content,
            'content_length': len(text_content) if text_content else 0,
            'message_id_header': header_dict.get('Message-ID', ''),
            'size_estimate': message.get('sizeEstimate', 0),
            'is_newsletter': self.is_likely_newsletter(header_dict, text_content, html_content)
        }
    
    def extract_message_body(self, payload: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Extract text and HTML content from message payload"""
        text_content = None
        html_content = None
        
        def extract_from_part(part):
            nonlocal text_content, html_content
            
            mime_type = part.get('mimeType', '')
            if 'data' in part.get('body', {}):
                data = part['body']['data']
                content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
                if mime_type == 'text/plain' and not text_content:
                    text_content = content
                elif mime_type == 'text/html' and not html_content:
                    html_content = content
        
        # Handle multipart messages
        if 'parts' in payload:
            for part in payload['parts']:
                if 'parts' in part:
                    # Nested multipart
                    for subpart in part['parts']:
                        extract_from_part(subpart)
                else:
                    extract_from_part(part)
        else:
            extract_from_part(payload)
        
        # Convert HTML to text if no plain text available
        if not text_content and html_content:
            text_content = self.html_to_text(html_content)
        
        return text_content, html_content
    
    def html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception:
            return html_content
    
    def parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.now()
    
    def parse_sender(self, from_header: str) -> Tuple[str, Optional[str]]:
        """Parse sender email and name from From header"""
        try:
            from email.utils import parseaddr
            name, email_addr = parseaddr(from_header)
            return email_addr.lower(), name if name else None
        except Exception:
            return from_header.lower(), None
    
    def is_likely_newsletter(self, headers: Dict, text_content: str = None, html_content: str = None) -> bool:
        """Determine if email is likely a newsletter"""
        indicators = 0
        
        # Check for unsubscribe links
        if text_content or html_content:
            content = (text_content or '') + (html_content or '')
            unsubscribe_patterns = [
                r'unsubscribe',
                r'opt.?out',
                r'remove.?me',
                r'manage.?preferences',
                r'email.?preferences'
            ]
            for pattern in unsubscribe_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    indicators += 2
                    break
        
        # Check headers
        list_unsubscribe = headers.get('List-Unsubscribe', '')
        if list_unsubscribe:
            indicators += 3
        
        # Check for mailing list headers
        list_headers = ['List-ID', 'List-Post', 'List-Help', 'Mailing-List']
        for header in list_headers:
            if headers.get(header):
                indicators += 1
        
        # Check sender patterns
        sender = headers.get('From', '').lower()
        newsletter_sender_patterns = [
            r'newsletter',
            r'noreply',
            r'no-reply',
            r'digest',
            r'updates?',
            r'notifications?',
            r'alerts?'
        ]
        for pattern in newsletter_sender_patterns:
            if re.search(pattern, sender):
                indicators += 1
        
        # Check subject patterns
        subject = headers.get('Subject', '').lower()
        newsletter_subject_patterns = [
            r'newsletter',
            r'digest',
            r'weekly.*update',
            r'daily.*update',
            r'monthly.*update',
            r'issue.*\d+',
            r'edition.*\d+',
            r'vol\.?\s*\d+'
        ]
        for pattern in newsletter_subject_patterns:
            if re.search(pattern, subject):
                indicators += 1
        
        # Return true if we have strong indicators
        return indicators >= 3
    
    def extract_newsletter_metadata(self, email_data: Dict) -> Dict:
        """Extract newsletter-specific metadata"""
        sender_email = email_data.get('sender_email', '')
        domain = urlparse(f"http://{sender_email.split('@')[-1]}").netloc if '@' in sender_email else ''
        
        # Try to determine newsletter title
        title = self.guess_newsletter_title(email_data)
        
        # Estimate publication frequency
        frequency = self.estimate_publication_frequency(email_data)
        
        # Categorize newsletter
        category = self.categorize_newsletter(email_data)
        
        return {
            'sender_email': sender_email,
            'sender_name': email_data.get('sender_name'),
            'newsletter_title': title,
            'domain': domain,
            'category': category,
            'publication_frequency': frequency,
            'average_length': email_data.get('content_length', 0)
        }
    
    def guess_newsletter_title(self, email_data: Dict) -> Optional[str]:
        """Guess newsletter title from email content"""
        subject = email_data.get('subject', '')
        sender_name = email_data.get('sender_name', '')
        
        # Common newsletter title patterns
        title_patterns = [
            r'(.+?)\s*newsletter',
            r'(.+?)\s*digest',
            r'(.+?)\s*weekly',
            r'(.+?)\s*daily',
            r'(.+?)\s*update',
            r'the\s+(.+?)\s+report',
            r'(.+?)\s*bulletin'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to sender name or domain
        if sender_name and sender_name != email_data.get('sender_email'):
            return sender_name
        
        # Extract from domain
        domain = email_data.get('sender_email', '').split('@')[-1]
        if domain:
            return domain.split('.')[0].title()
        
        return None
    
    def estimate_publication_frequency(self, email_data: Dict) -> Optional[str]:
        """Estimate how often this newsletter is published"""
        subject = email_data.get('subject', '').lower()
        
        if any(word in subject for word in ['daily', 'today']):
            return 'daily'
        elif any(word in subject for word in ['weekly', 'week']):
            return 'weekly'
        elif any(word in subject for word in ['monthly', 'month']):
            return 'monthly'
        elif any(word in subject for word in ['quarterly', 'quarter']):
            return 'quarterly'
        
        return 'unknown'
    
    def categorize_newsletter(self, email_data: Dict) -> Optional[str]:
        """Categorize newsletter based on content"""
        content = (email_data.get('subject', '') + ' ' + 
                  email_data.get('content_text', '') or '').lower()
        
        categories = {
            'Technology': ['tech', 'software', 'ai', 'machine learning', 'programming', 'coding', 'developer'],
            'Business': ['business', 'startup', 'entrepreneur', 'marketing', 'sales', 'strategy'],
            'Finance': ['finance', 'investment', 'crypto', 'stock', 'trading', 'money', 'economy'],
            'News': ['news', 'politics', 'world', 'breaking', 'update', 'current events'],
            'Health': ['health', 'wellness', 'fitness', 'medical', 'nutrition', 'exercise'],
            'Science': ['science', 'research', 'study', 'discovery', 'experiment', 'academic'],
            'Education': ['education', 'learning', 'course', 'training', 'skill', 'knowledge'],
            'Lifestyle': ['lifestyle', 'travel', 'food', 'culture', 'entertainment', 'fashion']
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return 'General'
    
    def sync_emails(self, max_emails: int = 100, days_back: int = 7) -> Dict:
        """Sync emails and detect newsletters"""
        if not self.service:
            return {'error': 'Not authenticated'}
        
        try:
            # Get recent emails
            messages = self.list_messages(max_results=max_emails, days_back=days_back)
            
            processed_emails = []
            newsletters_detected = []
            
            for message in messages:
                email_data = self.get_message_details(message['id'])
                if email_data:
                    processed_emails.append(email_data)
                    
                    # Check if it's a newsletter
                    if email_data.get('is_newsletter'):
                        newsletter_metadata = self.extract_newsletter_metadata(email_data)
                        newsletters_detected.append({
                            'email_data': email_data,
                            'newsletter_metadata': newsletter_metadata
                        })
            
            return {
                'status': 'success',
                'emails_processed': len(processed_emails),
                'newsletters_detected': len(newsletters_detected),
                'processed_emails': processed_emails,
                'newsletters': newsletters_detected,
                'sync_completed_at': datetime.now()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'emails_processed': 0,
                'newsletters_detected': 0
            }