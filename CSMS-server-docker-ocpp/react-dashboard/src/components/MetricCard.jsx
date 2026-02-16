import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const MetricCard = ({ title, value, change, changeType, icon: Icon }) => {
  const isPositive = changeType === 'positive';

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-primary mt-2">{value}</p>
          {change && (
            <div className={`flex items-center mt-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? (
                <TrendingUp className="h-4 w-4 mr-1" />
              ) : (
                <TrendingDown className="h-4 w-4 mr-1" />
              )}
              <span className="text-sm font-medium">{change}</span>
            </div>
          )}
        </div>
        <div className="bg-gradient-to-r from-secondary to-accent p-3 rounded-xl">
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
};

export default MetricCard;
