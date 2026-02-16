# Modern EV Charging Station Dashboard

A beautiful, responsive React dashboard for monitoring AI-powered EV charging stations with modern UI/UX design.

## Features

- **Modern Design**: Clean, professional interface with blue-navy-ocean color palette
- **AI/ML Visualizations**: Four interactive charts showing predictive analytics
- **KPI Metrics**: Real-time system metrics with trend indicators
- **Station Management**: Comprehensive station status table
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Performance**: Optimized with Tailwind CSS and Recharts

## Tech Stack

- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Beautiful, responsive charts
- **Lucide React** - Modern icon library

## Installation

1. **Navigate to the dashboard directory:**
   ```bash
   cd react-dashboard
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Project Structure

```
react-dashboard/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Main header with branding
│   │   ├── ChartCard.jsx       # Reusable chart container
│   │   ├── MetricCard.jsx      # KPI metric cards
│   │   └── StationTable.jsx    # Station status table
│   ├── pages/
│   │   └── Dashboard.jsx       # Main dashboard page
│   ├── App.js                  # Root component
│   ├── index.js               # App entry point
│   └── index.css              # Global styles
├── package.json
├── tailwind.config.js
└── README.md
```

## Charts Included

1. **Availability Prediction** - Area chart showing 24-hour availability forecast
2. **Energy Demand Forecast** - Line chart with weekly consumption patterns
3. **Station Efficiency Metrics** - Bar chart comparing station performance
4. **Anomaly Detection Score** - Area chart monitoring system irregularities

## Customization

### Colors
The dashboard uses a custom color palette defined in `tailwind.config.js`:

```javascript
colors: {
  primary: '#0A1F44',    // Navy
  secondary: '#0D7BFF',  // Ocean blue
  accent: '#4CCBFF',     // Light blue accent
  background: '#F8FAFC', // Soft background
}
```

### Adding New Charts
1. Import the chart type from Recharts
2. Add data in the `Dashboard.jsx` component
3. Use the `ChartCard` component wrapper
4. Ensure responsive design with `ResponsiveContainer`

### Sample Data
All chart data is currently using sample data. Replace with real API calls:

```javascript
// Example API integration
useEffect(() => {
  fetch('/api/availability-data')
    .then(res => res.json())
    .then(data => setAvailabilityData(data));
}, []);
```

## Deployment

1. **Build for production:**
   ```bash
   npm run build
   ```

2. **Serve the build:**
   ```bash
   npm install -g serve
   serve -s build
   ```

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple screen sizes
5. Submit a pull request

## License

This project is open source and available under the MIT License.
