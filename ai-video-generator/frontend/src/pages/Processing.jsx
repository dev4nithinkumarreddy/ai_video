import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import ProgressTracker from '../components/ProgressTracker'
import websocketService from '../services/websocketService'

const Processing = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { jobId, videoId } = location.state || {}
  
  const [isComplete, setIsComplete] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!jobId && !videoId) {
      navigate('/')
      return
    }

    // Connect to WebSocket if not connected
    if (!websocketService.isConnected()) {
      websocketService.connect()
    }

    // Check connection status
    const checkConnection = () => {
      setIsConnected(websocketService.isConnected())
    }

    const interval = setInterval(checkConnection, 1000)
    checkConnection()

    return () => clearInterval(interval)
  }, [jobId, videoId, navigate])

  const handleJobComplete = (data) => {
    setIsComplete(true)
    setTimeout(() => {
      navigate('/result', { state: { videoId: data.video_url || videoId } })
    }, 2000)
  }

  const handleJobFailed = (data) => {
    setHasError(true)
    setErrorMessage(data.error || 'Video generation failed')
  }

  const handleRetry = () => {
    setHasError(false)
    setErrorMessage('')
    setIsComplete(false)
    // Navigate back to script preview to retry
    navigate('/script-preview')
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen bg-gradient-to-br from-dark-primary via-dark-secondary to-dark-accent flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-4xl"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            className="w-20 h-20 mx-auto bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center mb-4"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          >
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </motion.div>
          <h1 className="text-4xl font-bold text-gray-200 mb-2">Creating Your Video</h1>
          <p className="text-gray-400">
            {!isConnected ? 'Connecting to progress server...' : 'Tracking real-time progress...'}
          </p>
        </div>

        {/* Progress Tracker */}
        <AnimatePresence>
          {!hasError && !isComplete && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ProgressTracker
                jobId={jobId}
                onJobComplete={handleJobComplete}
                onJobFailed={handleJobFailed}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error State */}
        <AnimatePresence>
          {hasError && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="glass-effect rounded-xl p-8 text-center space-y-6"
            >
              <div className="w-16 h-16 mx-auto bg-red-500/20 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-red-400">Generation Failed</h2>
                <p className="text-gray-400">{errorMessage}</p>
              </div>
              <div className="flex justify-center space-x-4">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleRetry}
                  className="px-6 py-3 bg-neon-blue text-black rounded-lg font-medium hover:bg-neon-blue/80 transition-colors"
                >
                  Try Again
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/')}
                  className="px-6 py-3 bg-dark-accent text-gray-300 rounded-lg font-medium hover:bg-dark-highlight transition-colors"
                >
                  Go Home
                </motion.button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  )
}

export default Processing
