import os
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import mimetypes
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StaticFileServer:
    """Production static file serving with caching and optimization"""
    
    def __init__(self, app: FastAPI, static_dir: str = "static", url_prefix: str = "/static"):
        self.app = app
        self.static_dir = Path(static_dir)
        self.url_prefix = url_prefix
        self.cache_dir = self.static_dir / "cache"
        self.compressed_dir = self.static_dir / "compressed"
        
        # Create directories
        self.static_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.compressed_dir.mkdir(exist_ok=True)
        
        self.setup_static_serving()
    
    def setup_static_serving(self):
        """Setup static file serving with optimization"""
        
        # Mount static files with custom configuration
        self.app.mount(
            self.url_prefix,
            StaticFiles(
                directory=str(self.static_dir),
                html=True,
                cache_control="public, max-age=31536000",  # 1 year
                check_dir=True
            ),
            name="static"
        )
        
        # Add optimized file serving endpoints
        self.add_optimized_endpoints()
    
    def add_optimized_endpoints(self):
        """Add optimized file serving endpoints"""
        
        @self.app.get(f"{self.url_prefix}/{{file_path:path}}")
        async def serve_static_file(file_path: str):
            """Serve static file with optimization"""
            file_full_path = self.static_dir / file_path
            
            if not file_full_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            # Get file info
            file_size = file_full_path.stat().st_size
            file_mtime = file_full_path.stat().st_mtime
            
            # Generate ETag
            etag = f'"{file_size}-{int(file_mtime)}"'
            
            # Check if client has cached version
            headers = {}
            headers["ETag"] = etag
            headers["Cache-Control"] = "public, max-age=31536000"
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(file_full_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Serve file
            return FileResponse(
                file_full_path,
                media_type=mime_type,
                headers=headers
            )
        
        @self.app.get(f"{self.url_prefix}/compressed/{{file_path:path}}")
        async def serve_compressed_file(file_path: str):
            """Serve compressed file (gzip/brotli)"""
            # Check for compressed versions
            original_path = self.static_dir / file_path
            gzip_path = self.compressed_dir / f"{file_path}.gz"
            brotli_path = self.compressed_dir / f"{file_path}.br"
            
            # Choose best compression
            if brotli_path.exists():
                return FileResponse(
                    brotli_path,
                    media_type=mimetypes.guess_type(str(original_path))[0],
                    headers={
                        "Content-Encoding": "br",
                        "Cache-Control": "public, max-age=31536000"
                    }
                )
            elif gzip_path.exists():
                return FileResponse(
                    gzip_path,
                    media_type=mimetypes.guess_type(str(original_path))[0],
                    headers={
                        "Content-Encoding": "gzip",
                        "Cache-Control": "public, max-age=31536000"
                    }
                )
            else:
                # Fallback to original
                return await serve_static_file(file_path)
    
    def compress_static_files(self):
        """Compress static files for better performance"""
        import gzip
        import brotli
        
        for file_path in self.static_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # Skip already compressed files
                    if file_path.suffix in ['.gz', '.br', '.zip']:
                        continue
                    
                    # Read original file
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Create compressed versions
                    relative_path = file_path.relative_to(self.static_dir)
                    
                    # Gzip compression
                    gzip_path = self.compressed_dir / f"{relative_path}.gz"
                    gzip_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(gzip_path, 'wb') as f:
                        f.write(gzip.compress(content, compresslevel=9))
                    
                    # Brotli compression
                    brotli_path = self.compressed_dir / f"{relative_path}.br"
                    with open(brotli_path, 'wb') as f:
                        f.write(brotli.compress(content, quality=11))
                    
                    logger.info(f"Compressed: {relative_path}")
                    
                except Exception as e:
                    logger.error(f"Error compressing {file_path}: {str(e)}")
    
    def generate_file_manifest(self) -> dict:
        """Generate manifest with file hashes for cache busting"""
        manifest = {}
        
        for file_path in self.static_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # Calculate file hash
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()[:8]
                    
                    # Get relative path
                    relative_path = str(file_path.relative_to(self.static_dir))
                    
                    # Add to manifest
                    manifest[relative_path] = {
                        "hash": file_hash,
                        "size": file_path.stat().st_size,
                        "mtime": file_path.stat().st_mtime
                    }
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Save manifest
        manifest_path = self.static_dir / "manifest.json"
        import json
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest


class AssetOptimizer:
    """Asset optimization for production"""
    
    def __init__(self, static_dir: str = "static"):
        self.static_dir = Path(static_dir)
        self.optimized_dir = self.static_dir / "optimized"
        self.optimized_dir.mkdir(exist_ok=True)
    
    def optimize_images(self):
        """Optimize images for production"""
        try:
            from PIL import Image, ImageOps
        except ImportError:
            logger.warning("PIL not available, skipping image optimization")
            return
        
        for image_path in self.static_dir.rglob("*"):
            if image_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                try:
                    with Image.open(image_path) as img:
                        # Auto-orient
                        img = ImageOps.exif_transpose(img)
                        
                        # Convert to RGB if necessary
                        if img.mode in ['RGBA', 'LA']:
                            # Create white background
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                background.paste(img, mask=img.split()[-1])
                            else:
                                background.paste(img, mask=img.split()[-1])
                            img = background
                        
                        # Resize if too large
                        max_size = (1920, 1080)
                        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                            img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        
                        # Save optimized version
                        relative_path = image_path.relative_to(self.static_dir)
                        optimized_path = self.optimized_dir / relative_path
                        optimized_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Save with optimization
                        if image_path.suffix.lower() in ['.png']:
                            img.save(optimized_path, 'PNG', optimize=True)
                        elif image_path.suffix.lower() in ['.jpg', '.jpeg']:
                            img.save(optimized_path, 'JPEG', quality=85, optimize=True)
                        elif image_path.suffix.lower() == '.webp':
                            img.save(optimized_path, 'WebP', quality=85, optimize=True)
                        
                        logger.info(f"Optimized image: {relative_path}")
                        
                except Exception as e:
                    logger.error(f"Error optimizing {image_path}: {str(e)}")
    
    def minify_css_js(self):
        """Minify CSS and JS files"""
        try:
            import cssmin
            import jsmin
        except ImportError:
            logger.warning("cssmin/jsmin not available, skipping minification")
            return
        
        for file_path in self.static_dir.rglob("*"):
            if file_path.suffix == '.css':
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    minified = cssmin.cssmin(content)
                    
                    relative_path = file_path.relative_to(self.static_dir)
                    minified_path = self.optimized_dir / relative_path
                    minified_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(minified_path, 'w') as f:
                        f.write(minified)
                    
                    logger.info(f"Minified CSS: {relative_path}")
                    
                except Exception as e:
                    logger.error(f"Error minifying {file_path}: {str(e)}")
            
            elif file_path.suffix == '.js':
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    minified = jsmin.jsmin(content)
                    
                    relative_path = file_path.relative_to(self.static_dir)
                    minified_path = self.optimized_dir / relative_path
                    minified_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(minified_path, 'w') as f:
                        f.write(minified)
                    
                    logger.info(f"Minified JS: {relative_path}")
                    
                except Exception as e:
                    logger.error(f"Error minifying {file_path}: {str(e)}")


def setup_static_files(app: FastAPI, static_dir: str = "static") -> StaticFileServer:
    """Setup static file serving for production"""
    server = StaticFileServer(app, static_dir)
    
    # Optimize assets
    optimizer = AssetOptimizer(static_dir)
    optimizer.optimize_images()
    optimizer.minify_css_js()
    
    # Compress files
    server.compress_static_files()
    
    # Generate manifest
    server.generate_file_manifest()
    
    logger.info(f"Static file serving setup complete: {static_dir}")
    return server
