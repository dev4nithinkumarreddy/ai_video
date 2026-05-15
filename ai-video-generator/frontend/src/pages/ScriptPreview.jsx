import { motion, AnimatePresence } from 'framer-motion'
import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { SceneProvider, useScene } from '../contexts/SceneContext'
import apiService from '../services/apiService'

const ScriptPreviewContent = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { topic, description, analysis, suggestions } = location.state || {}
  
  const {
    scenes,
    loading,
    error,
    hasChanges,
    initializeScenes,
    updateScene,
    updateSceneFields,
    addScene,
    deleteScene,
    regenerateScene,
    saveScenes,
    toggleEditScene
  } = useScene()
  
  const [generatingVideo, setGeneratingVideo] = useState(false)
  const [videoProgress, setVideoProgress] = useState(0)
  const [saving, setSaving] = useState(false)
  const [generatingSceneId, setGeneratingSceneId] = useState(null)

  // Initialize scenes on mount
  useEffect(() => {
    const initialScenes = location.state?.scenes || [
      {
        id: 1,
        number: 1,
        narration: 'Welcome to our groundbreaking product that will revolutionize the way you work and live.',
        visualPrompt: 'Modern office setting with futuristic technology, bright lighting, professional atmosphere',
        duration: 5,
        isEditing: false
      },
      {
        id: 2,
        number: 2,
        narration: 'Imagine having all your tasks automated, giving you more time to focus on what truly matters.',
        visualPrompt: 'Person working relaxed on a laptop, clean minimalist workspace, warm ambient light',
        duration: 7,
        isEditing: false
      },
      {
        id: 3,
        number: 3,
        narration: 'Our AI-powered solution learns from your habits and adapts to your unique workflow.',
        visualPrompt: 'Abstract AI visualization with neural network patterns, blue and purple gradient background',
        duration: 6,
        isEditing: false
      }
    ]
    initializeScenes(initialScenes)
  }, [location.state?.scenes, initializeScenes])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  }

  const handleRegenerateScene = async (sceneId) => {
    setGeneratingSceneId(sceneId)
    try {
      await regenerateScene(sceneId)
    } finally {
      setGeneratingSceneId(null)
    }
  }

  const handleSaveChanges = async () => {
    setSaving(true)
    try {
      await saveScenes()
    } finally {
      setSaving(false)
    }
  }

  const handleGenerateVideo = async () => {
    setGeneratingVideo(true)
    setVideoProgress(0)
    
    try {
      console.log('[ScriptPreview] Generating video with scenes:', scenes.length)
      
      // Save any pending changes first
      if (hasChanges) {
        await handleSaveChanges()
      }
      
      const videoData = {
        script: description || topic,
        scenes: scenes,
        quality: 'HD',
        format: 'MP4'
      }
      
      console.log('[ScriptPreview] Calling API to generate video:', videoData)
      const response = await apiService.generateVideo(videoData)
      console.log('[ScriptPreview] Video generation initiated:', response.data)
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        setVideoProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval)
            return 100
          }
          return prev + 10
        })
      }, 500)
      
      setTimeout(() => {
        clearInterval(progressInterval)
        navigate('/processing', { state: { videoId: response.data.id } })
      }, 5000)
      
    } catch (error) {
      console.error('[ScriptPreview] Failed to generate video:', error)
      console.error('[ScriptPreview] Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      setGeneratingVideo(false)
    }
  }

  const totalDuration = scenes.reduce((sum, scene) => sum + scene.duration, 0)

  return (
    <>
      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-400 mb-6"
        >
          {error}
        </motion.div>
      )}

      {/* Unsaved Changes Banner */}
      <AnimatePresence>
        {hasChanges && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-4 mb-6 flex items-center justify-between"
          >
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
              <span className="text-yellow-400">You have unsaved changes</span>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSaveChanges}
              disabled={saving}
              className="px-4 py-2 bg-yellow-500 text-black rounded-lg font-medium disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-6xl mx-auto space-y-8 py-8"
      >
      {/* Header */}
      <motion.div variants={itemVariants} className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold">
          <span className="bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent">
            Script Preview
          </span>
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Review and edit your scenes before generating the video
        </p>
      </motion.div>

      {/* Stats Overview */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-effect rounded-lg p-4 text-center backdrop-blur-lg">
          <div className="text-2xl font-bold text-neon-blue">{scenes.length}</div>
          <div className="text-sm text-gray-400">Scenes</div>
        </div>
        <div className="glass-effect rounded-lg p-4 text-center backdrop-blur-lg">
          <div className="text-2xl font-bold text-neon-purple">{totalDuration}s</div>
          <div className="text-sm text-gray-400">Total Duration</div>
        </div>
        <div className="glass-effect rounded-lg p-4 text-center backdrop-blur-lg">
          <div className="text-2xl font-bold text-neon-pink">HD</div>
          <div className="text-sm text-gray-400">Quality</div>
        </div>
        <div className="glass-effect rounded-lg p-4 text-center backdrop-blur-lg">
          <div className="text-2xl font-bold text-green-400">MP4</div>
          <div className="text-sm text-gray-400">Format</div>
        </div>
      </motion.div>

      {/* Topic/Description Display */}
      {topic && (
        <motion.div variants={itemVariants} className="glass-effect rounded-xl p-6 backdrop-blur-lg">
          <div className="space-y-2">
            <div className="text-sm text-gray-400 uppercase tracking-wide">Topic</div>
            <div className="text-xl font-semibold text-gray-200">{topic}</div>
          </div>
        </motion.div>
      )}

      {/* Scenes Grid */}
      <motion.div variants={itemVariants} className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-200">Generated Scenes</h2>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 bg-neon-blue/20 text-neon-blue rounded-lg hover:bg-neon-blue/30 transition-colors"
            onClick={() => addScene()}
          >
            + Add Scene
          </motion.button>
        </div>

        <div className="space-y-4">
          <AnimatePresence>
            {scenes.map((scene, index) => (
              <motion.div
                key={scene.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.3 }}
                className="glass-effect rounded-xl p-6 backdrop-blur-lg border border-gray-700/50"
              >
                <div className="space-y-4">
                  {/* Scene Header */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-neon-blue to-neon-purple rounded-lg flex items-center justify-center text-white font-bold">
                        {scene.number}
                      </div>
                      <div>
                        <div className="text-sm text-gray-400">Scene {scene.number}</div>
                        <div className="text-xs text-gray-500">{scene.duration}s duration</div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => toggleEditScene(scene.id)}
                        className="p-2 bg-dark-accent rounded-lg hover:bg-dark-highlight transition-colors"
                      >
                        <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => handleRegenerateScene(scene.id)}
                        disabled={generatingSceneId === scene.id}
                        className="p-2 bg-dark-accent rounded-lg hover:bg-dark-highlight transition-colors disabled:opacity-50"
                      >
                        {generatingSceneId === scene.id ? (
                          <motion.div
                            className="w-4 h-4 border-2 border-neon-blue border-t-transparent rounded-full"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          />
                        ) : (
                          <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        )}
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => deleteScene(scene.id)}
                        className="p-2 bg-red-500/20 rounded-lg hover:bg-red-500/30 transition-colors"
                      >
                        <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </motion.button>
                    </div>
                  </div>

                  {/* Scene Content */}
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* Narration */}
                    <div className="space-y-2">
                      <label className="text-sm font-semibold text-gray-300">Narration</label>
                      {scene.isEditing ? (
                        <textarea
                          value={scene.narration}
                          onChange={(e) => updateScene(scene.id, 'narration', e.target.value)}
                          className="w-full h-32 px-3 py-2 bg-dark-accent/50 border border-gray-700 rounded-lg text-gray-100 text-sm focus:outline-none focus:border-neon-blue resize-none"
                          placeholder="Enter narration..."
                        />
                      ) : (
                        <p className="text-gray-300 text-sm leading-relaxed">{scene.narration}</p>
                      )}
                    </div>

                    {/* Visual Prompt */}
                    <div className="space-y-2">
                      <label className="text-sm font-semibold text-gray-300">Visual Prompt</label>
                      {scene.isEditing ? (
                        <textarea
                          value={scene.visualPrompt}
                          onChange={(e) => updateScene(scene.id, 'visualPrompt', e.target.value)}
                          className="w-full h-32 px-3 py-2 bg-dark-accent/50 border border-gray-700 rounded-lg text-gray-100 text-sm focus:outline-none focus:border-neon-purple resize-none"
                          placeholder="Enter visual prompt..."
                        />
                      ) : (
                        <p className="text-gray-400 text-sm leading-relaxed italic">{scene.visualPrompt}</p>
                      )}
                    </div>
                  </div>

                  {/* Duration Slider */}
                  {scene.isEditing && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <label className="text-gray-300">Duration</label>
                        <span className="text-neon-blue">{scene.duration}s</span>
                      </div>
                      <input
                        type="range"
                        min="2"
                        max="15"
                        value={scene.duration}
                        onChange={(e) => updateScene(scene.id, 'duration', parseInt(e.target.value))}
                        className="w-full h-2 bg-dark-accent rounded-lg appearance-none cursor-pointer accent-neon-blue"
                      />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Video Generation Progress */}
      <AnimatePresence>
        {generatingVideo && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-effect rounded-xl p-6 backdrop-blur-lg"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <motion.div
                    className="w-8 h-8 border-2 border-neon-blue border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  />
                  <span className="text-gray-200 font-semibold">Generating Video...</span>
                </div>
                <span className="text-neon-blue font-bold">{videoProgress}%</span>
              </div>
              <div className="w-full bg-dark-accent rounded-full h-2 overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-neon-blue to-neon-purple rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${videoProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Action Buttons */}
      <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4 justify-center">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/')}
          className="btn-secondary"
          disabled={generatingVideo}
        >
          Back to Home
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleGenerateVideo}
          disabled={generatingVideo || scenes.length === 0}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generatingVideo ? 'Generating...' : 'Generate Video'}
        </motion.button>
      </motion.div>
    </motion.div>
    </>
  )
}

const ScriptPreview = () => (
  <SceneProvider>
    <ScriptPreviewContent />
  </SceneProvider>
)

export default ScriptPreview
