import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Video, 
  Settings, 
  Plus, 
  Clock,
  TrendingUp,
  Users,
  BarChart3
} from 'lucide-react';

const Dashboard = () => {
  const menuItems = [
    {
      title: 'Create Video',
      icon: Plus,
      description: 'Start a new video project',
      link: '/create',
      color: 'bg-blue-500'
    },
    {
      title: 'My Videos',
      icon: Video,
      description: 'View your video projects',
      link: '/videos',
      color: 'bg-purple-500'
    },
    {
      title: 'Analytics',
      icon: BarChart3,
      description: 'View usage statistics',
      link: '/analytics',
      color: 'bg-green-500'
    },
    {
      title: 'Settings',
      icon: Settings,
      description: 'Manage your account',
      link: '/settings',
      color: 'bg-gray-500'
    }
  ];

  const recentProjects = [
    {
      id: 1,
      title: 'Product Demo Video',
      status: 'completed',
      createdAt: '2024-01-15',
      thumbnail: '/api/placeholder/300/200'
    },
    {
      id: 2,
      title: 'Marketing Campaign',
      status: 'processing',
      createdAt: '2024-01-14',
      thumbnail: '/api/placeholder/300/200'
    },
    {
      id: 3,
      title: 'Tutorial Series',
      status: 'draft',
      createdAt: '2024-01-13',
      thumbnail: '/api/placeholder/300/200'
    }
  ];

  const stats = [
    {
      label: 'Total Videos',
      value: '12',
      icon: Video,
      change: '+2 this week',
      color: 'text-blue-600'
    },
    {
      label: 'Processing',
      value: '3',
      icon: Clock,
      change: '+1 from yesterday',
      color: 'text-yellow-600'
    },
    {
      label: 'Completed',
      value: '9',
      icon: TrendingUp,
      change: '+3 this week',
      color: 'text-green-600'
    },
    {
      label: 'Storage Used',
      value: '2.3GB',
      icon: BarChart3,
      change: '15% of 15GB',
      color: 'text-purple-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center space-x-3">
                <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Video className="h-5 w-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">AI Video Generator</h1>
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              <Link
                to="/create"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-colors"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Video
              </Link>

            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">
            Welcome to AI Video Generator!
          </h2>
          <p className="mt-1 text-gray-600">
            Create amazing AI-generated videos with our powerful tools
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-xs text-gray-500 mt-1">{stat.change}</p>
                </div>
                <div className={`p-3 rounded-lg bg-gray-100`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {menuItems.map((item, index) => (
              <Link
                key={index}
                to={item.link}
                className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow group"
              >
                <div className={`inline-flex p-3 rounded-lg ${item.color} mb-4 group-hover:scale-110 transition-transform`}>
                  <item.icon className="h-6 w-6 text-white" />
                </div>
                <h4 className="text-lg font-medium text-gray-900 mb-2">{item.title}</h4>
                <p className="text-sm text-gray-600">{item.description}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Projects */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Projects</h3>
            <Link
              to="/videos"
              className="text-sm text-blue-600 hover:text-blue-500 font-medium"
            >
              View all
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentProjects.map((project) => (
              <div key={project.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden group">
                <div className="aspect-w-16 aspect-h-9 bg-gray-200">
                  <img
                    src={project.thumbnail}
                    alt={project.title}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
                <div className="p-4">
                  <h4 className="font-medium text-gray-900 mb-2">{project.title}</h4>
                  <div className="flex justify-between items-center">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      project.status === 'completed' ? 'bg-green-100 text-green-800' :
                      project.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {project.status}
                    </span>
                    <span className="text-xs text-gray-500">{project.createdAt}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
