import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Play, Video, Zap, Users, TrendingUp, Star } from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative z-10 pb-8 pt-20 sm:pb-12 sm:pt-24">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="text-center">
                <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                  <span className="block">Transform Your Ideas Into</span>
                  <span className="block text-blue-600">Stunning Videos</span>
                </h1>
                <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
                  Powered by advanced AI technology, our video generator creates professional-quality videos from your text descriptions.
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Why Choose AI Video Generator?
            </h2>
            <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {/* Feature 1 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center"
              >
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 p-4">
                  <Video className="h-6 w-6 text-white" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">AI-Powered Scripts</h3>
                    <p className="mt-2 text-sm text-white">
                      Generate professional video scripts with scene-by-scene narration
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Feature 2 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="text-center"
              >
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 p-4">
                  <Zap className="h-6 w-6 text-white" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">Smart Scene Generation</h3>
                    <p className="mt-2 text-sm text-white">
                      Create detailed scenes with AI-generated visuals and prompts
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Feature 3 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="text-center"
              >
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-r from-pink-600 to-red-600 p-4">
                  <TrendingUp className="h-6 w-6 text-white" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">High-Quality Output</h3>
                    <p className="mt-2 text-sm text-white">
                      Export in multiple formats with professional-grade quality
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
            <div className="text-center">
              <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-white p-4 shadow-sm">
                <Users className="h-6 w-6 text-blue-600" />
                <div className="mt-2">
                  <h3 className="text-lg font-semibold text-gray-900">10K+ Users</h3>
                  <p className="text-sm text-gray-600">Trust our growing community</p>
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-white p-4 shadow-sm">
                <Video className="h-6 w-6 text-green-600" />
                <div className="mt-2">
                  <h3 className="text-lg font-semibold text-gray-900">50K+ Videos</h3>
                  <p className="text-sm text-gray-600">Created successfully</p>
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-white p-4 shadow-sm">
                <Star className="h-6 w-6 text-yellow-600" />
                <div className="mt-2">
                  <h3 className="text-lg font-semibold text-gray-900">4.9/5 Rating</h3>
                  <p className="text-sm text-gray-600">User satisfaction</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Create Your Masterpiece?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg text-white">
              Join thousands of creators who trust our AI video generator for their projects.
            </p>
            <div className="mt-10">
              <Link
                to="/dashboard"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-white bg-opacity-20 hover:bg-opacity-30 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transition-all duration-200"
              >
                Start Creating
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
