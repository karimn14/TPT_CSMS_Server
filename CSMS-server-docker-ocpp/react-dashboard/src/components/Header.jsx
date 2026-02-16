import React from 'react';
import { Zap } from 'lucide-react';

const Header = () => {
  return (
    <div className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-gradient-to-r from-secondary to-accent p-3 rounded-xl">
              <Zap className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-primary">
                AI-Powered Charging Station Management
              </h1>
              <p className="text-gray-600 mt-1">
                Real-time monitoring and predictive analytics for EV infrastructure
              </p>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">System Status</p>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-600">Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
