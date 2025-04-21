document.addEventListener('DOMContentLoaded', () => {
    const API_URL = window.appConfig.API_BASE_URL;
    const svg = d3.select('#minmaxTemperatureChart');
    const margin = { top: 50, right: 50, bottom: 50, left: 60 };
    const width = +svg.attr('width') - margin.left - margin.right;
    const height = +svg.attr('height') - margin.top - margin.bottom;
    const chartArea = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    let xScale = d3.scaleLinear().range([0, width]);
    let yScale = d3.scaleLinear().range([height, 0]);

    let xAxis = chartArea.append('g').attr('transform', `translate(0,${height})`);
    let yAxis = chartArea.append('g');

    chartArea.append('text')
        .attr('transform', `translate(${width / 2},${height + 40})`)
        .style('text-anchor', 'middle')
        .text('Year');

    chartArea.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -50)
        .attr('x', -height / 2)
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .text('Temperature (°C)');

    const lineMin = d3.line()
        .x(d => xScale(d.year))
        .y(d => yScale(d.min_temp));

    const lineMax = d3.line()
        .x(d => xScale(d.year))
        .y(d => yScale(d.max_temp));

    const minPath = chartArea.append('path')
        .attr('fill', 'none')
        .attr('stroke', 'blue')
        .attr('stroke-width', 2);

    const maxPath = chartArea.append('path')
        .attr('fill', 'none')
        .attr('stroke', 'red')
        .attr('stroke-width', 2);

    document.getElementById('minmax-load-btn').addEventListener('click', async () => {
        const month = document.getElementById('minmax-month').value;
        const startYear = +document.getElementById('minmax-start-year').value;
        const endYear = +document.getElementById('minmax-end-year').value;

        try {
            const res = await axios.get(`${API_URL}/api/min_max`, {
                params: { month, start_year: startYear, end_year: endYear }
            });

            const data = res.data;

            if (!Array.isArray(data) || data.length === 0) {
                alert('Нет данных для выбранного диапазона.');
                minPath.attr('d', null);
                maxPath.attr('d', null);
                return;
            }

            data.forEach(d => {
                d.year = +d.year;
                d.min_temp = +d.min_temp;
                d.max_temp = +d.max_temp;
            });

            xScale.domain(d3.extent(data, d => d.year));
            yScale.domain([
                d3.min(data, d => Math.min(d.min_temp, d.max_temp)),
                d3.max(data, d => Math.max(d.min_temp, d.max_temp))
            ]);

            xAxis.call(d3.axisBottom(xScale).tickFormat(d3.format("d")));
            yAxis.call(d3.axisLeft(yScale));

            minPath.datum(data).attr('d', lineMin);
            maxPath.datum(data).attr('d', lineMax);

        } catch (err) {
            console.error('Error:', err);
            alert('Error.');
        }
    });
});
