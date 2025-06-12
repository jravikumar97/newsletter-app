from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.auth import get_current_active_user
from app.schemas.interest import (
    UserInterestCreate, UserInterestUpdate, UserInterestResponse,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    BulkInterestsCreate, InterestCategory
)
from app.crud import interest as interest_crud

router = APIRouter()

# Interest Categories (predefined)
INTEREST_CATEGORIES = [
    {
        "category": "Technology",
        "subcategories": ["AI/Machine Learning", "Software Development", "Cybersecurity", "Blockchain", "Cloud Computing", "Mobile Development"],
        "description": "Technology trends, innovations, and industry news"
    },
    {
        "category": "Business",
        "subcategories": ["Startups", "Entrepreneurship", "Marketing", "Sales", "Strategy", "Leadership", "Management"],
        "description": "Business strategy, leadership, and industry insights"
    },
    {
        "category": "Finance",
        "subcategories": ["Investment", "Stock Market", "Cryptocurrency", "Personal Finance", "Banking", "Fintech"],
        "description": "Financial markets, investment strategies, and economic news"
    },
    {
        "category": "Health & Wellness",
        "subcategories": ["Nutrition", "Fitness", "Mental Health", "Medical Research", "Lifestyle", "Wellness"],
        "description": "Health, wellness, and medical advancement news"
    },
    {
        "category": "Science",
        "subcategories": ["Research", "Climate", "Space", "Biology", "Physics", "Chemistry"],
        "description": "Scientific discoveries and research developments"
    },
    {
        "category": "News & Politics",
        "subcategories": ["World News", "Politics", "Government", "International Relations", "Policy"],
        "description": "Current events, political developments, and world news"
    },
    {
        "category": "Education",
        "subcategories": ["Online Learning", "Career Development", "Skills", "Academic Research", "Training"],
        "description": "Educational resources and professional development"
    },
    {
        "category": "Lifestyle",
        "subcategories": ["Travel", "Food", "Fashion", "Entertainment", "Culture", "Hobbies"],
        "description": "Lifestyle, culture, and entertainment content"
    }
]

# User Interest Endpoints
@router.get("/categories", response_model=List[InterestCategory])
async def get_interest_categories():
    """
    Get available interest categories and subcategories
    """
    return INTEREST_CATEGORIES

@router.post("/", response_model=UserInterestResponse, status_code=status.HTTP_201_CREATED)
async def create_interest(
    interest: UserInterestCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user interest
    """
    try:
        db_interest = interest_crud.create_user_interest(db, current_user.id, interest)
        return db_interest
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interest: {str(e)}"
        )

@router.get("/", response_model=List[UserInterestResponse])
async def get_my_interests(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all interests for the current user
    """
    interests = interest_crud.get_user_interests(db, current_user.id)
    return interests

@router.get("/{interest_id}", response_model=UserInterestResponse)
async def get_interest(
    interest_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific interest by ID
    """
    interest = interest_crud.get_user_interest_by_id(db, current_user.id, interest_id)
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found"
        )
    return interest

@router.put("/{interest_id}", response_model=UserInterestResponse)
async def update_interest(
    interest_id: int,
    interest_update: UserInterestUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a user interest
    """
    updated_interest = interest_crud.update_user_interest(
        db, current_user.id, interest_id, interest_update
    )
    if not updated_interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found"
        )
    return updated_interest

@router.delete("/{interest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interest(
    interest_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user interest
    """
    success = interest_crud.delete_user_interest(db, current_user.id, interest_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interest not found"
        )

@router.post("/bulk", response_model=List[UserInterestResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_interests(
    bulk_interests: BulkInterestsCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create multiple interests at once
    """
    try:
        db_interests = interest_crud.create_bulk_interests(
            db, current_user.id, bulk_interests.interests
        )
        return db_interests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interests: {str(e)}"
        )

@router.get("/category/{category}", response_model=List[UserInterestResponse])
async def get_interests_by_category(
    category: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user interests by category
    """
    interests = interest_crud.get_interests_by_category(db, current_user.id, category)
    return interests

# User Preference Endpoints
@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_my_preferences(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user preferences
    """
    preferences = interest_crud.get_user_preferences(db, current_user.id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found. Create preferences first."
        )
    return preferences

@router.post("/preferences", response_model=UserPreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_preferences(
    preferences: UserPreferenceCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create user preferences
    """
    # Check if preferences already exist
    existing_preferences = interest_crud.get_user_preferences(db, current_user.id)
    if existing_preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User preferences already exist. Use PUT to update."
        )
    
    try:
        db_preferences = interest_crud.create_user_preferences(db, current_user.id, preferences)
        return db_preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create preferences: {str(e)}"
        )

@router.put("/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    preferences_update: UserPreferenceUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences
    """
    try:
        updated_preferences = interest_crud.update_user_preferences(
            db, current_user.id, preferences_update
        )
        return updated_preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.delete("/preferences", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preferences(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete user preferences
    """
    success = interest_crud.delete_user_preferences(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )