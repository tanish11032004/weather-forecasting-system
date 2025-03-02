// Create a new Chart.js chart for temperature forecast
const ctx = document.getElementById('chart').getContext('2d');

// Extract temperature data from the DOM
const tempElements = document.querySelectorAll('.forecast-temperatureValue');
const timeElements = document.querySelectorAll('.forecast_time');

// Create arrays for chart data
const tempData = [];
const timeLabels = [];

// Extract data from DOM elements
tempElements.forEach(element => {
    tempData.push(parseFloat(element.textContent));
});

timeElements.forEach(element => {
    timeLabels.push(element.textContent);
});

// Create the chart
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: timeLabels,
        datasets: [{
            label: 'Temperature (°C)',
            data: tempData,
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            borderColor: 'rgba(255, 255, 255, 0.7)',
            borderWidth: 2,
            tension: 0.3,
            pointBackgroundColor: 'rgba(255, 255, 255, 1)',
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                titleColor: 'white',
                bodyColor: 'white',
                borderColor: 'white',
                borderWidth: 1,
                displayColors: false
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: 'rgba(255, 255, 255, 0.7)'
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    color: 'rgba(255, 255, 255, 0.7)'
                }
            }
        }
    }
});