import asyncio
import uuid
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from models.script import (
    ScriptRequest, ScriptResponse, ScriptAnalysisRequest, 
    ScriptAnalysisResponse, ScriptSuggestion, ScriptAnalysis, ScriptTemplate
)
from utils.config import get_settings

logger = logging.getLogger(__name__)

# In-memory storage for demo purposes (replace with database in production)
scripts_db: Dict[str, Dict[str, Any]] = {}

# Sample script templates
SCRIPT_TEMPLATES = [
    ScriptTemplate(
        id="template_1",
        name="Product Launch",
        description="Template for product launch videos",
        category="marketing",
        script_template="Introducing {product_name}, the revolutionary {product_category} that will change the way you {benefit}. With features like {feature_1}, {feature_2}, and {feature_3}, you'll experience {main_benefit}. Don't miss out on this opportunity to {call_to_action}.",
        variables=["product_name", "product_category", "benefit", "feature_1", "feature_2", "feature_3", "main_benefit", "call_to_action"],
        examples=[
            {
                "variables": {
                    "product_name": "SmartWatch Pro",
                    "product_category": "smartwatch",
                    "benefit": "track your fitness",
                    "feature_1": "heart rate monitoring",
                    "feature_2": "GPS tracking",
                    "feature_3": "sleep analysis",
                    "main_benefit": "better health insights",
                    "call_to_action": "upgrade your fitness journey"
                }
            }
        ],
        created_at=datetime.utcnow()
    ),
    ScriptTemplate(
        id="template_2",
        name="Educational Tutorial",
        description="Template for educational content",
        category="educational",
        script_template="Welcome to this tutorial on {topic}. Today, we'll learn about {main_concept}. First, let's understand {step_1}. Then, we'll explore {step_2}. Finally, we'll practice {step_3}. By the end of this video, you'll be able to {outcome}.",
        variables=["topic", "main_concept", "step_1", "step_2", "step_3", "outcome"],
        examples=[
            {
                "variables": {
                    "topic": "Python programming",
                    "main_concept": "list comprehensions",
                    "step_1": "basic syntax",
                    "step_2": "advanced patterns",
                    "step_3": "real-world examples",
                    "outcome": "write efficient list comprehensions"
                }
            }
        ],
        created_at=datetime.utcnow()
    )
]


class ScriptService:
    """Service for script operations"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def analyze_script(
        self, 
        script: str, 
        include_suggestions: bool = True,
        analysis_depth: str = "standard"
    ) -> ScriptAnalysisResponse:
        """Analyze a script and return insights"""
        start_time = datetime.utcnow()
        
        # Basic analysis
        word_count = len(script.split())
        character_count = len(script)
        estimated_duration = max(30, word_count // 3)  # Rough estimate: 3 words per second
        
        # Extract keywords (simple implementation)
        words = re.findall(r'\b\w+\b', script.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter out short words
                word_freq[word] = word_freq.get(word, 0) + 1
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [word for word, freq in keywords]
        
        # Detect topics (simple keyword-based approach)
        topics = []
        topic_keywords = {
            "technology": ["software", "computer", "digital", "app", "system"],
            "business": ["company", "market", "sales", "customer", "revenue"],
            "education": ["learn", "teach", "student", "course", "knowledge"],
            "health": ["health", "medical", "patient", "treatment", "wellness"]
        }
        
        for topic, kwords in topic_keywords.items():
            if any(kword in script.lower() for kword in kwords):
                topics.append(topic)
        
        # Calculate complexity score (simple metric)
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        complexity_score = min(1.0, avg_word_length / 8)
        
        # Calculate readability score (simplified Flesch-Kincaid)
        sentences = len(re.findall(r'[.!?]+', script))
        avg_sentence_length = word_count / sentences if sentences > 0 else 0
        readability_score = max(0, min(100, 206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length)))
        
        analysis = ScriptAnalysis(
            word_count=word_count,
            character_count=character_count,
            estimated_duration=estimated_duration,
            sentiment="neutral",  # Would use NLP library in production
            keywords=keywords,
            topics=topics,
            complexity_score=complexity_score,
            readability_score=readability_score
        )
        
        # Generate suggestions if requested
        suggestions = []
        if include_suggestions:
            suggestions = await self._generate_suggestions(script, analysis)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ScriptAnalysisResponse(
            analysis=analysis,
            suggestions=suggestions,
            processing_time=processing_time
        )
    
    async def get_script_suggestions(self, script: str) -> List[ScriptSuggestion]:
        """Get AI-powered suggestions for script improvement"""
        analysis = await self.analyze_script(script, include_suggestions=False)
        return await self._generate_suggestions(script, analysis.analysis)
    
    async def save_script(self, script_request: ScriptRequest) -> ScriptResponse:
        """Save a script"""
        script_id = str(uuid.uuid4())
        
        # Analyze the script
        analysis_result = await self.analyze_script(script_request.script)
        
        script_data = {
            "id": script_id,
            "title": script_request.title,
            "description": script_request.description,
            "script": script_request.script,
            "tags": script_request.tags,
            "analysis": analysis_result.analysis,
            "suggestions": analysis_result.suggestions,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        scripts_db[script_id] = script_data
        return ScriptResponse(**script_data)
    
    async def get_saved_scripts(
        self, 
        page: int = 1, 
        limit: int = 10, 
        tag: Optional[str] = None
    ) -> List[ScriptResponse]:
        """Get saved scripts with pagination and filtering"""
        filtered_scripts = []
        
        for script_data in scripts_db.values():
            if tag and tag not in script_data.get("tags", []):
                continue
            filtered_scripts.append(ScriptResponse(**script_data))
        
        # Sort by created_at descending
        filtered_scripts.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        return filtered_scripts[start:end]
    
    async def get_script(self, script_id: str) -> Optional[ScriptResponse]:
        """Get a saved script by ID"""
        script_data = scripts_db.get(script_id)
        if not script_data:
            return None
        return ScriptResponse(**script_data)
    
    async def update_script(self, script_id: str, script_request: ScriptRequest) -> Optional[ScriptResponse]:
        """Update a saved script"""
        if script_id not in scripts_db:
            return None
        
        # Re-analyze the updated script
        analysis_result = await self.analyze_script(script_request.script)
        
        script_data = scripts_db[script_id]
        script_data.update({
            "title": script_request.title,
            "description": script_request.description,
            "script": script_request.script,
            "tags": script_request.tags,
            "analysis": analysis_result.analysis,
            "suggestions": analysis_result.suggestions,
            "updated_at": datetime.utcnow()
        })
        
        return ScriptResponse(**script_data)
    
    async def delete_script(self, script_id: str) -> bool:
        """Delete a saved script"""
        if script_id not in scripts_db:
            return False
        
        del scripts_db[script_id]
        return True
    
    async def get_script_templates(self, category: Optional[str] = None) -> List[ScriptTemplate]:
        """Get available script templates"""
        templates = SCRIPT_TEMPLATES
        if category:
            templates = [t for t in templates if t.category == category]
        return templates
    
    async def generate_script_from_template(self, template_id: str, variables: dict) -> Optional[str]:
        """Generate a script from a template"""
        template = next((t for t in SCRIPT_TEMPLATES if t.id == template_id), None)
        if not template:
            return None
        
        # Replace variables in template
        script = template.script_template
        for var, value in variables.items():
            script = script.replace(f"{{{var}}}", str(value))
        
        return script
    
    async def _generate_suggestions(self, script: str, analysis: ScriptAnalysis) -> List[ScriptSuggestion]:
        """Generate suggestions for script improvement"""
        suggestions = []
        
        # Length suggestions
        if analysis.word_count < 50:
            suggestions.append(ScriptSuggestion(
                type="length",
                text="Consider adding more detail to make your script more engaging",
                priority="medium"
            ))
        elif analysis.word_count > 1000:
            suggestions.append(ScriptSuggestion(
                type="length",
                text="Your script is quite long. Consider breaking it into shorter segments",
                priority="high"
            ))
        
        # Complexity suggestions
        if analysis.complexity_score > 0.7:
            suggestions.append(ScriptSuggestion(
                type="complexity",
                text="Your script uses complex language. Consider simplifying for better understanding",
                priority="medium"
            ))
        
        # Readability suggestions
        if analysis.readability_score < 50:
            suggestions.append(ScriptSuggestion(
                type="readability",
                text="Consider using shorter sentences to improve readability",
                priority="medium"
            ))
        
        # Content suggestions
        if not analysis.topics:
            suggestions.append(ScriptSuggestion(
                type="content",
                text="Add specific topics or themes to make your content more focused",
                priority="low"
            ))
        
        return suggestions
