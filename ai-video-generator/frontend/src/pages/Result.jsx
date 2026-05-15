import { motion, AnimatePresence } from 'framer-motion'
import { useState, useRef, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

const Result = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const videoRef = useRef(null)
  
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [selectedQuality, setSelectedQuality] = useState('HD')
  const [showControls, setShowControls] = useState(true)
  const [downloadProgress, setDownloadProgress] = useState(0)
  const [isDownloading, setIsDownloading] = useState(false)

  // Sample video data - in production, this would come from the backend
  const videoData = {
    id: location.state?.videoId || 'sample-123',
    url: 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
    title: 'AI Generated Video',
    topic: location.state?.topic || 'Product Introduction',
    createdAt: new Date().toLocaleDateString(),
    scenes: location.state?.scenes || 3,
    stats: {
      duration: '2:45',
      resolution: '1920x1080',
      fileSize: '45.2 MB',
      fps: '30',
      format: 'MP4'
    }
  }

  const qualityOptions = ['SD', 'HD', 'Full HD', '4K']

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

  // Video controls
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration)
    }
  }

  const handleSeek = (e) => {
    const time = (e.target.value / 100) * duration
    if (videoRef.current) {
      videoRef.current.currentTime = time
    }
  }

  const handleVolumeChange = (e) => {
    const newVolume = e.target.value / 100
    setVolume(newVolume)
    if (videoRef.current) {
      videoRef.current.volume = newVolume
    }
  }

  const toggleMute = () => {
    setIsMuted(!isMuted)
    if (videoRef.current) {
      videoRef.current.muted = !isMuted
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleDownload = async () => {
    setIsDownloading(true)
    setDownloadProgress(0)
    
    // Simulate download progress
    const interval = setInterval(() => {
      setDownloadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsDownloading(false)
          return 100
        }
        return prev + 5
      })
    }, 200)
    
    // In production, this would trigger actual download
    setTimeout(() => {
      clearInterval(interval)
      setIsDownloading(false)
      setDownloadProgress(0)
    }, 4000)
  }

  const handleGenerateAgain = () => {
    navigate('/')
  }

  // Auto-hide controls
  useEffect(() => {
    let timeout
    if (isPlaying) {
      timeout = setTimeout(() => setShowControls(false), 3000)
    }
    return () => clearTimeout(timeout)
  }, [isPlaying, showControls])

  const progress = (currentTime / duration) * 100 || 0

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-7xl mx-auto space-y-8 py-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="text-center space-y-4">
        <motion.h1 
          className="text-4xl md:text-5xl font-bold"
          animate={{ 
            textShadow: [
              '0 0 20px rgba(74, 222, 128, 0.3)',
              '0 0 40px rgba(59, 130, 246, 0.3)',
              '0 0 20px rgba(74, 222, 128, 0.3)'
            ]
          }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <span className="bg-gradient-to-r from-green-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
            Your Video is Ready!
          </span>
        </motion.h1>
        <p className="text-gray-400">
          Your AI-generated video has been successfully created
        </p>
      </motion.div>

      {/* Video Player Section */}
      <motion.div variants={itemVariants} className="space-y-6">
        <div 
          className="relative aspect-video bg-dark-accent rounded-2xl overflow-hidden shadow-2xl shadow-neon-blue/20"
          onMouseEnter={() => setShowControls(true)}
          onMouseLeave={() => isPlaying && setShowControls(false)}
        >
          {/* HTML5 Video Player */}
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={() => setIsPlaying(false)}
            poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1920 1080'%3E%3Crect fill='%231e293b' width='1920' height='1080'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2364748b' font-size='48'%3EAI Generated Video%3C/text%3E%3C/svg%3E"
          >
            <source src={videoData.url} type="video/mp4" />
            Your browser does not support the video tag.
          </video>

          {/* Play/Pause Overlay */}
          <AnimatePresence>
            {!isPlaying && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 flex items-center justify-center bg-black/30"
              >
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={togglePlayPause}
                  className="w-24 h-24 bg-gradient-to-r from-neon-blue to-neon-purple rounded-full flex items-center justify-center shadow-lg shadow-neon-blue/50"
                >
                  <svg className="w-12 h-12 text-white ml-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Video Controls */}
          <AnimatePresence>
            {showControls && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-6"
              >
                {/* Progress Bar */}
                <div className="mb-4">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={progress}
                    onChange={handleSeek}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-neon-blue"
                  />
                  <div className="flex justify-between text-white text-sm mt-2">
                    <span>{formatTime(currentTime)}</span>
                    <span>{formatTime(duration)}</span>
                  </div>
                </div>

                {/* Control Buttons */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={togglePlayPause}
                      className="p-2 text-white hover:text-neon-blue transition-colors"
                    >
                      {isPlaying ? (
                        <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                        </svg>
                      ) : (
                        <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      )}
                    </motion.button>

                    <div className="flex items-center space-x-2">
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={toggleMute}
                        className="p-2 text-white hover:text-neon-blue transition-colors"
                      >
                        {isMuted ? (
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
                          </svg>
                        )}
                      </motion.button>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={isMuted ? 0 : volume * 100}
                        onChange={handleVolumeChange}
                        className="w-20 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-neon-blue"
                      />
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <span className="text-white text-sm font-medium">{selectedQuality}</span>
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="p-2 text-white hover:text-neon-blue transition-colors"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z" />
                      </svg>
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Quality Selector */}
        <div className="flex items-center justify-center space-x-4">
          <span className="text-sm text-gray-400">Quality:</span>
          <div className="flex space-x-2">
            {qualityOptions.map((quality) => (
              <motion.button
                key={quality}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedQuality(quality)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedQuality === quality
                    ? 'bg-neon-blue text-white shadow-lg shadow-neon-blue/25'
                    : 'bg-dark-accent text-gray-400 hover:text-white hover:bg-dark-highlight'
                }`}
              >
                {quality}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Project Details */}
      <motion.div variants={itemVariants} className="grid md:grid-cols-2 gap-6">
        {/* Video Stats */}
        <div className="glass-effect rounded-2xl p-6 backdrop-blur-lg space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">Video Details</h3>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(videoData.stats).map(([key, value]) => (
              <div key={key} className="bg-dark-accent/30 rounded-lg p-3">
                <div className="text-xs text-gray-400 capitalize mb-1">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div className="text-lg font-bold text-neon-blue">{value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Project Info */}
        <div className="glass-effect rounded-2xl p-6 backdrop-blur-lg space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">Project Information</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-gray-700/50">
              <span className="text-gray-400">Video ID</span>
              <span className="text-gray-200 font-mono text-sm">{videoData.id}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-700/50">
              <span className="text-gray-400">Topic</span>
              <span className="text-gray-200">{videoData.topic}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-700/50">
              <span className="text-gray-400">Scenes</span>
              <span className="text-gray-200">{videoData.scenes}</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-400">Created</span>
              <span className="text-gray-200">{videoData.createdAt}</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div variants={itemVariants} className="grid md:grid-cols-2 gap-4">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleDownload}
          disabled={isDownloading}
          className="btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isDownloading ? (
            <>
              <motion.div
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
              <span>Downloading... {downloadProgress}%</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Download Video</span>
            </>
          )}
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleGenerateAgain}
          className="btn-secondary flex items-center justify-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Generate Again</span>
        </motion.button>
      </motion.div>

      {/* Download Progress */}
      <AnimatePresence>
        {isDownloading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-effect rounded-xl p-4 backdrop-blur-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-200 font-medium">Downloading Video...</span>
              <span className="text-neon-blue font-bold">{downloadProgress}%</span>
            </div>
            <div className="w-full bg-dark-accent rounded-full h-2 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-neon-blue to-neon-purple rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${downloadProgress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default Result
