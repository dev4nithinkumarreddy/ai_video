import React from 'react';
import { motion } from 'framer-motion';
import { Download, Share2, Play, ArrowLeft, CheckCircle, Star } from 'lucide-react';
import Card from '../components/Card';

const ResultModern = () => {
  const [video, setVideo] = useState({
    url: '',
    title: 'AI-Generated Product Demo',
    description: 'A stunning product demonstration video created entirely with AI technology',
    thumbnail: '',
    duration: 60,
    format: 'mp4'
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
                    <p className="text-sm text-gray-600">Your video is ready!</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg text-gray-600 hover:text-gray-900 transition-colors">
                <ArrowLeft className="h-5 w-5" />
                Back to Editor
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Video Preview */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <div className="aspect-w-16 bg-black rounded-lg overflow-hidden">
                {video.url ? (
                  <video 
                    className="w-full h-full"
                    controls
                    poster={video.thumbnail}
                  >
                    <source src={video.url} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <Download className="h-12 w-12 text-gray-400 mb-4" />
                      <p className="text-gray-600">Video will appear here when ready</p>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="mt-4">
                <h2 className="text-2xl font-bold text-gray-900">Video Details</h2>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Title</h3>
                    <p className="text-gray-700">{video.title}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Description</h3>
                    <p className="text-gray-700">{video.description}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Duration</h3>
                    <p className="text-gray-700">{video.duration} seconds</p>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Format</h3>
                    <p className="text-gray-700">{video.format.toUpperCase()}</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Actions */}
          <div className="lg:col-span-1">
            <Card className="p-6">
              <div className="space-y-4">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Actions</h3>
                
                <div className="grid grid-cols-1 gap-4">
                  <button className="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg transition-colors flex items-center justify-center">
                    <Download className="h-5 w-5 mr-3" />
                    Download Video
                  </button>
                  
                  <button className="w-full bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-lg transition-colors flex items-center justify-center">
                    <Share2 className="h-5 w-5 mr-3" />
                    Share Video
                  </button>
                  
                  <button className="w-full bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg transition-colors flex items-center justify-center">
                    <Play className="h-5 w-5 mr-3" />
                    Play Video
                  </button>
                  
                  <button className="w-full bg-gray-600 hover:bg-gray-700 text-white p-4 rounded-lg transition-colors flex items-center justify-center">
                    <CheckCircle className="h-5 w-5 mr-3" />
                    Create New Video
                  </button>
                </div>
                
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Share Your Creation</h4>
                  <div className="flex space-x-4">
                    <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg transition-colors">
                      <Share2 className="h-4 w-4" />
                      Share Link
                    </button>
                    <button className="flex-1 bg-green-600 hover:bg-green-700 text-white p-3 rounded-lg transition-colors">
                      <Star className="h-4 w-4" />
                      Copy Link
                    </button>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ResultModern;
