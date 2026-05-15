import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Play, Download, Edit, Save, Clock, Eye } from 'lucide-react';
import Card from '../components/Card';

const ScriptPreview = () => {
  const [script, setScript] = useState({
    title: "AI-Generated Product Demo",
    introduction: "Welcome to our revolutionary product that will change the way you work and play.",
    scenes: [
      {
        scene_number: 1,
        narration: "Opening shot of the product in a modern office setting, with the product prominently displayed on a clean desk.",
        visual_prompt: "Professional office environment with natural lighting, product on desk, modern minimalist design",
        duration: 15,
        camera_movement: "slow pan"
      },
      {
        scene_number: 2,
        narration: "Close-up shot showing the product's key features and benefits, with smooth transitions between different aspects.",
        visual_prompt: "Sleek product photography with highlight effects on key features, clean white background",
        duration: 20,
        camera_movement: "static"
      },
      {
        scene_number: 3,
        narration: "Action shot of someone using the product in a real-world scenario, demonstrating its practical applications.",
        visual_prompt: "Realistic office or home environment with natural lighting, person interacting with product naturally",
        duration: 25,
        camera_movement: "handheld"
      }
    ],
    conclusion: "This innovative product represents the future of workplace efficiency and user experience.",
    estimated_duration: 60
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <Play className="h-5 w-5 text-white" />
                  </div>
                  <div className="ml-4">
                    <h1 className="text-2xl font-bold text-gray-900">AI Video Generator</h1>
                    <p className="text-sm text-gray-600">Script Preview</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg text-gray-600 hover:text-gray-900 transition-colors">
                <ArrowLeft className="h-5 w-5" />
                Back to Editor
              </button>
              
              <div className="flex items-center space-x-2">
                <button className="p-2 rounded-lg text-gray-600 hover:text-gray-900 transition-colors">
                  <Edit className="h-5 w-5" />
                  Edit
                </button>
                <button className="p-2 rounded-lg text-gray-600 hover:text-gray-900 transition-colors">
                  <Save className="h-5 w-5" />
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Script Info */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900">Script Details</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Duration: {script.estimated_duration}s</span>
                  <span className="text-sm text-gray-500">Style: {script.style}</span>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Title</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{script.title}</p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Introduction</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{script.introduction}</p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Conclusion</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{script.conclusion}</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Scenes */}
          <div className="lg:col-span-1">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Scenes ({script.scenes.length})</h3>
            <div className="space-y-4">
              {script.scenes.map((scene, index) => (
                <Card key={index} className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-gray-900">
                      Scene {scene.scene_number}
                    </h4>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">Duration: {scene.duration}s</span>
                      <span className="text-sm text-gray-500">Camera: {scene.camera_movement}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Narration</h5>
                      <p className="text-gray-700 whitespace-pre-wrap">{scene.narration}</p>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <h5 className="font-medium text-gray-900">Visual Prompt</h5>
                      <button className="p-1 rounded text-blue-600 hover:text-blue-700 transition-colors">
                        <Eye className="h-4 w-4" />
                      </button>
                    </div>
                    <p className="text-gray-700 text-sm mt-2 bg-gray-100 p-3 rounded">
                      {scene.visual_prompt}
                    </p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* Floating Action Buttons */}
      <div className="fixed bottom-8 right-8 flex flex-col space-y-4">
        <button className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg shadow-lg transition-colors">
          <Play className="h-5 w-5" />
          Generate Video
        </button>
        
        <button className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg shadow-lg transition-colors">
          <Download className="h-5 w-5" />
          Export Script
        </button>
      </div>
    </div>
  );
};

export default ScriptPreview;
