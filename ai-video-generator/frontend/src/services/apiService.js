import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
const DEBUG_MODE = import.meta.env.VITE_DEBUG === 'true';

// Helper function to mask sensitive data
const maskSensitiveData = (data) => {
  if (!data) return data;
  const str = JSON.stringify(data);
  return str.replace(/"api_key":"[^"]*"/g, '"api_key":"***"')
            .replace(/"api_token":"[^"]*"/g, '"api_token":"***"');
};

// Helper function to get formatted timestamp
const getTimestamp = () => new Date().toISOString();

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor with logging
api.interceptors.request.use(
  (config) => {
    const startTime = Date.now();
    config.metadata = { startTime };
    
    // Log request details
    if (DEBUG_MODE) {
      console.log(`[apiService] ${getTimestamp()} - REQUEST:`, {
        method: config.method?.toUpperCase(),
        url: config.baseURL + config.url,
        headers: config.headers,
        data: maskSensitiveData(config.data),
        params: config.params
      });
    }
    
    return config;
  },
  (error) => {
    console.error(`[apiService] ${getTimestamp()} - REQUEST ERROR:`, {
      message: error.message,
      config: error.config
    });
    return Promise.reject(error);
  }
);

// Response interceptor with logging
api.interceptors.response.use(
  (response) => {
    const endTime = Date.now();
    const duration = endTime - (response.config.metadata?.startTime || endTime);
    
    // Log response details
    if (DEBUG_MODE) {
      console.log(`[apiService] ${getTimestamp()} - RESPONSE:`, {
        method: response.config.method?.toUpperCase(),
        url: response.config.url,
        status: response.status,
        statusText: response.statusText,
        duration: `${duration}ms`,
        dataSize: JSON.stringify(response.data).length
      });
    }
    
    return response;
  },
  async (error) => {
    const endTime = Date.now();
    const duration = endTime - (error.config?.metadata?.startTime || endTime);
    
    // Log error details
    console.error(`[apiService] ${getTimestamp()} - RESPONSE ERROR:`, {
      method: error.config?.method?.toUpperCase(),
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      duration: `${duration}ms`,
      message: error.message,
      data: error.response?.data
    });

    return Promise.reject(error);
  }
);

// API endpoints
export const apiEndpoints = {
  // Script generation endpoints
  generateScript: '/generate-script',
  generateSceneVariations: '/generate-scene-variations',
  enhanceVisualPrompt: '/enhance-visual-prompt',
  
  // Project endpoints
  getProjects: '/projects',
  getProject: '/projects/:id',
  createProject: '/projects',
  updateProject: '/projects/:id',
  deleteProject: '/projects/:id',
  
  // Video endpoints
  generateVideo: '/video-rendering/generate',
  getVideoStatus: '/video-rendering/status/:id',
  downloadVideo: '/video-rendering/download/:id',
  
  // Storage endpoints
  uploadFile: '/storage/upload',
  getFile: '/storage/file/:id',
  deleteFile: '/storage/file/:id',
};

// API methods
export const apiService = {
  // Script generation methods
  generateScript: (scriptData) => api.post(apiEndpoints.generateScript, scriptData),
  generateSceneVariations: (sceneData) => api.post(apiEndpoints.generateSceneVariations, sceneData),
  enhanceVisualPrompt: (promptData) => api.post(apiEndpoints.enhanceVisualPrompt, promptData),
  
  // Project methods
  getProjects: () => api.get(apiEndpoints.getProjects),
  getProject: (id) => api.get(apiEndpoints.getProject.replace(':id', id)),
  createProject: (projectData) => api.post(apiEndpoints.createProject, projectData),
  updateProject: (id, projectData) => api.put(apiEndpoints.updateProject.replace(':id', id), projectData),
  deleteProject: (id) => api.delete(apiEndpoints.deleteProject.replace(':id', id)),
  
  // Video methods
  generateVideo: (videoData) => api.post(apiEndpoints.generateVideo, videoData),
  getVideoStatus: (id) => api.get(apiEndpoints.getVideoStatus.replace(':id', id)),
  downloadVideo: (id) => api.get(apiEndpoints.downloadVideo.replace(':id', id), { responseType: 'blob' }),
  
  // Storage methods
  uploadFile: (formData) => api.post(apiEndpoints.uploadFile, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getFile: (id) => api.get(apiEndpoints.getFile.replace(':id', id)),
  deleteFile: (id) => api.delete(apiEndpoints.deleteFile.replace(':id', id)),
};

export default apiService;
