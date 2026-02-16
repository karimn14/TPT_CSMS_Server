import React from 'react';
import { Wifi, WifiOff, AlertTriangle } from 'lucide-react';

const StationTable = () => {
  const stations = [
    { id: 'CP_111', name: 'Station Alpha', status: 'online', connectors: 2, power: '22kW', uptime: '99.8%' },
    { id: 'CP_112', name: 'Station Beta', status: 'online', connectors: 1, power: '11kW', uptime: '97.2%' },
    { id: 'CP_123', name: 'Station Gamma', status: 'warning', connectors: 2, power: '22kW', uptime: '95.1%' },
    { id: 'CP_321', name: 'Station Delta', status: 'offline', connectors: 1, power: '11kW', uptime: '0%' },
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online':
        return <Wifi className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'offline':
        return <WifiOff className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'online':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'warning':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'offline':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return baseClasses;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-primary">Charging Stations</h3>
        <p className="text-sm text-gray-600">Real-time status of all charging points</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Station</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Connectors</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Power</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Uptime</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {stations.map((station) => (
              <tr key={station.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-r from-secondary to-accent flex items-center justify-center">
                        <span className="text-white font-medium text-sm">
                          {station.name.charAt(0)}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{station.name}</div>
                      <div className="text-sm text-gray-500">{station.id}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {getStatusIcon(station.status)}
                    <span className={`ml-2 ${getStatusBadge(station.status)}`}>
                      {station.status.charAt(0).toUpperCase() + station.status.slice(1)}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {station.connectors}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {station.power}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {station.uptime}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StationTable;
