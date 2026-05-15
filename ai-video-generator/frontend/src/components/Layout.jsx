import React from 'react';
import { Outlet } from 'react-router-dom';
import { Video } from 'lucide-react';

const Layout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <Video className="h-5 w-5 text-white" />
                  </div>
                  <div className="ml-4">
                    <h1 className="text-2xl font-bold text-gray-900">AI Video Generator</h1>
                    <p className="text-sm text-gray-600">Create amazing videos with AI</p>
                  </div>
                </div>
              </div>
            </div>

            <nav className="hidden md:flex space-x-8">
              <a
                href="/dashboard"
                className="text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Dashboard
              </a>
              <a
                href="/create"
                className="text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Create
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="bg-white border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="md:flex md:justify-between">
            <div className="md:mb-0 md:mr-4">
              <h3 className="text-lg font-semibold text-gray-900">AI Video Generator</h3>
              <p className="mt-2 text-sm text-gray-600">
                Transform your ideas into stunning videos with AI
              </p>
            </div>
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h4 className="text-sm font-semibold text-gray-900">Product</h4>
                <ul className="mt-4 space-y-2 text-sm text-gray-600">
                  <li>Features</li>
                  <li>Pricing</li>
                  <li>Documentation</li>
                  <li>Support</li>
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-900">Company</h4>
                <ul className="mt-4 space-y-2 text-sm text-gray-600">
                  <li>About</li>
                  <li>Blog</li>
                  <li>Careers</li>
                </ul>
              </div>
            </div>
          </div>
          <div className="mt-8 border-t border-slate-200 pt-8">
            <p className="text-center text-sm text-gray-500">
              &copy; 2024 AI Video Generator. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
