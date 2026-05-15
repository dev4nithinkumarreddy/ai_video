// App constants
export const APP_CONFIG = {
  NAME: import.meta.env.VITE_APP_NAME || 'AI Video Generator',
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
}

// Video quality options
export const VIDEO_QUALITIES = {
  SD: { label: 'SD (480p)', resolution: '854x480', bitrate: '1000k' },
  HD: { label: 'HD (720p)', resolution: '1280x720', bitrate: '2500k' },
  FULL_HD: { label: 'Full HD (1080p)', resolution: '1920x1080', bitrate: '5000k' },
  UHD_4K: { label: '4K (2160p)', resolution: '3840x2160', bitrate: '15000k' },
}

// Video formats
export const VIDEO_FORMATS = ['MP4', 'WebM', 'AVI', 'MOV']

// Animation durations
export const ANIMATIONS = {
  FAST: 0.2,
  NORMAL: 0.3,
  SLOW: 0.5,
  VERY_SLOW: 1.0,
}

// Breakpoints
export const BREAKPOINTS = {
  SM: '640px',
  MD: '768px',
  LG: '1024px',
  XL: '1280px',
  '2XL': '1536px',
}

// Theme colors
export const THEME_COLORS = {
  PRIMARY: '#0f172a',
  SECONDARY: '#1e293b',
  ACCENT: '#334155',
  HIGHLIGHT: '#475569',
  NEON_BLUE: '#00d4ff',
  NEON_PURPLE: '#a855f7',
  NEON_PINK: '#ec4899',
}

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  INVALID_INPUT: 'Invalid input. Please check your data.',
  NOT_FOUND: 'The requested resource was not found.',
  GENERIC_ERROR: 'Something went wrong. Please try again.',
}

// Success messages
export const SUCCESS_MESSAGES = {
  VIDEO_GENERATED: 'Video generated successfully!',
  SCRIPT_SAVED: 'Script saved successfully!',
  VIDEO_DOWNLOADED: 'Video downloaded successfully!',
  VIDEO_DELETED: 'Video deleted successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
}

// Loading messages
export const LOADING_MESSAGES = {
  GENERATING_VIDEO: 'Generating your video...',
  ANALYZING_SCRIPT: 'Analyzing your script...',
  SAVING_CHANGES: 'Saving changes...',
  UPLOADING_FILE: 'Uploading file...',
  PROCESSING: 'Processing...',
}

// Local storage keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'userPreferences',
  RECENT_PROJECTS: 'recentProjects',
  DRAFTED_SCRIPTS: 'draftedScripts',
}

// Regex patterns
export const PATTERNS = {
  URL: /^https?:\/\/.+/,
  SCRIPT_MIN_LENGTH: 10,
  SCRIPT_MAX_LENGTH: 10000,
}
