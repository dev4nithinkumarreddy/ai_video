import { motion } from 'framer-motion'

const LoadingSpinner = ({ size = 'md', text = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-20 h-20'
  }

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className={`relative ${sizeClasses[size]}`}>
        <motion.div
          className={`absolute inset-0 rounded-full border-2 border-gray-700`}
        />
        <motion.div
          className={`absolute inset-0 rounded-full border-2 border-transparent border-t-neon-blue border-r-neon-purple`}
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        />
        <motion.div
          className={`absolute inset-2 rounded-full border-2 border-transparent border-t-neon-pink border-r-neon-blue`}
          animate={{ rotate: -360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        />
      </div>
      {text && (
        <motion.p
          className="text-gray-400 text-sm font-medium"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {text}
        </motion.p>
      )}
    </div>
  )
}

export default LoadingSpinner
