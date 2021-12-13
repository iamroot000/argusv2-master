var ctx = document.getElementById("myChart").getContext('2d');


var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['13:00', '13:05', '13:15', '13:20', '13:25', '13:30', '13:35', '13:40', '13:45', '13:50','13:55', '14:00' ],
        datasets: [{
            label: 'Active Connecions',
            data: [12, 19, 3, 5, 2, 3,50, 19, 3, 5, 2, 3],
            backgroundColor: [
                'rgba(0, 0, 128, 0.2)',

            ],
            borderColor: [
                'rgba(255,99,132,1)',

            ],
            borderWidth: 3,
            //steppedLine:true,
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        }
    }
});

var ctx = document.getElementById("myChart2").getContext('2d');


var myChart2 = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['13:00', '13:05', '13:15', '13:20', '13:25', '13:30', '13:35', '13:40', '13:45', '13:50','13:55', '14:00' ],
        datasets: [{
            label: 'Active Connecions',
            data: [12, 19, 3, 5, 2, 3,50, 19, 3, 5, 2, 3],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',

            ],
            borderColor: [
                'rgba(255,99,132,1)',

            ],
            borderWidth: 1,
            //steppedLine:true,
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        }
    }
});