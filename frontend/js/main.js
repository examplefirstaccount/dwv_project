// Chart instances
let temperatureChart;
let countryTemperatureChart;
let extremeCountriesChart;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    setupTabs();
    
    // Initialize charts
    initMeanTempYearChart();
    initCountryTemperatureChart();
    
    // Load initial data
    updateMeanTempYearChart();
    loadCountries();
    loadExtremeCountries();
    
    // Setup event listeners
    document.getElementById('update-btn').addEventListener('click', updateMeanTempYearChart);
    document.getElementById('update-country-btn').addEventListener('click', updateCountryTemperatureChart);
});

// Tab functionality
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// Load countries for dropdown
function loadCountries() {
    axios.get('http://localhost:5000/api/countries')
        .then(response => {
            const select = document.getElementById('country-select');
            select.innerHTML = '';
            
            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select a country';
            select.appendChild(defaultOption);
            
            // Add countries
            response.data.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading countries:', error);
        });
}

// Initialize Europe temperature chart
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
        options: getChartOptions()
    });
}

// Initialize Country temperature chart
function initCountryTemperatureChart() {
    const ctx = document.getElementById('countryTemperatureChart').getContext('2d');
    
    countryTemperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Mean Annual Temperature (°C)',
                data: [],
                borderColor: 'rgb(153, 102, 255)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: getChartOptions()
    });
}

// Shared chart options
function getChartOptions() {
    return {
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
    };
}

// Update Europe temperature chart
function updateMeanTempYearChart() {
    const startYear = document.getElementById('start-year').value;
    const endYear = document.getElementById('end-year').value;
    
    axios.get(`http://localhost:5000/api/mean_temperature/${startYear}/${endYear}`)
        .then(response => {
            temperatureChart.data.labels = response.data.years;
            temperatureChart.data.datasets[0].data = response.data.temperatures;
            temperatureChart.update();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('Error loading temperature data');
        });
}

// Update Country temperature chart
function updateCountryTemperatureChart() {
    const startYear = document.getElementById('country-start-year').value;
    const endYear = document.getElementById('country-end-year').value;
    const country = document.getElementById('country-select').value;
    
    if (!country) {
        alert('Please select a country');
        return;
    }
    
    axios.get(`http://localhost:5000/api/country_temperature/${country}/${startYear}/${endYear}`)
        .then(response => {
            countryTemperatureChart.data.labels = response.data.years;
            countryTemperatureChart.data.datasets[0].data = response.data.temperatures;
            countryTemperatureChart.data.datasets[0].label = `Mean Temperature (${country})`;
            countryTemperatureChart.update();
        })
        .catch(error => {
            console.error('Error fetching country data:', error);
            alert('Error loading country temperature data');
        });
}

// Load extreme countries data
function loadExtremeCountries() {
    axios.get('http://localhost:5000/api/extreme_countries_temperatures/1990/2020')
        .then(response => renderExtremeCountriesChart(response.data))
        .catch(error => {
            console.error('Error loading extreme countries:', error);
        });
}

// Render extreme countries chart
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
    
    extremeCountriesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.data[data.countries[0]].years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
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