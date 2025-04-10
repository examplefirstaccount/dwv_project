let temperatureChart;

// Initialize chart
function initChart() {
    const ctx = document.getElementById('temperatureChart').getContext('2d');

    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Mean Annual Temperature (°C)',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '°';
                        }
                    },
                    grid: {
                        color: function(context) {
                            return context.tick.value === 0 ? 'rgba(0, 0, 0, 0.5)' : 'rgba(0, 0, 0, 0.1)';
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(2) + '°C';
                        }
                    }
                }
            }
        }
    });
}

// Fetch data and update chart
function updateChart() {
    const startYear = document.getElementById('start-year').value;
    const endYear = document.getElementById('end-year').value;

    // Configure Axios to point to Flask backend on port 5000
    axios.get(`http://localhost:5000/api/mean_temperature/${startYear}/${endYear}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        const data = response.data;

        // Update chart data
        temperatureChart.data.labels = data.years;
        temperatureChart.data.datasets[0].data = data.temperatures;
        temperatureChart.update();
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        if (error.response) {
            // The request was made and the server responded with a status code
            console.error('Server responded with:', error.response.status);
            console.error('Response data:', error.response.data);
        } else if (error.request) {
            // The request was made but no response was received
            console.error('No response received:', error.request);
        } else {
            // Something happened in setting up the request
            console.error('Request setup error:', error.message);
        }
        alert('Error loading temperature data. Please check console for details.');
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initChart();
    updateChart();

    // Add event listener to update button
    document.getElementById('update-btn').addEventListener('click', updateChart);
});