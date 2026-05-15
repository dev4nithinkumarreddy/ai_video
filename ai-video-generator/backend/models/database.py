from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class TimestampMixin:
    """Mixin for adding timestamp fields to models"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class User(Base, TimestampMixin):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class Project(Base, TimestampMixin):
    """Project model for organizing video generation projects"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    topic = Column(String(500))
    status = Column(String(50), default="draft", nullable=False)  # draft, processing, completed, failed
    total_duration = Column(Float)  # Total video duration in seconds
    total_scenes = Column(Integer, default=0)
    settings = Column(JSON)  # Project settings (voice, style, etc.)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("GeneratedAsset", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title}, user_id={self.user_id})>"


class Scene(Base, TimestampMixin):
    """Scene model for individual video scenes"""
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    narration = Column(Text, nullable=False)
    visual_prompt = Column(Text, nullable=False)
    duration = Column(Float, nullable=False)  # Duration in seconds
    camera_movement = Column(String(100), default="static")
    mood = Column(String(100), default="professional")
    
    # Relationships
    project = relationship("Project", back_populates="scenes")
    assets = relationship("GeneratedAsset", back_populates="scene", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scene(id={self.id}, project_id={self.project_id}, scene_number={self.scene_number})>"


class GeneratedAsset(Base, TimestampMixin):
    """GeneratedAsset model for tracking generated files (audio, images, videos)"""
    __tablename__ = "generated_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True)  # Optional, for scene-specific assets
    asset_type = Column(String(50), nullable=False)  # script, audio, image, video
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500))
    file_size = Column(Integer)  # Size in bytes
    asset_metadata = Column(JSON)  # Additional metadata (duration, resolution, etc.)
    status = Column(String(50), default="processing", nullable=False)  # processing, completed, failed
    error_message = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="assets")
    scene = relationship("Scene", back_populates="assets")
    
    def __repr__(self):
        return f"<GeneratedAsset(id={self.id}, type={self.asset_type}, project_id={self.project_id})>"
