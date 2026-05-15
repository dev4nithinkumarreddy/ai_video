import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const DEBUG_MODE = import.meta.env.VITE_DEBUG === 'true'

// Helper function to mask sensitive data
const maskSensitiveData = (data) => {
  if (!data) return data
  const str = JSON.stringify(data)
  return str.replace(/"password":"[^"]*"/g, '"password":"***"')
            .replace(/"token":"[^"]*"/g, '"token":"***"')
            .replace(/"api_key":"[^"]*"/g, '"api_key":"***"')
            .replace(/"api_token":"[^"]*"/g, '"api_token":"***"')
}

// Helper function to get formatted timestamp
const getTimestamp = () => new Date().toISOString()

// Create centralized axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor with token injection and debugging
api.interceptors.request.use(
  (config) => {
    const startTime = Date.now()
    config.metadata = { startTime }
    
    // Log request for debugging
    if (DEBUG_MODE) {
      console.log(`[API] ${getTimestamp()} - REQUEST:`, {
        method: config.method?.toUpperCase(),
        url: config.baseURL + config.url,
        headers: {
          ...config.headers,
          Authorization: config.headers.Authorization ? 'Bearer ***' : undefined
        },
        data: maskSensitiveData(config.data),
        params: config.params
      })
    }
    
    return config
  },
  (error) => {
    console.error(`[API] ${getTimestamp()} - REQUEST ERROR:`, {
      message: error.message,
      config: error.config
    })
    return Promise.reject(error)
  }
)

// Response interceptor with error normalization and debugging
api.interceptors.response.use(
  (response) => {
    const endTime = Date.now()
    const duration = endTime - (response.config.metadata?.startTime || endTime)
    
    // Log response for debugging
    if (DEBUG_MODE) {
      console.log(`[API] ${getTimestamp()} - RESPONSE:`, {
        method: response.config.method?.toUpperCase(),
        url: response.config.url,
        status: response.status,
        statusText: response.statusText,
        duration: `${duration}ms`,
        dataSize: JSON.stringify(response.data).length
      })
    }
    
    return response
  },
  (error) => {
    const endTime = Date.now()
    const duration = endTime - (error.config?.metadata?.startTime || endTime)
    
    // Log response error for debugging
    console.error(`[API] ${getTimestamp()} - RESPONSE ERROR:`, {
      method: error.config?.method?.toUpperCase(),
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      duration: `${duration}ms`,
      message: error.message,
      data: error.response?.data
    })
    

    
    // Handle network errors
    if (!error.response && error.request) {
      console.error(`[API] ${getTimestamp()} - NETWORK ERROR: No response received from server`)
    }
    
    // Normalize error for consistent handling
    const normalizedError = {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message || 'An error occurred',
      data: error.response?.data,
      url: error.config?.url
    }
    
    return Promise.reject(normalizedError)
  }
)

// ============================================================================
// VIDEO API
// ============================================================================
export const videoAPI = {
  // Create video request
  createVideo: (videoData) => api.post('/videos/', videoData),
  
  // Get video details by ID
  getVideo: (videoId) => api.get(`/videos/${videoId}`),
  
  // Get video processing status
  getVideoStatus: (videoId) => api.get(`/videos/${videoId}/status`),
  
  // List videos with pagination and filtering
  listVideos: (params = {}) => api.get('/videos/', { params }),
  
  // Download video file
  downloadVideo: (videoId, quality = 'HD') => 
    api.get(`/videos/${videoId}/download`, { 
      params: { quality },
      responseType: 'blob' 
    }),
  
  // Delete video
  deleteVideo: (videoId) => api.delete(`/videos/${videoId}`),
  
  // Get video statistics
  getVideoStats: () => api.get('/videos/stats'),
  
  // Retry failed video processing
  retryVideo: (videoId) => api.post(`/videos/${videoId}/retry`),
}

// ============================================================================
// SCRIPT API
// ============================================================================
export const scriptAPI = {
  // Analyze script
  analyzeScript: (script) => api.post('/scripts/analyze', { script }),
  
  // Get AI-powered suggestions
  getScriptSuggestions: (script) => api.post('/scripts/suggestions', { script }),
  
  // Save script
  saveScript: (scriptData) => api.post('/scripts/', scriptData),
  
  // List saved scripts with pagination
  listScripts: (params = {}) => api.get('/scripts/', { params }),
  
  // Get script by ID
  getScript: (scriptId) => api.get(`/scripts/${scriptId}`),
  
  // Update script
  updateScript: (scriptId, scriptData) => api.put(`/scripts/${scriptId}`, scriptData),
  
  // Delete script
  deleteScript: (scriptId) => api.delete(`/scripts/${scriptId}`),
  
  // Get script templates
  getScriptTemplates: () => api.get('/scripts/templates'),
  
  // Generate script from template
  generateFromTemplate: (templateId, scriptData) => 
    api.post(`/scripts/templates/${templateId}/generate`, scriptData),
}

// ============================================================================
// SCRIPT GENERATION API
// ============================================================================
export const scriptGenerationAPI = {
  // Generate complete video script
  generateScript: (scriptData) => api.post('/generate-script', scriptData),
  
  // Generate variations for a specific scene
  generateSceneVariations: (sceneData) => api.post('/generate-scene-variations', sceneData),
  
  // Enhance visual prompt
  enhanceVisualPrompt: (promptData) => api.post('/enhance-visual-prompt', promptData),
  
  // Health check
  healthCheck: () => api.get('/script-generation/health'),
}

// ============================================================================
// TEMPLATE API
// ============================================================================
export const templateAPI = {
  // List templates with pagination and filtering
  listTemplates: (params = {}) => api.get('/templates/', { params }),
  
  // Get template by ID
  getTemplate: (templateId) => api.get(`/templates/${templateId}`),
  
  // Create new template
  createTemplate: (templateData) => api.post('/templates/', templateData),
  
  // Update template
  updateTemplate: (templateId, templateData) => 
    api.put(`/templates/${templateId}`, templateData),
  
  // Delete template
  deleteTemplate: (templateId) => api.delete(`/templates/${templateId}`),
  
  // Get available template categories
  getCategories: () => api.get('/templates/categories'),
  
  // Get template usage statistics
  getUsageStats: (templateId) => api.get(`/templates/${templateId}/usage`),
  
  // Rate template
  rateTemplate: (templateId, rating) => 
    api.post(`/templates/${templateId}/rate`, { rating }),
  
  // Get popular templates
  getPopular: () => api.get('/templates/popular'),
}

// ============================================================================
// AUDIO API
// ============================================================================
export const audioAPI = {
  // Generate audio from text
  generateAudio: (audioData) => api.post('/audio/generate-audio', audioData),
  
  // Generate audio with custom voice settings
  generateAudioWithSettings: (audioData) => 
    api.post('/audio/generate-audio-with-settings', audioData),
  
  // Batch generate audio for multiple scenes
  generateSceneAudio: (scenesData) => 
    api.post('/audio/generate-scene-audio', scenesData),
  
  // Asynchronously generate audio for scenes with progress tracking
  generateAudioScenes: (scenesData) => 
    api.post('/audio/generate-audio-scenes', scenesData),
  
  // Get progress of audio generation job
  getAudioGenerationProgress: (generationId) => 
    api.get(`/audio/generate-audio-scenes/${generationId}`),
  
  // Get available ElevenLabs voices
  getVoices: () => api.get('/audio/voices'),
  
  // Serve generated audio file
  getAudioFile: (filename) => api.get(`/audio/audio/${filename}`, { responseType: 'blob' }),
  
  // Delete audio files
  deleteAudio: (filenames) => api.delete('/audio/audio', { data: { filenames } }),
  
  // Cleanup old audio files
  cleanupAudio: () => api.post('/audio/cleanup'),
  
  // Health check
  healthCheck: () => api.get('/audio/health'),
}

// ============================================================================
// IMAGE API
// ============================================================================
export const imageAPI = {
  // Generate a single image
  generateImage: (imageData) => api.post('/images/generate-image', imageData),
  
  // Batch generate images for multiple scenes
  generateSceneImages: (scenesData) => 
    api.post('/images/generate-scene-images', scenesData),
  
  // Asynchronously generate images for scenes with progress tracking
  generateSceneImagesAsync: (scenesData) => 
    api.post('/images/generate-scene-images-async', scenesData),
  
  // Get progress of image generation job
  getImageGenerationProgress: (generationId) => 
    api.get(`/images/generate-scene-images-async/${generationId}`),
  
  // Queue image generation jobs
  queueImageGeneration: (jobData) => api.post('/images/generate-images', jobData),
  
  // Get progress of queued image job
  getQueuedImageProgress: (jobId) => 
    api.get(`/images/generate-images/${jobId}`),
  
  // Serve generated image file
  getImageFile: (filename) => api.get(`/images/image/${filename}`, { responseType: 'blob' }),
  
  // Delete image files
  deleteImage: (filenames) => api.delete('/images/image', { data: { filenames } }),
  
  // Cleanup old image files
  cleanupImages: () => api.post('/images/cleanup'),
  
  // Health check
  healthCheck: () => api.get('/images/health'),
}

// ============================================================================
// VIDEO RENDERING API
// ============================================================================
export const videoRenderingAPI = {
  // Render a complete video synchronously
  renderVideo: (renderData) => api.post('/video-rendering/render-video', renderData),
  
  // Asynchronously render videos with progress tracking
  renderVideoAsync: (renderData) => 
    api.post('/video-rendering/render-video-async', renderData),
  
  // Get progress of async video rendering job
  getRenderingProgress: (jobId) => 
    api.get(`/video-rendering/render-video-async/${jobId}`),
  
  // Queue video generation jobs
  queueVideoGeneration: (jobData) => api.post('/video-rendering/generate-video', jobData),
  
  // Get progress of queued video job
  getQueuedVideoProgress: (jobId) => 
    api.get(`/video-rendering/generate-video/${jobId}`),
  
  // Serve rendered video file
  getVideoFile: (filename) => api.get(`/video-rendering/video/${filename}`, { responseType: 'blob' }),
  
  // Get video information
  getVideoInfo: (filename) => api.get(`/video-rendering/video/${filename}/info`),
  
  // Delete video files
  deleteVideo: (filenames) => api.delete('/video-rendering/video', { data: { filenames } }),
  
  // Cleanup old video files
  cleanupVideos: () => api.post('/video-rendering/cleanup'),
  
  // Health check
  healthCheck: () => api.get('/video-rendering/health'),
}

// ============================================================================
// STORAGE API
// ============================================================================
export const storageAPI = {
  // Upload video file
  uploadVideo: (formData) => api.post('/storage/upload/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  // Upload image file
  uploadImage: (formData) => api.post('/storage/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  // Upload audio file
  uploadAudio: (formData) => api.post('/storage/upload/audio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  // Get file content
  getFile: (filePath) => api.get(`/storage/file/${filePath}`),
  
  // Delete file
  deleteFile: (filePath) => api.delete(`/storage/file/${filePath}`),
  
  // Get file information
  getFileInfo: (filePath) => api.get(`/storage/file/${filePath}/info`),
  
  // List all files for a project
  listProjectFiles: (projectId) => api.get(`/storage/project/${projectId}/files`),
  
  // Cleanup old files
  cleanupFiles: () => api.post('/storage/cleanup'),
  
  // Get storage statistics
  getStorageStats: () => api.get('/storage/stats'),
  
  // Get public URL for a file
  getFileUrl: (filePath) => api.get(`/storage/url/${filePath}`),
}

// ============================================================================
// HEALTH API
// ============================================================================
export const healthAPI = {
  // General health check
  getHealth: () => api.get('/health'),
  
  // Readiness check
  getReadiness: () => api.get('/health/ready'),
  
  // Liveness check
  getLiveness: () => api.get('/health/live'),
  
  // Version check
  getVersion: () => api.get('/health/version'),
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================
export const apiHelpers = {
  // Build query string from params object
  buildQueryString: (params) => {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        query.append(key, value)
      }
    })
    return query.toString()
  },
  
  // Handle API errors consistently
  handleApiError: (error) => {
    if (error.status) {
      // Normalized error from interceptor
      return error
    }
    // Raw axios error
    return {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message || 'An error occurred',
      data: error.response?.data,
      url: error.config?.url
    }
  },
  
  // Check if error is a network error
  isNetworkError: (error) => {
    return !error.response && error.request
  },
  
  // Check if error is a timeout
  isTimeoutError: (error) => {
    return error.code === 'ECONNABORTED' || error.message.includes('timeout')
  }
}

export default api
