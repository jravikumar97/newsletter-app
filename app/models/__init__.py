from app.database import Base
from .user import User
from .interest import UserInterest, UserPreference
from .newsletter import Newsletter, UserNewsletter, NewsletterEmail, EmailConnection

# Import all models here so they are registered with SQLAlchemy
__all__ = ["Base", "User", "UserInterest", "UserPreference", "Newsletter", "UserNewsletter", "NewsletterEmail", "EmailConnection"]