document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('minmaxTemperatureChart').getContext('2d');
    const API_URL = window.appConfig.API_BASE_URL;

    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Min Temperature',
                    borderColor: 'blue',
                    data: [],
                    fill: false
                },
                {
                    label: 'Max Temperature',
                    borderColor: 'red',
                    data: [],
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Year' }},
                y: { title: { display: true, text: 'Temperature (°C)' }}
            }
        }
    });

    document.getElementById('minmax-load-btn').addEventListener('click', async () => {
        const month = document.getElementById('minmax-month').value;
        const startYear = document.getElementById('minmax-start-year').value;
        const endYear = document.getElementById('minmax-end-year').value;

        try {
            const res = await axios.get(`${API_URL}/api/min_max`, {
                params: {
                    month,
                    start_year: startYear,
                    end_year: endYear
                }
            });

            const raw = res.data;

            if (!Array.isArray(raw) || raw.length === 0) {
                alert('Нет данных для выбранного диапазона.');
                chart.data.labels = [];
                chart.data.datasets[0].data = [];
                chart.data.datasets[1].data = [];
                chart.update();
                return;
            }

            const years = raw.map(d => d.year);
            const minTemps = raw.map(d => d.min_temp);
            const maxTemps = raw.map(d => d.max_temp);

            chart.data.labels = years;
            chart.data.datasets[0].data = minTemps;
            chart.data.datasets[1].data = maxTemps;
            chart.update();
        } catch (err) {
            console.error('Ошибка загрузки данных:', err);
            alert('Не удалось загрузить данные min/max температур.');
        }
    });
});
