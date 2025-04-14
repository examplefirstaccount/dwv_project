document.addEventListener('DOMContentLoaded', function() {
    const svg = d3.select("#temperature-histogram");
    const width = 800;
    const height = 500;
    const margin = {top: 40, right: 30, bottom: 80, left: 60};

    svg.attr("width", width)
       .attr("height", height);

    const x = d3.scaleLinear()
        .range([margin.left, width - margin.right])
        .domain([-5, 25]);

    const y = d3.scaleLinear()
        .range([height - margin.bottom, margin.top]);

    // Загрузка данных
    d3.json("hist_data.json").then(data => {
        if (!data) {
            throw new Error("No data loaded");
        }

        const years = Object.keys(data).sort();
        const select = d3.select("#histogram-year-select");

        // Заполняем выбор года
        select.selectAll("option")
            .data(years)
            .enter()
            .append("option")
            .attr("value", d => d)
            .text(d => d);

        // Первая отрисовка
        if (years.length > 0) {
            updateChart(data[years[0]]);
        }

        // Обработчик изменения года
        select.on("change", function() {
            updateChart(data[this.value]);
        });

    }).catch(error => {
        console.error("Error:", error);
        alert("Error loading data. See console for details.");
    });

    function updateChart(yearData) {
        if (!yearData || !Array.isArray(yearData)) {
            console.error("Invalid year data:", yearData);
            return;
        }

        const temperatures = yearData.map(Number).filter(t => !isNaN(t));
        const bins = d3.bin()
            .domain([-5, 25])
            .thresholds(20)(temperatures);

        y.domain([0, d3.max(bins, d => d.length)]);

        // Очищаем предыдущий график
        svg.selectAll("*").remove();

        // Рисуем столбцы
        svg.selectAll(".bar")
            .data(bins)
            .enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.x0) + 1)
            .attr("y", d => y(d.length))
            .attr("width", d => Math.max(0, x(d.x1) - x(d.x0) - 1))
            .attr("height", d => y(0) - y(d.length));

        // Рисуем оси
        svg.append("g")
            .attr("class", "x-axis axis")
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x).ticks(10))
            .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-0.8em")
                .attr("dy", "0.15em")
                .attr("transform", "rotate(-45)");

        svg.append("g")
            .attr("class", "y-axis axis")
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y));

        // Подписи осей
        svg.append("text")
            .attr("class", "axis-label")
            .attr("x", width / 2)
            .attr("y", height - 15)
            .style("text-anchor", "middle")
            .text("Temperature (°C)");

        svg.append("text")
            .attr("class", "axis-label")
            .attr("transform", "rotate(-90)")
            .attr("x", -height / 2 + margin.top)
            .attr("y", 15)
            .style("text-anchor", "middle")
            .text("Number of Countries");
    }
});