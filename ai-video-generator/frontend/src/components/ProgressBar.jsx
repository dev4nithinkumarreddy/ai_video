import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'

const ProgressBar = ({ 
  progress = 0, 
  status = 'processing',
  animated = true,
  color = 'blue',
  size = 'medium',
  showPercentage = true,
  showStatus = true,
  className = ''
}) => {
  const [displayProgress, setDisplayProgress] = useState(0)
  
  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setDisplayProgress(progress), 100)
      return () => clearTimeout(timer)
    } else {
      setDisplayProgress(progress)
    }
  }, [progress, animated])

  const colorClasses = {
    blue: 'bg-gradient-to-r from-neon-blue to-blue-500',
    green: 'bg-gradient-to-r from-green-400 to-green-500',
    purple: 'bg-gradient-to-r from-neon-purple to-purple-500',
    pink: 'bg-gradient-to-r from-pink-400 to-pink-500',
    yellow: 'bg-gradient-to-r from-yellow-400 to-yellow-500',
    red: 'bg-gradient-to-r from-red-400 to-red-500'
  }

  const sizeClasses = {
    small: 'h-2',
    medium: 'h-3',
    large: 'h-4'
  }

  const statusColors = {
    queued: 'text-yellow-400',
    processing: 'text-blue-400',
    completed: 'text-green-400',
    failed: 'text-red-400',
    cancelled: 'text-gray-400'
  }

  const statusText = {
    queued: 'Queued',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed',
    cancelled: 'Cancelled'
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Progress Bar */}
      <div className="relative">
        <div className={`w-full ${sizeClasses[size]} bg-dark-accent rounded-full overflow-hidden`}>
          <motion.div
            className={`h-full ${colorClasses[color]} rounded-full relative overflow-hidden`}
            initial={{ width: 0 }}
            animate={{ width: `${displayProgress}%` }}
            transition={{ duration: animated ? 0.5 : 0, ease: 'easeInOut' }}
          >
            {/* Animated shimmer effect */}
            {animated && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                animate={{
                  x: ['-100%', '100%']
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'linear'
                }}
              />
            )}
          </motion.div>
        </div>
        
        {/* Percentage overlay */}
        {showPercentage && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-semibold text-white drop-shadow-lg">
              {Math.round(displayProgress)}%
            </span>
          </div>
        )}
      </div>

      {/* Status */}
      {showStatus && (
        <div className="flex items-center justify-between">
          <span className={`text-sm font-medium ${statusColors[status]}`}>
            {statusText[status]}
          </span>
          
          {/* Animated status indicator */}
          <AnimatePresence>
            {status === 'processing' && (
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
                className="flex items-center space-x-1"
              >
                <motion.div
                  className="w-2 h-2 bg-blue-400 rounded-full"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [1, 0.7, 1]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: 'easeInOut'
                  }}
                />
                <motion.div
                  className="w-2 h-2 bg-blue-400 rounded-full"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [1, 0.7, 1]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: 0.2
                  }}
                />
                <motion.div
                  className="w-2 h-2 bg-blue-400 rounded-full"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [1, 0.7, 1]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: 0.4
                  }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}

export default ProgressBar
