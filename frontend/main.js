let temperatureChart;

function initMeanTempYearChart() {
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
                    },
                    ticks: {
                      callback: function(value, index) {
                        return index % 5 === 0 ? this.getLabelForValue(value) : '';
                      }
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

function updateMeanTempYearChart() {
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

function renderExtremeCountriesChart(data) {
    const ctx = document.getElementById('extremeCountriesChart').getContext('2d');

    const hotColors = ['#ff0000', '#ff5252', '#ff7b7b'];
    const coldColors = ['#00bfff', '#0095ff', '#0066ff'];

    const datasets = data.countries.map((country, i) => {
      const isHot = i < hotColors.length;
      const color = isHot ? hotColors[i] : coldColors[i - hotColors.length] || '#cccccc';

      return {
        label: country,
        data: data.data[country].temperatures,
        borderColor: color,
        backgroundColor: color,
        fill: false,
        tension: 0.3,
        pointRadius: 3,
        pointHoverRadius: 5
      };
    });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.data[data.countries[0]].years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false,
                    text: 'Temperature Trends: Hottest (Red) vs Coldest (Blue)'
                },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}°C`
                    }
                }
            },
            scales: {
                y: {
                    title: { display: true, text: 'Temperature (°C)' },
                    ticks: { callback: v => `${v}°` }
                },
                x: {
                    title: { display: true, text: 'Year' },
                    ticks: {
                      callback: function(value, index) {
                        return index % 5 === 0 ? this.getLabelForValue(value) : '';
                      }
                    }
                }
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // 1. Process Europe mean temperature by year
    initMeanTempYearChart();
    updateMeanTempYearChart();
    document.getElementById('update-btn').addEventListener('click', updateMeanTempYearChart);

    // 2. Fetch and render extreme countries
    axios.get('http://localhost:5000/api/extreme_countries_temperatures/1990/2020')
    .then(response => renderExtremeCountriesChart(response.data));
});