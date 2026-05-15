import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import ProgressBar from './ProgressBar'
import websocketService from '../services/websocketService'

const ProgressTracker = ({ jobId, onJobComplete, onJobFailed }) => {
  const [jobData, setJobData] = useState({
    scriptProgress: { progress: 0, status: 'queued', currentStep: '', totalSteps: 0 },
    audioProgress: { progress: 0, status: 'queued', currentStep: '', totalSteps: 0 },
    imageProgress: { progress: 0, status: 'queued', currentStep: '', totalSteps: 0 },
    videoProgress: { progress: 0, status: 'queued', currentStep: '', totalSteps: 0 }
  })
  
  const [overallProgress, setOverallProgress] = useState(0)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!jobId) return

    // Connect to WebSocket if not connected
    if (!websocketService.isConnected()) {
      websocketService.connect()
    }

    // Subscribe to job updates
    websocketService.subscribeToJob(jobId)

    // Set up event listeners
    const handleConnectionChange = (data) => {
      setIsConnected(data.type === 'connected')
    }

    const handleScriptProgress = (data) => {
      setJobData(prev => ({
        ...prev,
        scriptProgress: {
          progress: data.data.progress_percentage || 0,
          status: data.data.status || 'processing',
          currentStep: data.data.current_step || '',
          totalSteps: data.data.total_steps || 0
        }
      }))
    }

    const handleAudioProgress = (data) => {
      setJobData(prev => ({
        ...prev,
        audioProgress: {
          progress: data.data.progress_percentage || 0,
          status: data.data.status || 'processing',
          currentStep: data.data.current_step || '',
          totalSteps: data.data.total_steps || 0
        }
      }))
    }

    const handleImageProgress = (data) => {
      setJobData(prev => ({
        ...prev,
        imageProgress: {
          progress: data.data.progress_percentage || 0,
          status: data.data.status || 'processing',
          currentStep: data.data.current_step || '',
          totalSteps: data.data.total_steps || 0
        }
      }))
    }

    const handleVideoProgress = (data) => {
      setJobData(prev => ({
        ...prev,
        videoProgress: {
          progress: data.data.progress_percentage || 0,
          status: data.data.status || 'processing',
          currentStep: data.data.current_step || '',
          totalSteps: data.data.total_steps || 0
        }
      }))
    }

    const handleJobCompleted = (data) => {
      setOverallProgress(100)
      onJobComplete?.(data.data)
    }

    const handleJobFailed = (data) => {
      onJobFailed?.(data.data)
    }

    // Register event listeners
    websocketService.on('connected', handleConnectionChange)
    websocketService.on('disconnected', handleConnectionChange)
    websocketService.on('script_progress', handleScriptProgress)
    websocketService.on('audio_progress', handleAudioProgress)
    websocketService.on('image_progress', handleImageProgress)
    websocketService.on('video_progress', handleVideoProgress)
    websocketService.on('job_completed', handleJobCompleted)
    websocketService.on('job_failed', handleJobFailed)

    // Cleanup
    return () => {
      websocketService.off('connected', handleConnectionChange)
      websocketService.off('disconnected', handleConnectionChange)
      websocketService.off('script_progress', handleScriptProgress)
      websocketService.off('audio_progress', handleAudioProgress)
      websocketService.off('image_progress', handleImageProgress)
      websocketService.off('video_progress', handleVideoProgress)
      websocketService.off('job_completed', handleJobCompleted)
      websocketService.off('job_failed', handleJobFailed)
      
      if (jobId) {
        websocketService.unsubscribeFromJob(jobId)
      }
    }
  }, [jobId, onJobComplete, onJobFailed])

  // Calculate overall progress
  useEffect(() => {
    const { scriptProgress, audioProgress, imageProgress, videoProgress } = jobData
    const totalProgress = (
      scriptProgress.progress +
      audioProgress.progress +
      imageProgress.progress +
      videoProgress.progress
    ) / 4
    setOverallProgress(totalProgress)
  }, [jobData])

  const progressSteps = [
    {
      key: 'script',
      title: 'Script Generation',
      icon: '📝',
      color: 'blue',
      data: jobData.scriptProgress
    },
    {
      key: 'audio',
      title: 'Audio Generation',
      icon: '🎵',
      color: 'purple',
      data: jobData.audioProgress
    },
    {
      key: 'image',
      title: 'Image Generation',
      icon: '🎨',
      color: 'pink',
      data: jobData.imageProgress
    },
    {
      key: 'video',
      title: 'Video Rendering',
      icon: '🎬',
      color: 'green',
      data: jobData.videoProgress
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-gray-200">Video Generation Progress</h3>
        
        {/* Connection Status */}
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          <span className="text-sm text-gray-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Overall Progress */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-300">Overall Progress</span>
          <span className="text-sm font-bold text-neon-blue">
            {Math.round(overallProgress)}%
          </span>
        </div>
        <ProgressBar
          progress={overallProgress}
          status={overallProgress === 100 ? 'completed' : 'processing'}
          color="blue"
          size="large"
          showPercentage={false}
        />
      </div>

      {/* Individual Progress Steps */}
      <div className="space-y-4">
        {progressSteps.map((step, index) => (
          <motion.div
            key={step.key}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="space-y-2"
          >
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{step.icon}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-300">{step.title}</h4>
                  <span className="text-xs text-gray-400">
                    {step.data.currentStep}
                  </span>
                </div>
                <ProgressBar
                  progress={step.data.progress}
                  status={step.data.status}
                  color={step.color}
                  size="small"
                  showPercentage={false}
                  showStatus={false}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Status Messages */}
      <AnimatePresence>
        {jobData.scriptProgress.status === 'failed' && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-red-500/10 border border-red-500/50 rounded-lg p-3"
          >
            <p className="text-sm text-red-400">Script generation failed</p>
          </motion.div>
        )}
        
        {jobData.audioProgress.status === 'failed' && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-red-500/10 border border-red-500/50 rounded-lg p-3"
          >
            <p className="text-sm text-red-400">Audio generation failed</p>
          </motion.div>
        )}
        
        {jobData.imageProgress.status === 'failed' && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-red-500/10 border border-red-500/50 rounded-lg p-3"
          >
            <p className="text-sm text-red-400">Image generation failed</p>
          </motion.div>
        )}
        
        {jobData.videoProgress.status === 'failed' && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-red-500/10 border border-red-500/50 rounded-lg p-3"
          >
            <p className="text-sm text-red-400">Video rendering failed</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default ProgressTracker
