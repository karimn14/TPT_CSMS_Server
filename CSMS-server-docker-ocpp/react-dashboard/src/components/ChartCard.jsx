import React from 'react';

const ChartCard = ({ title, subtitle, icon: Icon, children, className = "" }) => {
  return (
    <div className={`bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300 animate-fade-in ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
            {Icon && <Icon className="h-5 w-5 text-secondary" />}
            {title}
          </h3>
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>
      </div>
      <div className="h-64">
        {children}
      </div>
    </div>
  );
};

export default ChartCard;
