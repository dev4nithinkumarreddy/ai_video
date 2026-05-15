# AI Video Generator Frontend

A modern React.js frontend application for AI-powered video generation with cinematic UI design.

## Features

- 🎬 **Modern UI Design** - Dark theme with neon accents and cinematic aesthetics
- 📱 **Responsive Layout** - Works seamlessly on all devices
- ⚡ **Framer Motion Animations** - Smooth transitions and micro-interactions
- 🎨 **Tailwind CSS** - Utility-first styling with custom components
- 🛣️ **React Router** - Client-side routing with smooth navigation
- 🌐 **Axios Integration** - HTTP client with interceptors and error handling
- 🎭 **Multiple Pages** - Home, Script Preview, Processing, and Result pages
- 📦 **Component Architecture** - Reusable components and clean folder structure
- 🔧 **Environment Variables** - Configurable API endpoints and app settings
- 🎯 **TypeScript Ready** - Easy to migrate to TypeScript if needed

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast development server and build tool
- **React Router DOM** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Axios** - HTTP client
- **PostCSS** - CSS post-processing

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable components
│   │   ├── Navbar.jsx     # Navigation component
│   │   └── LoadingSpinner.jsx  # Loading animation
│   ├── pages/             # Page components
│   │   ├── Home.jsx       # Landing page
│   │   ├── ScriptPreview.jsx  # Script editing page
│   │   ├── Processing.jsx  # Video processing page
│   │   └── Result.jsx     # Video result page
│   ├── hooks/             # Custom React hooks
│   │   ├── useTheme.js    # Theme management
│   │   └── useLocalStorage.js  # Local storage hook
│   ├── utils/             # Utility functions
│   │   ├── api.js         # API configuration
│   │   └── constants.js   # App constants
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # App entry point
│   └── index.css          # Global styles
├── .env                   # Environment variables
├── .env.example           # Environment variables template
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
└── vite.config.js         # Vite configuration
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai_video/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=AI Video Generator
VITE_APP_VERSION=1.0.0
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Build for production:
```bash
npm run build
```

### Preview

Preview production build:
```bash
npm run preview
```

## Pages

### Home (`/`)
- Landing page with hero section
- Script input area
- Feature showcase
- Recent projects display

### Script Preview (`/script-preview`)
- Script editing interface
- Real-time statistics (words, characters, duration)
- AI suggestions
- Template recommendations

### Processing (`/processing`)
- Video generation progress
- Step-by-step processing indicators
- Estimated time remaining
- Tips and information

### Result (`/result`)
- Video player interface
- Download options
- Quality selection
- Share functionality
- Next steps suggestions

## Components

### Navbar
- Responsive navigation
- Active route indicators
- Mobile menu support
- Dark theme toggle

### LoadingSpinner
- Animated loading indicator
- Multiple size options
- Custom text support
- Neon glow effects

## Hooks

### useTheme
- Dark/light theme management
- Local storage persistence
- System preference detection

### useLocalStorage
- Generic local storage hook
- JSON serialization
- Cross-tab synchronization

## API Integration

The app includes a comprehensive API setup with:

- Axios instance with interceptors
- Error handling
- Authentication support
- Multiple API endpoints:
  - Video generation and management
  - Script analysis and suggestions
  - Template management

## Styling

### Tailwind CSS Configuration
- Custom color palette with neon accents
- Dark mode support
- Extended animations
- Custom components

### Design System
- Glass morphism effects
- Neon glow styling
- Gradient backgrounds
- Smooth transitions

## Environment Variables

- `VITE_API_BASE_URL` - Backend API URL
- `VITE_APP_NAME` - Application name
- `VITE_APP_VERSION` - Application version

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
