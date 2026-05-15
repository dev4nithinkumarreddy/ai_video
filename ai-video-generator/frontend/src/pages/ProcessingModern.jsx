import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle, AlertCircle, Play } from 'lucide-react';
import Card from '../components/Card';

const ProcessingModern = () => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('processing');
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) return 100;
        return prev + 1;
      });
    }, 100);

    return () => {
      clearInterval(interval);
    }, []);

  const steps = [
    { id: 1, title: 'Generating Script', description: 'Creating AI-powered video script' },
    { id: 2, title: 'Creating Visuals', description: 'Generating scene-by-scene visuals' },
    { id: 3, title: 'Generating Audio', description: 'Creating professional voice narration' },
    { id: 4, title: 'Rendering Video', description: 'Combining all elements into final video' },
  ];

  const getProgressPercentage = () => {
    return Math.min((progress / 100) * 100, 100);
  };

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
                    <h1 className="text-2xl font-bold text-gray-900">Processing...</h1>
                    <p className="text-sm text-gray-600">Your video is being created</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <button className="p-2 rounded-lg text-gray-600 hover:text-gray-900 transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Progress Indicator */}
          <div className="lg:col-span-2">
            <Card>
              <div className="text-center">
                <div className="relative w-32 h-32 mx-auto">
                  <svg className="absolute top-0 left-0 w-full h-full" viewBox="0 0 100 100">
                    <circle
                      className="text-gray-200"
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      strokeWidth="4"
                    />
                    <circle
                      className="text-blue-600 transition-all duration-300"
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      strokeWidth="4"
                      strokeDasharray="5 5"
                      strokeLinecap="round"
                      style={{
                        strokeDashoffset: getProgressPercentage() - 5,
                        transform: `rotate(-90deg)`,
                        transition: 'stroke-dashoffset 0.3s'
                      }}
                    />
                    <circle
                      className="text-white"
                      cx="50"
                      cy="50"
                      r="40"
                      fill="currentColor"
                    />
                    <text
                      x="50"
                      y="50"
                      textAnchor="middle"
                      className="text-2xl font-bold fill-current"
                    >
                      {`${getProgressPercentage()}%`}
                    </text>
                  </svg>
                </div>
                <div className="mt-4">
                  <h3 className="text-lg font-semibold text-gray-900">{getProgressPercentage()}%</h3>
                  <p className="text-sm text-gray-600">
                    {steps[currentStep - 1].description}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Current Step */}
          <div className="space-y-4">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Current Step</h2>
              <div className="space-y-2">
                {steps.map((step, index) => (
                  <div key={index} className={`flex items-center space-x-3 p-4 rounded-lg ${
                    index + 1 === currentStep ? 'bg-blue-100 border-blue-500' : 'bg-gray-100 border-gray-300'
                  }`}>
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      index + 1 === currentStep ? 'bg-blue-600 text-white' : 'bg-gray-400 text-gray-600'
                    }`}>
                      {index + 1 === currentStep ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : (
                        <div className="h-2 w-2 bg-white rounded-full border-2 border-gray-300"></div>
                      )}
                    </div>
                    <div>
                      <h3 className="text-sm font-medium">Step {step.id}</h3>
                      <p className="text-sm">{step.title}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProcessingModern;
