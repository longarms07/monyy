
/*
 * NET WORTH GRAPH
 */
var networth = new Chart(document.getElementById('chart-networth').getContext('2d'), {
    type: 'line',
    options: {
        title: {
            display: true,
            position: 'top',
            fontSize: 20,
            fontColor: "#373737",
            padding: 10,
            text: "Net Worth in USD"
        },
        legend: {
            display: false
        }
    },
    responsive: false,
    maintainAspectRatio: true,
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            data: [574389, 326574, 543908, 432678, 543897, 534896,
             594306, 434372, 543890, 543879, 543908, 526478],
        borderColor: "#1d1e22",
        backgroundColor: "rgb(0,0,0,0)"
        }]
    }
});

/*
 * STOCKS GRAPH
 */
var stocks = new Chart(document.getElementById('chart-stocks').getContext('2d'), {
    type: 'line',
    options: {
        title: {
            display: true,
            position: 'top',
            fontSize: 20,
            fontColor: "#373737",
            padding: 10,
            text: "Stock Closing Price"
        },
        legend: {
            display: false
        }
    },
    responsive: false,
    maintainAspectRatio: true,
    data: {
        labels: ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri'],
        datasets: [{
            data: [432.54, 567.45, 423.54, 333.45, 677.87,],
        borderColor: "#1d1e22",
        backgroundColor: "rgb(0,0,0,0)"
        }]
    }
});