// Configuración de gráficas
const tempConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperatura °C',
            data: [],
            borderColor: '#2196F3',
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: false
            }
        }
    }
};

const humConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Humedad Aire %',
            data: [],
            borderColor: '#4CAF50',
            tension: 0.4
        }, {
            label: 'Humedad Suelo %',
            data: [],
            borderColor: '#9C27B0',
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
};

const tempChart = new Chart(document.getElementById('tempChart'), tempConfig);
const humChart = new Chart(document.getElementById('humChart'), humConfig);

let bombaActiva = false;

function updateDatos() {
    fetch('/datos')
        .then(response => response.json())
        .then(data => {
            // Actualizar métricas
            document.getElementById('temperatura').textContent = data.temperatura.toFixed(1);
            document.getElementById('humedad_aire').textContent = data.humedad_aire.toFixed(1);
            document.getElementById('humedad_suelo').textContent = data.humedad_suelo.toFixed(1);
            
            // Actualizar gráficas
            tempChart.data.labels = data.historico.tiempo;
            tempChart.data.datasets[0].data = data.historico.temperatura;
            tempChart.update();

            humChart.data.labels = data.historico.tiempo;
            humChart.data.datasets[0].data = data.historico.humedad_aire;
            humChart.data.datasets[1].data = data.historico.humedad_suelo;
            humChart.update();
            
            // Actualizar estado bomba
            bombaActiva = data.bomba;
            updateBombaUI(bombaActiva);

            // Mostrar alertas
            if(data.humedad_suelo < 30) {
                showAlert('¡Alerta! Suelo muy seco');
            } else {
                hideAlert();
            }
        })
        .catch(error => console.error('Error:', error));
}

function toggleBomba() {
    const nuevoEstado = !bombaActiva;
    fetch('/bomba', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'estado=' + (nuevoEstado ? '1' : '0')
    })
    .then(response => {
        if(response.ok) {
            bombaActiva = nuevoEstado;
            updateBombaUI(bombaActiva);
        }
    });
}

function updateBombaUI(activa) {
    const button = document.getElementById('toggleButton');
    const status = document.getElementById('bombaStatus');
    
    button.textContent = activa ? 'Desactivar Bomba' : 'Activar Bomba';
    status.textContent = activa ? 'Bomba Activa' : 'Bomba Inactiva';
    status.className = 'status ' + (activa ? 'active' : 'inactive');
}

function showAlert(message) {
    const alertBox = document.getElementById('alertBox');
    alertBox.textContent = message;
    alertBox.style.display = 'block';
}

function hideAlert() {
    document.getElementById('alertBox').style.display = 'none';
}

// Actualizar datos cada 2 segundos
setInterval(updateDatos, 2000);
document.getElementById('toggleButton').onclick = toggleBomba;