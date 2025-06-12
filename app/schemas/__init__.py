from .user import UserCreate, UserUpdate, UserResponse, UserLogin, Token, TokenData
from .auth import UserLogin, Token, TokenData, PasswordReset, PasswordResetConfirm, ChangePassword
from .interest import (
    UserInterestCreate, UserInterestUpdate, UserInterestResponse,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    BulkInterestsCreate, InterestCategory
)
from .newsletter import (
    NewsletterCreate, NewsletterResponse, UserNewsletterCreate, UserNewsletterResponse,
    NewsletterEmailResponse, EmailConnectionCreate, EmailConnectionResponse,
    EmailSyncRequest, EmailSyncResponse, NewsletterStats
)

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "Token", "TokenData",
    "PasswordReset", "PasswordResetConfirm", "ChangePassword",
    "UserInterestCreate", "UserInterestUpdate", "UserInterestResponse",
    "UserPreferenceCreate", "UserPreferenceUpdate", "UserPreferenceResponse",
    "BulkInterestsCreate", "InterestCategory",
    "NewsletterCreate", "NewsletterResponse", "UserNewsletterCreate", "UserNewsletterResponse",
    "NewsletterEmailResponse", "EmailConnectionCreate", "EmailConnectionResponse",
    "EmailSyncRequest", "EmailSyncResponse", "NewsletterStats"
]