# AI Video Generator Backend

A FastAPI backend for AI-powered video generation with modular architecture and async support.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🏗️ **Modular Architecture** - Clean separation of concerns with routes, services, models, and utils
- 🔄 **Async Support** - Full async/await support for high performance
- 🌐 **CORS Enabled** - Cross-origin resource sharing configured
- 🔧 **Environment Variables** - Flexible configuration management
- 📊 **Health Checks** - Comprehensive health monitoring endpoints
- 📝 **Logging** - Structured logging with rich output
- 🎬 **Video Processing** - Async video generation pipeline
- 📜 **Script Analysis** - AI-powered script analysis and suggestions
- 🎨 **Template System** - Flexible video templates

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **Python-dotenv** - Environment variable management
- **Structlog** - Structured logging
- **Rich** - Rich console output
- **Psutil** - System monitoring

## Project Structure

```
backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── routes/                 # API route handlers
│   ├── __init__.py
│   ├── health.py          # Health check endpoints
│   ├── videos.py          # Video management endpoints
│   ├── scripts.py         # Script analysis endpoints
│   └── templates.py       # Template management endpoints
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── video_service.py   # Video processing service
│   ├── script_service.py  # Script analysis service
│   └── template_service.py # Template management service
├── models/                # Pydantic models
│   ├── __init__.py
│   ├── video.py           # Video-related models
│   ├── script.py          # Script-related models
│   └── template.py        # Template-related models
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   └── logging_config.py  # Logging setup
├── tests/                 # Test files
└── uploads/               # File upload directory
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip or poetry

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai_video/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create your `.env` file in `backend/` and set the required values.

Edit `.env` file with your configuration:
```env
HOST=0.0.0.0
PORT=8000
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production
```

### Running the Application

Development mode:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## API Endpoints

### Health Checks
- `GET /api/health` - Comprehensive health check
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe
- `GET /api/health/version` - Version information

### Videos
- `POST /api/videos/` - Create video generation request
- `GET /api/videos/{video_id}` - Get video details
- `GET /api/videos/{video_id}/status` - Get processing status
- `GET /api/videos/` - List videos with pagination
- `GET /api/videos/{video_id}/download` - Download video
- `DELETE /api/videos/{video_id}` - Delete video
- `POST /api/videos/{video_id}/retry` - Retry failed processing

### Scripts
- `POST /api/scripts/analyze` - Analyze script
- `POST /api/scripts/suggestions` - Get script suggestions
- `POST /api/scripts/` - Save script
- `GET /api/scripts/` - List saved scripts
- `GET /api/scripts/{script_id}` - Get saved script
- `PUT /api/scripts/{script_id}` - Update script
- `DELETE /api/scripts/{script_id}` - Delete script

### Templates
- `GET /api/templates/` - List templates
- `GET /api/templates/{template_id}` - Get template details
- `POST /api/templates/` - Create template
- `PUT /api/templates/{template_id}` - Update template
- `DELETE /api/templates/{template_id}` - Delete template
- `GET /api/templates/categories` - Get categories
- `GET /api/templates/{template_id}/usage` - Get usage stats

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `SECRET_KEY` | JWT secret key | `your-secret-key` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | `logs/app.log` |
| `MAX_FILE_SIZE` | Max upload size | `104857600` |
| `UPLOAD_DIR` | Upload directory | `uploads` |

### CORS Configuration

The API is configured to allow requests from:
- `http://localhost:3000` (React dev server)
- `http://127.0.0.1:3000`
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173`

## Logging

The application uses structured logging with rich console output:

- **Console**: Rich formatted logs with colors and markup
- **File**: Rotating log files (10MB max, 5 backups)
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Services

### Video Service
Handles video generation, processing, and management:
- Async video processing pipeline
- Progress tracking
- File management
- Quality options

### Script Service
Provides script analysis and AI suggestions:
- Word count and duration estimation
- Keyword extraction
- Sentiment analysis
- Readability scoring
- AI-powered suggestions

### Template Service
Manages video templates:
- Template CRUD operations
- Category management
- Usage tracking
- Rating system

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Production Deployment

### Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ai-video-backend .
docker run -p 8000:8000 ai-video-backend
```

### Environment Setup

For production, ensure:
1. Set `DEBUG=false`
2. Use a strong `SECRET_KEY`
3. Configure proper logging
4. Set up database connections
5. Configure file storage

## Monitoring

The health check endpoints provide:
- System metrics (CPU, memory, disk)
- Service status
- Dependency checks
- Performance metrics

## Security

- CORS protection
- Request validation
- Error handling
- Logging and monitoring
- Environment variable protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
