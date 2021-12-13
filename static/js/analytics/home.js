var ctx = document.getElementById("myChart").getContext('2d');



jsonUrl='https://argus.omtools.me/static/jsontest/XBET.json'

var datashit = $.ajax({
    url: jsonUrl,
    async: false,
    dataType: 'json'
}).responseJSON;
console.log(datashit)

var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: datashit['13.75.95.167']['connections']['check_time'],
        datasets: [{
            label: 'Active Connections',
            data: datashit['13.75.95.167']['connections']['data'],
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

