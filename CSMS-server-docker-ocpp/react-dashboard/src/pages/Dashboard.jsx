import React, { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import {
  Zap,
  Activity,
  Shield,
  AlertCircle,
  TrendingUp,
  Battery,
  Cpu
} from 'lucide-react';

import Header from '../components/Header';
import ChartCard from '../components/ChartCard';
import MetricCard from '../components/MetricCard';

// API base URL - change this to match your backend
const API_BASE_URL = 'http://localhost:5050'; // Adjust this to match your API service port

const Dashboard = () => {
  const [chargePoints, setChargePoints] = useState([]);
  const [connectors, setConnectors] = useState({});
  const [transactions, setTransactions] = useState([]);
  const [availabilityData, setAvailabilityData] = useState([]);
  const [energyData, setEnergyData] = useState([]);
  const [efficiencyData, setEfficiencyData] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from API
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch charge points with connectors
      const cpsResponse = await fetch(`${API_BASE_URL}/cps`);
      if (!cpsResponse.ok) throw new Error('Failed to fetch charge points');
      const cpsData = await cpsResponse.json();

      setChargePoints(cpsData);

      // Build connectors object
      const connectorsObj = {};
      cpsData.forEach(cp => {
        connectorsObj[cp.id] = cp.connectors || [];
      });
      setConnectors(connectorsObj);

      // Fetch transactions
      const txResponse = await fetch(`${API_BASE_URL}/transactions?page=1&limit=50`);
      if (!txResponse.ok) throw new Error('Failed to fetch transactions');
      const txData = await txResponse.json();
      setTransactions(txData);

      // Fetch ML data (if available)
      try {
        const availabilityResponse = await fetch(`${API_BASE_URL}/predict/availability?hours=24`);
        if (availabilityResponse.ok) {
          const availabilityData = await availabilityResponse.json();
          // Transform data for chart
          const chartData = availabilityData.map((val, index) => ({
            time: `${index}:00`,
            availability: val
          }));
          setAvailabilityData(chartData);
        }
      } catch (mlError) {
        console.log('ML service not available, using sample data');
        // Keep sample data
      }

      // Generate sample data for other charts (or fetch from ML service)
      setEnergyData([
        { day: 'Mon', demand: 245 },
        { day: 'Tue', demand: 312 },
        { day: 'Wed', demand: 289 },
        { day: 'Thu', demand: 356 },
        { day: 'Fri', demand: 423 },
        { day: 'Sat', demand: 198 },
        { day: 'Sun', demand: 167 },
      ]);

      setEfficiencyData([
        { station: 'Alpha', efficiency: 94 },
        { station: 'Beta', efficiency: 87 },
        { station: 'Gamma', efficiency: 91 },
        { station: 'Delta', efficiency: 89 },
      ]);

      setAnomalyData([
        { time: 'Week 1', score: 0.2 },
        { time: 'Week 2', score: 0.1 },
        { time: 'Week 3', score: 0.3 },
        { time: 'Week 4', score: 0.15 },
      ]);

    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 5 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Connected':
        return 'text-green-600 bg-green-100';
      case 'Disconnected':
        return 'text-red-600 bg-red-100';
      case 'Available':
        return 'text-green-600 bg-green-100';
      case 'Charging':
        return 'text-blue-600 bg-blue-100';
      case 'Faulted':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Calculate metrics from real data
  const totalStations = chargePoints.length;
  const activeSessions = transactions.filter(tx => !tx.stop_ts).length;
  const systemHealth = chargePoints.length > 0 ?
    Math.round((chargePoints.filter(cp => cp.connected).length / chargePoints.length) * 100) : 0;
  const alerts = chargePoints.filter(cp =>
    cp.connectors?.some(conn => conn.error_code !== 'NoError')
  ).length;

  if (loading && chargePoints.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">Error loading data: {error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-blue-50">
      <Header />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Stations"
            value={totalStations.toString()}
            change="+12%"
            changeType="positive"
            icon={Zap}
          />
          <MetricCard
            title="Active Sessions"
            value={activeSessions.toString()}
            change="+8%"
            changeType="positive"
            icon={Activity}
          />
          <MetricCard
            title="System Health"
            value={`${systemHealth}%`}
            change="+2%"
            changeType="positive"
            icon={Shield}
          />
          <MetricCard
            title="Alerts"
            value={alerts.toString()}
            change="-25%"
            changeType="positive"
            icon={AlertCircle}
          />
        </div>

        {/* AI/ML Insights Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartCard
            title="Availability Prediction"
            subtitle="24-hour forecast with AI-powered insights"
            icon={TrendingUp}
          >
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={availabilityData}>
                <defs>
                  <linearGradient id="availabilityGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0D7BFF" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#0D7BFF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e3f2fd" />
                <XAxis dataKey="time" stroke="#0A1F44" />
                <YAxis stroke="#0A1F44" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e3f2fd',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="availability"
                  stroke="#0D7BFF"
                  fillOpacity={1}
                  fill="url(#availabilityGradient)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard
            title="Energy Demand Forecast"
            subtitle="Weekly consumption patterns"
            icon={Battery}
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={energyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e3f2fd" />
                <XAxis dataKey="day" stroke="#0A1F44" />
                <YAxis stroke="#0A1F44" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e3f2fd',
                    borderRadius: '8px'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="demand"
                  stroke="#4CCBFF"
                  strokeWidth={3}
                  dot={{ fill: '#4CCBFF', strokeWidth: 2, r: 6 }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard
            title="Station Efficiency Metrics"
            subtitle="Performance comparison across stations"
            icon={Cpu}
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={efficiencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e3f2fd" />
                <XAxis dataKey="station" stroke="#0A1F44" />
                <YAxis stroke="#0A1F44" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e3f2fd',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="efficiency" fill="#0D7BFF" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard
            title="Anomaly Detection Score"
            subtitle="AI monitoring for system irregularities"
            icon={Shield}
          >
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={anomalyData}>
                <defs>
                  <linearGradient id="anomalyGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4CCBFF" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#4CCBFF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e3f2fd" />
                <XAxis dataKey="time" stroke="#0A1F44" />
                <YAxis stroke="#0A1F44" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e3f2fd',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="score"
                  stroke="#4CCBFF"
                  fillOpacity={1}
                  fill="url(#anomalyGradient)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Charge Points Table */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-primary">Charge Points</h3>
            <button
              onClick={fetchData}
              className="px-3 py-1 text-sm bg-primary text-white rounded-lg hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Firmware</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total kWh</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {chargePoints.map((cp) => (
                  <tr key={cp.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{cp.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cp.vendor || "-"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cp.model || "-"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cp.firmware_version || "-"}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(cp.connected ? 'Connected' : 'Disconnected')}`}>
                        {cp.connected ? 'Connected' : 'Disconnected'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{cp.total_kwh?.toFixed(2) || "0.00"} kWh</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Connectors Tables */}
        {Object.entries(connectors).map(([cpId, cpConnectors]) => (
          <div key={cpId} className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-primary">Connectors - {cpId}</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Connector ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Error Code</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Heartbeat</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {cpConnectors.map((conn) => (
                    <tr key={conn.connector_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{conn.connector_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(conn.status)}`}>
                          {conn.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{conn.error_code}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{conn.last_heartbeat || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}

        {/* Transactions Table */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-primary">Transactions</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CP</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tx ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">idTag</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Connector</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Meter Start (Wh)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Meter Stop (Wh)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">kWh Used</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Start Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stop Time</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.map((tx) => (
                  <tr key={tx.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{tx.cp_id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{tx.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.id_tag}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{tx.connector_id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.meter_start || "-"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.meter_stop || "-"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {tx.meter_start !== null && tx.meter_stop !== null ? ((tx.meter_stop - tx.meter_start) / 1000).toFixed(2) : "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.start_ts || "-"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tx.stop_ts || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
