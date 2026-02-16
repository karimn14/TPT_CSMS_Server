const express = require('express');
const cors = require('cors'); // Tambahkan ini
const app = express();
const port = 3000;

app.use(cors()); // Izinkan akses dari mana saja
app.use(express.json());

// Sajikan folder public secara statis (CSS, Gambar)
app.use('/public', express.static('public')); 

// Sajikan file HTML di root
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});
app.get('/connected.html', (req, res) => {
    res.sendFile(__dirname + '/connected.html');
});
app.get('/preface.html', (req, res) => {
    res.sendFile(__dirname + '/preface.html');
});

// Variabel Penyimpanan Data Sementara
let latestData = {
  uid: "N/A",
  username: "Guest",
  power: "0.0 kW",
  energy: "0.0 kWh",
  duration: "0 min",
  status: "STANDBY" // Status: STANDBY, CHARGING, FINISHED
};

// Endpoint untuk Python mengupdate data
app.post('/data', (req, res) => {
  const { uid, username, power, energy, duration, status } = req.body;
  console.log(`Update Status: ${status} | UID: ${uid}`);

  latestData = {
    uid: uid || latestData.uid,
    username: username || latestData.username,
    power: power || latestData.power,
    energy: energy || latestData.energy,
    duration: duration || latestData.duration,
    status: status || latestData.status
  };

  res.status(200).json({ message: "Data updated", data: latestData });
});

// Endpoint untuk Frontend mengambil data (Polling)
app.get('/api/data', (req, res) => {
  res.status(200).json(latestData);
});

app.listen(port, () => {
  console.log(`UI Server berjalan di http://localhost:${port}`);
});