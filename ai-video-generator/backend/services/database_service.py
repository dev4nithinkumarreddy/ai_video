import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from models.database import User, Project, Scene, GeneratedAsset
from database.database import get_async_session, get_db

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for CRUD operations"""
    
    async def create_user(
        self,
        email: str,
        username: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Create a new user"""
        async for session in get_db():
            user = User(
                email=email,
                username=username,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        async for session in get_db():
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
            break
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with get_async_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        async with get_async_session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()
    
    async def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login time"""
        async for session in get_db():
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login=datetime.utcnow())
            )
            await session.commit()
            return result.rowcount > 0
            break
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login=datetime.utcnow())
            )
            await session.commit()
            return result.rowcount > 0
    
    async def create_project(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        topic: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Project:
        """Create a new project"""
        async for session in get_db():
            project = Project(
                user_id=user_id,
                title=title,
                description=description,
                topic=topic,
                settings=settings or {}
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project
            break
            project = Project(
                user_id=user_id,
                title=title,
                description=description,
                topic=topic,
                settings=settings or {}
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project
    
    async def get_project_by_id(self, project_id: int, user_id: Optional[int] = None) -> Optional[Project]:
        """Get project by ID (optionally filtered by user)"""
        async with get_async_session() as session:
            query = select(Project).where(Project.id == project_id)
            if user_id:
                query = query.where(Project.user_id == user_id)
            
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_user_projects(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Project]:
        """Get user's projects with optional status filter"""
        async with get_async_session() as session:
            query = select(Project).where(Project.user_id == user_id)
            
            if status:
                query = query.where(Project.status == status)
            
            query = query.order_by(Project.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def update_project_status(self, project_id: int, status: str) -> bool:
        """Update project status"""
        async with get_async_session() as session:
            result = await session.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(status=status)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def update_project_metadata(
        self,
        project_id: int,
        total_duration: Optional[float] = None,
        total_scenes: Optional[int] = None
    ) -> bool:
        """Update project metadata"""
        async with get_async_session() as session:
            update_data = {}
            if total_duration is not None:
                update_data['total_duration'] = total_duration
            if total_scenes is not None:
                update_data['total_scenes'] = total_scenes
            
            if not update_data:
                return False
            
            result = await session.execute(
                update(Project)
                .where(Project.id == project_id)
                .values(**update_data)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def create_scene(
        self,
        project_id: int,
        scene_number: int,
        narration: str,
        visual_prompt: str,
        duration: float,
        camera_movement: str = "static",
        mood: str = "professional"
    ) -> Scene:
        """Create a new scene"""
        async with get_async_session() as session:
            scene = Scene(
                project_id=project_id,
                scene_number=scene_number,
                narration=narration,
                visual_prompt=visual_prompt,
                duration=duration,
                camera_movement=camera_movement,
                mood=mood
            )
            session.add(scene)
            await session.commit()
            await session.refresh(scene)
            return scene
    
    async def get_project_scenes(self, project_id: int) -> List[Scene]:
        """Get all scenes for a project"""
        async with get_async_session() as session:
            result = await session.execute(
                select(Scene)
                .where(Scene.project_id == project_id)
                .order_by(Scene.scene_number)
            )
            return result.scalars().all()
    
    async def update_scene(self, scene_id: int, **kwargs) -> bool:
        """Update scene fields"""
        async with get_async_session() as session:
            result = await session.execute(
                update(Scene)
                .where(Scene.id == scene_id)
                .values(**kwargs)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def delete_scene(self, scene_id: int) -> bool:
        """Delete a scene"""
        async with get_async_session() as session:
            result = await session.execute(
                delete(Scene).where(Scene.id == scene_id)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def create_asset(
        self,
        project_id: int,
        asset_type: str,
        file_path: str,
        scene_id: Optional[int] = None,
        file_url: Optional[str] = None,
        file_size: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GeneratedAsset:
        """Create a new generated asset"""
        async with get_async_session() as session:
            asset = GeneratedAsset(
                project_id=project_id,
                scene_id=scene_id,
                asset_type=asset_type,
                file_path=file_path,
                file_url=file_url,
                file_size=file_size,
                metadata=metadata or {}
            )
            session.add(asset)
            await session.commit()
            await session.refresh(asset)
            return asset
    
    async def update_asset_status(
        self,
        asset_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update asset status"""
        async with get_async_session() as session:
            update_data = {'status': status}
            if error_message:
                update_data['error_message'] = error_message
            
            result = await session.execute(
                update(GeneratedAsset)
                .where(GeneratedAsset.id == asset_id)
                .values(**update_data)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def get_project_assets(
        self,
        project_id: int,
        asset_type: Optional[str] = None
    ) -> List[GeneratedAsset]:
        """Get assets for a project, optionally filtered by type"""
        async with get_async_session() as session:
            query = select(GeneratedAsset).where(GeneratedAsset.project_id == project_id)
            
            if asset_type:
                query = query.where(GeneratedAsset.asset_type == asset_type)
            
            query = query.order_by(GeneratedAsset.created_at.desc())
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_scene_assets(self, scene_id: int, asset_type: Optional[str] = None) -> List[GeneratedAsset]:
        """Get assets for a scene, optionally filtered by type"""
        async with get_async_session() as session:
            query = select(GeneratedAsset).where(GeneratedAsset.scene_id == scene_id)
            
            if asset_type:
                query = query.where(GeneratedAsset.asset_type == asset_type)
            
            query = query.order_by(GeneratedAsset.created_at.desc())
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset"""
        async with get_async_session() as session:
            result = await session.execute(
                delete(GeneratedAsset).where(GeneratedAsset.id == asset_id)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        async with get_async_session() as session:
            # Project stats
            project_result = await session.execute(
                select(
                    func.count(Project.id).label('total_projects'),
                    func.sum(func.case((Project.status == 'completed', 1), else_=0)).label('completed_projects'),
                    func.sum(func.case((Project.status == 'processing', 1), else_=0)).label('processing_projects')
                ).where(Project.user_id == user_id)
            )
            project_stats = project_result.first()
            
            # Asset stats
            asset_result = await session.execute(
                select(
                    func.count(GeneratedAsset.id).label('total_assets'),
                    func.sum(GeneratedAsset.file_size).label('total_size')
                )
                .join(Project, GeneratedAsset.project_id == Project.id)
                .where(Project.user_id == user_id)
            )
            asset_stats = asset_result.first()
            
            return {
                'total_projects': project_stats.total_projects or 0,
                'completed_projects': project_stats.completed_projects or 0,
                'processing_projects': project_stats.processing_projects or 0,
                'total_assets': asset_stats.total_assets or 0,
                'total_size_bytes': asset_stats.total_size or 0
            }


# Singleton instance
_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get or create database service instance"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
