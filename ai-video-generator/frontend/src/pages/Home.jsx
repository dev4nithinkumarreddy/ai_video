import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { scriptGenerationAPI } from '../utils/api'

const Home = () => {
  const navigate = useNavigate()
  const [topic, setTopic] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})
  const [isFocused, setIsFocused] = useState(false)

  const MAX_CHARS = 5000

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

  const validateInputs = () => {
    const newErrors = {}
    
    if (!topic.trim()) {
      newErrors.topic = 'Topic is required'
    } else if (topic.length < 3) {
      newErrors.topic = 'Topic must be at least 3 characters'
    }
    
    if (!description.trim()) {
      newErrors.description = 'Description is required'
    } else if (description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleGenerateScript = async () => {
    if (!validateInputs()) return

    setLoading(true)
    setErrors({})

    try {
      console.log('[Home] Generating script for topic:', topic)
      console.log('[Home] Script description length:', description.length)
      
      const response = await scriptGenerationAPI.generateScript({
        topic,
        description,
        num_scenes: 3,
        style: 'professional'
      })
      console.log('[Home] Script generation response:', response.data)

      const scriptData = {
        topic,
        description,
        generatedScript: response.data
      }

      navigate('/script-preview', { state: scriptData })
    } catch (error) {
      console.error('[Home] Failed to generate script:', error)
      console.error('[Home] Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      setErrors({ 
        submit: error.response?.data?.detail || 'Failed to generate script. Please try again.' 
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleGenerateScript()
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen relative overflow-hidden"
    >
      {/* Animated Gradient Background */}
      <motion.div
        className="absolute inset-0 -z-10"
        animate={{
          background: [
            'radial-gradient(circle at 0% 0%, rgba(0, 212, 255, 0.15) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(168, 85, 247, 0.15) 0%, transparent 50%)',
            'radial-gradient(circle at 100% 0%, rgba(236, 72, 153, 0.15) 0%, transparent 50%), radial-gradient(circle at 0% 100%, rgba(0, 212, 255, 0.15) 0%, transparent 50%)',
            'radial-gradient(circle at 0% 0%, rgba(168, 85, 247, 0.15) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(236, 72, 153, 0.15) 0%, transparent 50%)'
          ]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          repeatType: 'reverse'
        }}
      />
      
      <div className="max-w-4xl mx-auto space-y-12 py-8">
        {/* Hero Section */}
        <motion.div variants={itemVariants} className="text-center space-y-6">
          <motion.h1 
            className="text-5xl md:text-7xl font-bold"
            animate={{ 
              textShadow: [
                '0 0 20px rgba(0, 212, 255, 0.3)',
                '0 0 40px rgba(168, 85, 247, 0.3)',
                '0 0 20px rgba(0, 212, 255, 0.3)'
              ]
            }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <span className="bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent">
              AI Video Generator
            </span>
          </motion.h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Transform your ideas into stunning videos with the power of artificial intelligence.
            Create professional content in seconds, not hours.
          </p>
        </motion.div>

        {/* Main Input Card */}
        <motion.div 
          variants={itemVariants}
          whileHover={{ scale: 1.01 }}
          className="glass-effect rounded-2xl p-8 space-y-6 backdrop-blur-xl border border-gray-700/50"
        >
          <div className="space-y-6">
            {/* Topic Input */}
            <div className="space-y-2">
              <label className="block text-lg font-semibold text-gray-200">
                Topic
              </label>
              <motion.input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Enter your video topic..."
                className={`w-full px-4 py-3 bg-dark-accent/50 border rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 transition-all ${
                  errors.topic ? 'border-red-500 focus:ring-red-500/20' : 'border-gray-700 focus:border-neon-blue focus:ring-neon-blue/20'
                }`}
                whileFocus={{ scale: 1.01 }}
              />
              <AnimatePresence>
                {errors.topic && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="text-red-400 text-sm"
                  >
                    {errors.topic}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>

            {/* Description Textarea */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="block text-lg font-semibold text-gray-200">
                  Description
                </label>
                <motion.span 
                  className={`text-sm ${
                    description.length > MAX_CHARS * 0.9 ? 'text-red-400' : 'text-gray-400'
                  }`}
                  animate={{ scale: description.length > MAX_CHARS * 0.9 ? [1, 1.1, 1] : 1 }}
                  transition={{ duration: 0.3 }}
                >
                  {description.length} / {MAX_CHARS}
                </motion.span>
              </div>
              <motion.textarea
                value={description}
                onChange={(e) => {
                  if (e.target.value.length <= MAX_CHARS) {
                    setDescription(e.target.value)
                  }
                }}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                onKeyDown={handleKeyPress}
                placeholder="Describe your video idea in detail..."
                className={`w-full h-48 px-4 py-3 bg-dark-accent/50 border rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 transition-all resize-none ${
                  errors.description ? 'border-red-500 focus:ring-red-500/20' : 'border-gray-700 focus:border-neon-blue focus:ring-neon-blue/20'
                }`}
                whileFocus={{ scale: 1.01 }}
              />
              <AnimatePresence>
                {errors.description && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="text-red-400 text-sm"
                  >
                    {errors.description}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>

            {/* Submit Error */}
            <AnimatePresence>
              {errors.submit && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm"
                >
                  {errors.submit}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Generate Button */}
            <motion.button
              onClick={handleGenerateScript}
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full btn-primary relative overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <AnimatePresence mode="wait">
                {loading ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center justify-center space-x-2"
                  >
                    <motion.div
                      className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                    <span>Generating Script...</span>
                  </motion.div>
                ) : (
                  <motion.span
                    key="generate"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    Generate Script
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>

            {/* Hint */}
            <p className="text-gray-500 text-sm text-center">
              Press Ctrl + Enter to generate quickly
            </p>
          </div>
        </motion.div>

        {/* Features Grid */}
        <motion.div variants={itemVariants} className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: '⚡',
              title: 'Lightning Fast',
              description: 'Generate videos in seconds with our optimized AI pipeline'
            },
            {
              icon: '🎨',
              title: 'Beautiful Templates',
              description: 'Choose from dozens of professional video templates'
            },
            {
              icon: '🎯',
              title: 'Smart Editing',
              description: 'AI-powered editing that understands your content'
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              whileHover={{ scale: 1.05, y: -5 }}
              className="glass-effect rounded-xl p-6 text-center space-y-4 cursor-pointer backdrop-blur-lg border border-gray-700/30"
            >
              <motion.div 
                className="text-4xl"
                whileHover={{ rotate: [0, -10, 10, 0] }}
                transition={{ duration: 0.5 }}
              >
                {feature.icon}
              </motion.div>
              <h3 className="text-xl font-semibold text-gray-200">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
  )
}

export default Home
