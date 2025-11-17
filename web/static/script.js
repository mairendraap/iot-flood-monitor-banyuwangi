// Konfigurasi
const CONFIG = {
    dataUrls: {
        main: '../data/raw/iot_floodmonitor_banyuwangi_hydrological_2024_v1.0.csv',
        samples: 'data/samples/'
    },
    updateInterval: 300000, // 5 minutes
    floodThresholds: {
        critical: 80,
        warning: 60,
        normal: 40
    }
};

// Data sungai Banyuwangi
const rivers = [
    { id: 1, name: 'Kali Setail', lat: -8.2192, lng: 114.3691, status: 'normal', waterLevel: 1.2, dangerLevel: 3.0 },
    { id: 2, name: 'Kali Baru', lat: -8.2135, lng: 114.3685, status: 'warning', waterLevel: 2.5, dangerLevel: 3.0 },
    { id: 3, name: 'Kali Tambong', lat: -8.2078, lng: 114.3662, status: 'normal', waterLevel: 1.8, dangerLevel: 3.5 },
    { id: 4, name: 'Kali Panggang', lat: -8.2019, lng: 114.3624, status: 'danger', waterLevel: 4.2, dangerLevel: 4.0 },
    { id: 5, name: 'Kali Mayang', lat: -8.1963, lng: 114.3587, status: 'normal', waterLevel: 1.5, dangerLevel: 3.2 },
    { id: 6, name: 'Kali Bomo', lat: -8.1905, lng: 114.3549, status: 'warning', waterLevel: 2.8, dangerLevel: 3.0 },
    { id: 7, name: 'Kali Sobo', lat: -8.1847, lng: 114.3512, status: 'normal', waterLevel: 1.1, dangerLevel: 2.8 }
];

// Data dummy untuk perangkat Arduino
const devices = [
    { id: 1, name: 'Sensor Kali Setail', location: 'Kali Setail', status: 'online', type: 'water-level' },
    { id: 2, name: 'Sensor Kali Baru', location: 'Kali Baru', status: 'online', type: 'water-level' },
    { id: 3, name: 'Sensor Kali Tambong', location: 'Kali Tambong', status: 'offline', type: 'water-level' },
    { id: 4, name: 'Sensor Kali Panggang', location: 'Kali Panggang', status: 'online', type: 'water-level' },
    { id: 5, name: 'Pompa Kali Mayang', location: 'Kali Mayang', status: 'online', type: 'pump' },
    { id: 6, name: 'Pintu Air Kali Bomo', location: 'Kali Bomo', status: 'online', type: 'gate' }
];

// Data log perangkat
let deviceLog = [
    { time: '2023-11-01 10:30:15', device: 'Sensor Kali Setail', action: 'Pembacaan data', status: 'Berhasil' },
    { time: '2023-11-01 10:25:42', device: 'Pompa Kali Mayang', action: 'Dinyalakan', status: 'Berhasil' },
    { time: '2023-11-01 10:20:18', device: 'Sensor Kali Baru', action: 'Kalibrasi', status: 'Berhasil' },
    { time: '2023-11-01 10:15:33', device: 'Sensor Kali Tambong', action: 'Pembacaan data', status: 'Gagal' },
    { time: '2023-11-01 10:10:27', device: 'Pintu Air Kali Bomo', action: 'Ditutup sebagian', status: 'Berhasil' }
];

// Variabel global untuk chart dan peta
let map;
let waterLevelChart, correlationChart, regressionChart, trendChart;

// Fungsi untuk cek authentication
function checkAuth() {
    return localStorage.getItem('admin_logged_in') === 'true';
}

function redirectToLogin() {
    window.location.href = '../php/login/index.php';
}

function logout() {
    localStorage.removeItem('admin_logged_in');
    localStorage.removeItem('admin_username');
    localStorage.removeItem('admin_login_time');
    updateUIForAuth();
    window.location.reload();
}

// Update UI berdasarkan status login
function updateUIForAuth() {
    const isLoggedIn = checkAuth();
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userDisplayName = document.getElementById('user-display-name');
    
    if (isLoggedIn) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
        document.getElementById('protected-admin-message').style.display = 'none';
        document.getElementById('admin-content').style.display = 'block';
        document.getElementById('protected-data-message').style.display = 'none';
        document.getElementById('data-content').style.display = 'block';
        document.getElementById('load-csv-btn').style.display = 'inline-block';
        
        const username = localStorage.getItem('admin_username') || 'Admin';
        userDisplayName.textContent = username;
        
        // Load data yang diproteksi
        renderDeviceControl();
        renderDeviceLog();
        loadCSVData();
    } else {
        loginBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
        document.getElementById('protected-admin-message').style.display = 'block';
        document.getElementById('admin-content').style.display = 'none';
        document.getElementById('protected-data-message').style.display = 'block';
        document.getElementById('data-content').style.display = 'none';
        document.getElementById('load-csv-btn').style.display = 'none';
        userDisplayName.textContent = 'Guest';
    }
}

// Inisialisasi peta
function initMap() {
    map = L.map('map').setView([-8.2192, 114.3691], 12);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Tambahkan marker untuk setiap sungai
    rivers.forEach(river => {
        let iconColor;
        if (river.status === 'normal') iconColor = 'green';
        else if (river.status === 'warning') iconColor = 'orange';
        else iconColor = 'red';
        
        const riverIcon = L.divIcon({
            html: `<div style="background-color: ${iconColor}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.5);"></div>`,
            className: 'river-marker',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
        
        const marker = L.marker([river.lat, river.lng], { icon: riverIcon }).addTo(map);
        marker.bindPopup(`
            <strong>${river.name}</strong><br>
            Status: ${river.status === 'normal' ? 'Normal' : river.status === 'warning' ? 'Waspada' : 'Bahaya'}<br>
            Tinggi Air: ${river.waterLevel} m<br>
            Level Bahaya: ${river.dangerLevel} m
        `);
    });
}

// Render kartu status sungai
function renderRiverStatus() {
    const container = document.getElementById('river-status-container');
    container.innerHTML = '';
    
    rivers.forEach(river => {
        const card = document.createElement('div');
        card.className = `river-card ${river.status}`;
        
        let statusText, statusClass;
        if (river.status === 'normal') {
            statusText = 'Normal';
            statusClass = 'normal';
        } else if (river.status === 'warning') {
            statusText = 'Waspada';
            statusClass = 'warning';
        } else {
            statusText = 'Bahaya';
            statusClass = 'danger';
        }
        
        card.innerHTML = `
            <h3>${river.name} <span class="status ${statusClass}">${statusText}</span></h3>
            <div class="data">
                <div class="data-item">
                    <div class="data-value">${river.waterLevel}m</div>
                    <div class="data-label">Tinggi Air</div>
                </div>
                <div class="data-item">
                    <div class="data-value">${river.dangerLevel}m</div>
                    <div class="data-label">Level Bahaya</div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
    
    // Update waktu terakhir pembaruan
    document.getElementById('last-update').textContent = 
        `Terakhir diperbarui: Februari 2024`;
}

// Render kontrol perangkat (hanya untuk admin)
function renderDeviceControl() {
    if (!checkAuth()) return;
    
    const container = document.getElementById('device-control-container');
    container.innerHTML = '';
    
    devices.forEach(device => {
        const card = document.createElement('div');
        card.className = 'device-card';
        
        card.innerHTML = `
            <h3>${device.name}</h3>
            <p>Lokasi: ${device.location}</p>
            <div class="device-status ${device.status}">${device.status === 'online' ? 'Online' : 'Offline'}</div>
            <div class="device-actions">
                <button class="btn btn-primary" onclick="controlDevice(${device.id}, 'start')">Nyalakan</button>
                <button class="btn btn-warning" onclick="controlDevice(${device.id}, 'restart')">Restart</button>
                <button class="btn btn-danger" onclick="controlDevice(${device.id}, 'stop')">Matikan</button>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// Render log perangkat (hanya untuk admin)
function renderDeviceLog() {
    if (!checkAuth()) return;
    
    const container = document.getElementById('device-log');
    container.innerHTML = '';
    
    deviceLog.forEach(log => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${log.time}</td>
            <td>${log.device}</td>
            <td>${log.action}</td>
            <td>${log.status}</td>
        `;
        container.appendChild(row);
    });
}

// Kontrol perangkat (dummy) - hanya untuk admin
function controlDevice(deviceId, action) {
    if (!checkAuth()) {
        alert('Anda harus login untuk mengontrol perangkat');
        return;
    }
    
    const device = devices.find(d => d.id === deviceId);
    if (!device) return;
    
    const actionText = action === 'start' ? 'Dinyalakan' : 
                     action === 'restart' ? 'Direstart' : 'Dimatikan';
    
    // Tambahkan ke log
    deviceLog.unshift({
        time: new Date().toLocaleString('id-ID'),
        device: device.name,
        action: actionText,
        status: 'Berhasil'
    });
    
    // Update render log
    renderDeviceLog();
    
    alert(`Perangkat ${device.name} berhasil ${actionText.toLowerCase()}`);
}

// Inisialisasi chart
function initCharts() {
    // Chart tinggi air
    const waterLevelCtx = document.getElementById('waterLevelChart').getContext('2d');
    waterLevelChart = new Chart(waterLevelCtx, {
        type: 'bar',
        data: {
            labels: rivers.map(r => r.name),
            datasets: [{
                label: 'Tinggi Air (m)',
                data: rivers.map(r => r.waterLevel),
                backgroundColor: rivers.map(r => 
                    r.status === 'normal' ? '#27ae60' : 
                    r.status === 'warning' ? '#f39c12' : '#e74c3c'
                ),
                borderColor: rivers.map(r => 
                    r.status === 'normal' ? '#219653' : 
                    r.status === 'warning' ? '#e67e22' : '#c0392b'
                ),
                borderWidth: 1
            }, {
                label: 'Level Bahaya (m)',
                data: rivers.map(r => r.dangerLevel),
                type: 'line',
                borderColor: '#2c3e50',
                borderWidth: 2,
                fill: false,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Tinggi Air (m)'
                    }
                }
            }
        }
    });
    
    // Chart korelasi
    const correlationCtx = document.getElementById('correlationChart').getContext('2d');
    correlationChart = new Chart(correlationCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Korelasi Tinggi Air vs Level Bahaya',
                data: rivers.map(r => ({x: r.waterLevel, y: r.dangerLevel})),
                backgroundColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Tinggi Air (m)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Level Bahaya (m)'
                    }
                }
            }
        }
    });
    
    // Chart regresi
    const regressionCtx = document.getElementById('regressionChart').getContext('2d');
    regressionChart = new Chart(regressionCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'],
            datasets: [{
                label: 'Tinggi Air Rata-rata',
                data: [1.2, 1.5, 1.8, 2.1, 2.3, 2.5, 2.8, 3.0, 2.7, 2.2, 1.8, 1.4],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Tinggi Air (m)'
                    }
                }
            }
        }
    });
    
    // Chart trend
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
            datasets: [{
                label: 'Kejadian Banjir',
                data: [12, 15, 18, 22, 19, 25],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                fill: true
            }, {
                label: 'Tinggi Air Maksimum',
                data: [3.2, 3.5, 3.8, 4.2, 3.9, 4.5],
                borderColor: '#3498db',
                backgroundColor: 'transparent',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Navigasi menu sidebar
function initNavigation() {
    const menuItems = document.querySelectorAll('.sidebar-menu li');
    const sections = document.querySelectorAll('.dashboard-section');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            
            // Cek proteksi untuk section tertentu
            if ((target === 'admin' || target === 'data') && !checkAuth()) {
                alert('Anda harus login terlebih dahulu untuk mengakses ' + 
                      (target === 'admin' ? 'Admin Panel' : 'River Data'));
                return;
            }
            
            // Update menu aktif
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Tampilkan section yang sesuai
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === target) {
                    section.classList.add('active');
                    
                    // Jika peta, inisialisasi ulang
                    if (target === 'map') {
                        setTimeout(() => {
                            if (map) map.invalidateSize();
                        }, 300);
                    }
                }
            });
        });
    });
    
    // Navigasi tab
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Update tab aktif
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Tampilkan konten tab yang sesuai
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// Load data CSV (hanya untuk admin)
function loadCSVData() {
    if (!checkAuth()) {
        alert('Anda harus login untuk mengakses data CSV');
        return;
    }
    
    // Simulasi pemuatan data CSV
    const sampleData = [
        { date: '2023-11-01', time: '08:00', setail: 1.2, baru: 2.5, tambong: 1.8, panggang: 4.2, mayang: 1.5, bomo: 2.8, sobo: 1.1 },
        { date: '2023-10-31', time: '08:00', setail: 1.1, baru: 2.3, tambong: 1.7, panggang: 3.9, mayang: 1.4, bomo: 2.6, sobo: 1.0 },
        { date: '2023-10-30', time: '08:00', setail: 1.3, baru: 2.7, tambong: 1.9, panggang: 4.5, mayang: 1.6, bomo: 2.9, sobo: 1.2 },
        { date: '2023-10-29', time: '08:00', setail: 1.0, baru: 2.1, tambong: 1.6, panggang: 3.7, mayang: 1.3, bomo: 2.4, sobo: 0.9 },
        { date: '2023-10-28', time: '08:00', setail: 1.4, baru: 2.9, tambong: 2.0, panggang: 4.8, mayang: 1.7, bomo: 3.1, sobo: 1.3 }
    ];
    
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';
    
    sampleData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.date}</td>
            <td>${row.time}</td>
            <td>${row.setail}</td>
            <td>${row.baru}</td>
            <td>${row.tambong}</td>
            <td>${row.panggang}</td>
            <td>${row.mayang}</td>
            <td>${row.bomo}</td>
            <td>${row.sobo}</td>
        `;
        tableBody.appendChild(tr);
    });
    
    alert('Data CSV berhasil dimuat!');
}

// Update chart data
function updateCharts() {
    if (waterLevelChart) {
        waterLevelChart.data.datasets[0].data = rivers.map(r => r.waterLevel);
        waterLevelChart.data.datasets[0].backgroundColor = rivers.map(r => 
            r.status === 'normal' ? '#27ae60' : 
            r.status === 'warning' ? '#f39c12' : '#e74c3c'
        );
        waterLevelChart.update();
    }
    
    if (correlationChart) {
        correlationChart.data.datasets[0].data = rivers.map(r => ({x: r.waterLevel, y: r.dangerLevel}));
        correlationChart.update();
    }
}

// Inisialisasi aplikasi
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    renderRiverStatus();
    initCharts();
    initNavigation();
    updateUIForAuth();
    
    // Event listener untuk tombol
    document.getElementById('login-btn').addEventListener('click', redirectToLogin);
    document.getElementById('logout-btn').addEventListener('click', logout);
    document.getElementById('admin-login-btn').addEventListener('click', redirectToLogin);
    document.getElementById('data-login-btn').addEventListener('click', redirectToLogin);
    document.getElementById('load-csv-btn').addEventListener('click', loadCSVData);
    
    // Cek jika kembali dari login dengan parameter success
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('login') === 'success') {
        localStorage.setItem('admin_logged_in', 'true');
        localStorage.setItem('admin_username', 'Administrator');
        localStorage.setItem('admin_login_time', new Date().getTime().toString());
        updateUIForAuth();
        
        // Remove parameter
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Simulasi update data real-time
    setInterval(() => {
        // Update status sungai secara acak untuk simulasi
        rivers.forEach(river => {
            // Simulasi perubahan level air kecil
            const change = (Math.random() - 0.5) * 0.2;
            river.waterLevel = Math.max(0.1, river.waterLevel + change);
            
            // Update status berdasarkan level air
            if (river.waterLevel > river.dangerLevel) {
                river.status = 'danger';
            } else if (river.waterLevel > river.dangerLevel * 0.7) {
                river.status = 'warning';
            } else {
                river.status = 'normal';
            }
        });
        
        renderRiverStatus();
        updateCharts();
    }, 10000); // Update setiap 10 detik
});