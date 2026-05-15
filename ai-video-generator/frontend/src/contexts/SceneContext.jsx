import { createContext, useContext, useState, useCallback } from 'react'
import apiService from '../services/apiService'
import { scriptAPI } from '../utils/api'

const SceneContext = createContext(null)

export const useScene = () => {
  const context = useContext(SceneContext)
  if (!context) {
    throw new Error('useScene must be used within a SceneProvider')
  }
  return context
}

export const SceneProvider = ({ children }) => {
  const [scenes, setScenes] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [hasChanges, setHasChanges] = useState(false)

  // Initialize scenes from data
  const initializeScenes = useCallback((initialScenes) => {
    setScenes(initialScenes)
    setHasChanges(false)
  }, [])

  // Update scene field
  const updateScene = useCallback((sceneId, field, value) => {
    setScenes(prevScenes => 
      prevScenes.map(scene => 
        scene.id === sceneId ? { ...scene, [field]: value } : scene
      )
    )
    setHasChanges(true)
  }, [])

  // Update multiple scene fields at once
  const updateSceneFields = useCallback((sceneId, updates) => {
    setScenes(prevScenes => 
      prevScenes.map(scene => 
        scene.id === sceneId ? { ...scene, ...updates } : scene
      )
    )
    setHasChanges(true)
  }, [])

  // Add new scene
  const addScene = useCallback((sceneData = {}) => {
    const newScene = {
      id: Date.now(),
      number: scenes.length + 1,
      narration: '',
      visualPrompt: '',
      duration: 5,
      cameraMovement: 'static',
      mood: 'professional',
      isEditing: true,
      ...sceneData
    }
    setScenes(prevScenes => [...prevScenes, newScene])
    setHasChanges(true)
  }, [scenes.length])

  // Delete scene
  const deleteScene = useCallback((sceneId) => {
    setScenes(prevScenes => {
      const filtered = prevScenes.filter(scene => scene.id !== sceneId)
      // Renumber scenes
      return filtered.map((scene, index) => ({ ...scene, number: index + 1 }))
    })
    setHasChanges(true)
  }, [])

  // Regenerate scene
  const regenerateScene = useCallback(async (sceneId) => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('[SceneContext] Regenerating scene:', sceneId)
      const scene = scenes.find(s => s.id === sceneId)
      if (!scene) {
        throw new Error('Scene not found')
      }

      // Call API to regenerate scene
      const response = await apiService.generateSceneVariations({
        scene: scene,
        variations: 1
      })
      console.log('[SceneContext] Scene variations response:', response.data)

      if (response.data.variations && response.data.variations.length > 0) {
        const variation = response.data.variations[0]
        updateSceneFields(sceneId, {
          narration: variation.narration,
          visualPrompt: variation.visual_prompt,
          duration: variation.duration,
          cameraMovement: variation.cameraMovement || 'static',
          mood: variation.mood || 'professional'
        })
        console.log('[SceneContext] Scene regenerated successfully')
      }
    } catch (err) {
      console.error('[SceneContext] Error regenerating scene:', err)
      console.error('[SceneContext] Error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      })
      setError(err.response?.data?.detail || 'Failed to regenerate scene')
    } finally {
      setLoading(false)
    }
  }, [scenes, updateSceneFields])

  // Save all scenes
  const saveScenes = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('[SceneContext] Saving scenes:', scenes.length)
      // Call API to save scenes
      const response = await scriptAPI.saveScript({ scenes: scenes })
      console.log('[SceneContext] Scenes saved successfully:', response.data)
      
      setHasChanges(false)
      return response.data
    } catch (err) {
      console.error('[SceneContext] Error saving scenes:', err)
      console.error('[SceneContext] Error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      })
      setError(err.response?.data?.detail || 'Failed to save scenes')
      throw err
    } finally {
      setLoading(false)
    }
  }, [scenes])

  // Reset scenes to initial state
  const resetScenes = useCallback((initialScenes) => {
    setScenes(initialScenes)
    setHasChanges(false)
    setError(null)
  }, [])

  // Toggle edit mode for a scene
  const toggleEditScene = useCallback((sceneId) => {
    setScenes(prevScenes => 
      prevScenes.map(scene => 
        scene.id === sceneId ? { ...scene, isEditing: !scene.isEditing } : scene
      )
    )
  }, [])

  const value = {
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
    resetScenes,
    toggleEditScene
  }

  return (
    <SceneContext.Provider value={value}>
      {children}
    </SceneContext.Provider>
  )
}
