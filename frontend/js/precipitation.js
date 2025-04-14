document.addEventListener('DOMContentLoaded', () => {
    const API_URL = window.appConfig.API_BASE_URL;
    const svg = d3.select('#precipitation-chart');
    const margin = { top: 20, right: 30, bottom: 50, left: 60 };
    const width = +svg.attr('width') - margin.left - margin.right;
    const height = +svg.attr('height') - margin.top - margin.bottom;
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime().range([0, width]);
    const y = d3.scaleLinear().range([height, 0]);

    const xAxis = g.append('g').attr('transform', `translate(0,${height})`);
    const yAxis = g.append('g');

    const line = d3.line()
        .x(d => x(new Date(d.date)))
        .y(d => y(d.precipitation));

    g.append('path')
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 2);

    document.getElementById('load-precipitation').addEventListener('click', async () => {
        const country = document.getElementById('precipitation-country').value;
        const year = document.getElementById('precipitation-year').value;

        try {
            const res = await axios.get(`${API_URL}/api/precipitation`, {
                params: { country, year }
            });
            const raw = res.data;

            // Преобразуем в массив { date, precipitation }
            const data = Object.entries(raw).map(([date, obj]) => ({
                date,
                precipitation: obj.precipitation
            })).sort((a, b) => new Date(a.date) - new Date(b.date));

            if (data.length === 0) {
                alert(`Нет данных об осадках для страны ${country} за ${year} год.`);
                return;
            }

            x.domain(d3.extent(data, d => new Date(d.date)));
            y.domain([0, d3.max(data, d => d.precipitation)]);

            xAxis.call(d3.axisBottom(x).ticks(12).tickFormat(d3.timeFormat('%b')));
            yAxis.call(d3.axisLeft(y));

            g.select('.line')
                .datum(data)
                .transition()
                .duration(1000)
                .attr('d', line);

        } catch (err) {
            console.error('Error loading precipitation data:', err);
        }
    });

    // Заполнение списка стран, можно взять с того же API, откуда берется страна для температур
    axios.get(`${API_URL}/api/countries`) // предполагаемое API, замени на актуальное
        .then(res => {
            const select = document.getElementById('precipitation-country');
            select.innerHTML = '';
            res.data.forEach(c => {
                const option = document.createElement('option');
                option.value = c;
                option.textContent = c;
                select.appendChild(option);
            });
        });
});
