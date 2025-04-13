document.addEventListener("DOMContentLoaded", () => {
    const heatmapContainer = document.getElementById("heatmap-container");
    const yearSlider = document.getElementById("heatmap-year");
    const yearDisplay = document.getElementById("year-display");
    const API_URL = window.appConfig.API_BASE_URL;

    const updateHeatmap = (year) => {
        const url = `${API_URL}/api/heatmap?year=${year}`;
        const img = new Image();
        img.src = url;
        img.alt = `Heatmap for ${year}`;
        img.className = "heatmap-image";
        img.onload = () => {
            // Clear previous image
            heatmapContainer.innerHTML = "";
            heatmapContainer.appendChild(img);
        };
        img.onerror = () => {
            heatmapContainer.innerHTML = `<p class="error-msg">Failed to load heatmap for year ${year}.</p>`;
        };
    };

    yearSlider.addEventListener("input", () => {
        const year = yearSlider.value;
        yearDisplay.textContent = year;
        updateHeatmap(year);
    });

    // Initial load
    updateHeatmap(yearSlider.value);
});
