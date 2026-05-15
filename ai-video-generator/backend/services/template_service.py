import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from models.template import (
    Template, TemplateRequest, TemplateResponse, 
    TemplateListResponse, TemplateCategory, TemplateUsage
)
from utils.config import get_settings

logger = logging.getLogger(__name__)

# In-memory storage for demo purposes (replace with database in production)
templates_db: Dict[str, Dict[str, Any]] = {}

# Sample templates
SAMPLE_TEMPLATES = [
    {
        "id": "template_corporate_1",
        "name": "Modern Corporate",
        "description": "Clean and professional corporate video template",
        "category": TemplateCategory.CORPORATE,
        "style": {
            "color_scheme": ["#1f2937", "#374151", "#6b7280", "#9ca3af", "#d1d5db"],
            "font_family": "Inter",
            "background_style": "gradient",
            "animation_style": "smooth",
            "transition_effects": ["fade", "slide", "zoom"]
        },
        "settings": {
            "max_duration": 300,
            "default_quality": "HD",
            "supported_formats": ["MP4", "WebM"],
            "aspect_ratio": "16:9",
            "fps": 30
        },
        "thumbnail_url": "/templates/corporate_1_thumb.jpg",
        "preview_url": "/templates/corporate_1_preview.mp4",
        "tags": ["professional", "business", "clean"],
        "popularity_score": 4.5,
        "usage_count": 1250,
        "is_premium": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "template_educational_1",
        "name": "Educational Tutorial",
        "description": "Engaging template for educational content",
        "category": TemplateCategory.EDUCATIONAL,
        "style": {
            "color_scheme": ["#3b82f6", "#60a5fa", "#93c5fd", "#dbeafe", "#eff6ff"],
            "font_family": "Roboto",
            "background_style": "minimal",
            "animation_style": "playful",
            "transition_effects": ["bounce", "flip", "rotate"]
        },
        "settings": {
            "max_duration": 600,
            "default_quality": "HD",
            "supported_formats": ["MP4", "WebM"],
            "aspect_ratio": "16:9",
            "fps": 30
        },
        "thumbnail_url": "/templates/educational_1_thumb.jpg",
        "preview_url": "/templates/educational_1_preview.mp4",
        "tags": ["education", "tutorial", "learning"],
        "popularity_score": 4.2,
        "usage_count": 890,
        "is_premium": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": "template_marketing_1",
        "name": "Marketing Campaign",
        "description": "Dynamic template for marketing videos",
        "category": TemplateCategory.MARKETING,
        "style": {
            "color_scheme": ["#ec4899", "#f472b6", "#f9a8d4", "#fce7f3", "#fdf2f8"],
            "font_family": "Montserrat",
            "background_style": "dynamic",
            "animation_style": "energetic",
            "transition_effects": ["flash", "glitch", "slide"]
        },
        "settings": {
            "max_duration": 180,
            "default_quality": "HD",
            "supported_formats": ["MP4", "WebM"],
            "aspect_ratio": "16:9",
            "fps": 30
        },
        "thumbnail_url": "/templates/marketing_1_thumb.jpg",
        "preview_url": "/templates/marketing_1_preview.mp4",
        "tags": ["marketing", "campaign", "dynamic"],
        "popularity_score": 4.7,
        "usage_count": 2100,
        "is_premium": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Initialize templates database
for template_data in SAMPLE_TEMPLATES:
    templates_db[template_data["id"]] = template_data

# Template usage tracking
template_usage_db: Dict[str, Dict[str, Any]] = {}


class TemplateService:
    """Service for template operations"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def get_templates(
        self, 
        page: int = 1, 
        limit: int = 10, 
        category: Optional[TemplateCategory] = None,
        is_premium: Optional[bool] = None,
        search: Optional[str] = None
    ) -> TemplateListResponse:
        """Get list of templates with pagination and filtering"""
        filtered_templates = []
        
        for template_data in templates_db.values():
            if category and template_data["category"] != category:
                continue
            if is_premium is not None and template_data["is_premium"] != is_premium:
                continue
            if search and search.lower() not in template_data["name"].lower() and search.lower() not in template_data["description"].lower():
                continue
            filtered_templates.append(Template(**template_data))
        
        # Sort by popularity score and usage count
        filtered_templates.sort(key=lambda x: (x.popularity_score, x.usage_count), reverse=True)
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_templates = filtered_templates[start:end]
        
        total = len(filtered_templates)
        total_pages = (total + limit - 1) // limit
        categories = list(TemplateCategory)
        
        return TemplateListResponse(
            templates=paginated_templates,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            categories=categories
        )
    
    async def get_template(self, template_id: str) -> Optional[TemplateResponse]:
        """Get template details by ID"""
        template_data = templates_db.get(template_id)
        if not template_data:
            return None
        
        # Increment usage count
        template_data["usage_count"] += 1
        template_data["updated_at"] = datetime.utcnow()
        
        return TemplateResponse(template=Template(**template_data))
    
    async def create_template(self, template_request: TemplateRequest) -> TemplateResponse:
        """Create a new template"""
        template_id = str(uuid.uuid4())
        
        template_data = {
            "id": template_id,
            "name": template_request.name,
            "description": template_request.description,
            "category": template_request.category,
            "style": template_request.style.dict(),
            "settings": template_request.settings.dict(),
            "thumbnail_url": None,
            "preview_url": None,
            "tags": template_request.tags,
            "popularity_score": 0.0,
            "usage_count": 0,
            "is_premium": template_request.is_premium,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        templates_db[template_id] = template_data
        return TemplateResponse(template=Template(**template_data))
    
    async def update_template(self, template_id: str, template_request: TemplateRequest) -> Optional[TemplateResponse]:
        """Update an existing template"""
        if template_id not in templates_db:
            return None
        
        template_data = templates_db[template_id]
        template_data.update({
            "name": template_request.name,
            "description": template_request.description,
            "category": template_request.category,
            "style": template_request.style.dict(),
            "settings": template_request.settings.dict(),
            "tags": template_request.tags,
            "is_premium": template_request.is_premium,
            "updated_at": datetime.utcnow()
        })
        
        return TemplateResponse(template=Template(**template_data))
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        if template_id not in templates_db:
            return False
        
        del templates_db[template_id]
        if template_id in template_usage_db:
            del template_usage_db[template_id]
        
        return True
    
    async def get_categories(self) -> List[TemplateCategory]:
        """Get available template categories"""
        return list(TemplateCategory)
    
    async def get_template_usage(self, template_id: str) -> Optional[TemplateUsage]:
        """Get template usage statistics"""
        template_data = templates_db.get(template_id)
        if not template_data:
            return None
        
        usage_data = template_usage_db.get(template_id, {
            "user_ratings": [],
            "last_used": None
        })
        
        return TemplateUsage(
            template_id=template_id,
            usage_count=template_data["usage_count"],
            last_used=usage_data.get("last_used"),
            user_ratings=usage_data.get("user_ratings", []),
            average_rating=sum(usage_data.get("user_ratings", [])) / len(usage_data.get("user_ratings", [1])) if usage_data.get("user_ratings") else None
        )
    
    async def rate_template(self, template_id: str, rating: int) -> bool:
        """Rate a template (1-5 stars)"""
        template_data = templates_db.get(template_id)
        if not template_data:
            return False
        
        if template_id not in template_usage_db:
            template_usage_db[template_id] = {
                "user_ratings": [],
                "last_used": None
            }
        
        template_usage_db[template_id]["user_ratings"].append(rating)
        
        # Update popularity score based on ratings
        ratings = template_usage_db[template_id]["user_ratings"]
        avg_rating = sum(ratings) / len(ratings)
        template_data["popularity_score"] = avg_rating
        template_data["updated_at"] = datetime.utcnow()
        
        return True
    
    async def get_popular_templates(self, limit: int = 10) -> List[Template]:
        """Get popular templates based on usage and ratings"""
        all_templates = []
        
        for template_data in templates_db.values():
            template = Template(**template_data)
            all_templates.append(template)
        
        # Sort by popularity score and usage count
        all_templates.sort(key=lambda x: (x.popularity_score, x.usage_count), reverse=True)
        
        return all_templates[:limit]
