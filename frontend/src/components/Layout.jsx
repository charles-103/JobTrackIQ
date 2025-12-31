import { Link, useLocation } from 'react-router-dom';
import { Briefcase, Inbox } from 'lucide-react';

export default function Layout({ children }) {
  const location = useLocation();
  
  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link
                to="/"
                className="flex items-center px-4 py-2 text-xl font-bold text-primary-600 hover:text-primary-700"
              >
                <Briefcase className="w-6 h-6 mr-2" />
                JobTrackIQ
              </Link>
              
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    isActive('/') && location.pathname !== '/jobs'
                      ? 'border-primary-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Applications
                </Link>
                <Link
                  to="/jobs"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    isActive('/jobs')
                      ? 'border-primary-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Inbox className="w-4 h-4 mr-1" />
                  Job Inbox
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}







