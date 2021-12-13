$('.input-daterange').datepicker({
                keyboardNavigation: false,
                forceParse: false,
                autoclose: true,
                format: 'mm/dd/yyyy',
                startDate: '08/01/2018',
                endDate: '+0d',
            });

var ctx = document.getElementById("myChart");
var myChart;

var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //January is 0!
var yyyy = today.getFullYear();

if(dd<10) {
    dd = '0'+dd
}

if(mm<10) {
    mm = '0'+mm
}

today = mm + '/' + dd + '/' + yyyy;

document.getElementById('start_date').value = today
document.getElementById('end_date').value = today



function getChartTemplate(title,ctype, labels, datasets, xlabel, ylabel){
    var t = {
        'type': ctype, //Assign Value
        'data': {
            'labels': labels,
            'datasets': datasets //Assign Value
        },
        'options': {

                'elements': {
                    'rectangle': {
                        'borderWidth': 2,
                    }
                },
                'responsive': true,
                'maintainAspectRatio':false,
                'legend': {
                    'position': 'right',
                },
                'title': {
                    'display': true,
                    'text': title
                },
                'scales': {
                    'xAxes': [{
                        'display': true,
                        'scaleLabel': {
                            'display': true,
                            'labelString': xlabel
                        }
                    }],
                    'yAxes': [{
                        'display': true,
                        'scaleLabel': {
                            'display': true,
                            'labelString': ylabel
                        }
                    }]
                }
            }
    }

    return t

}

function changeChart(){

    var start_date = document.getElementById('start_date').value
    var end_date = document.getElementById('end_date').value
    var q = document.getElementById('query').value
    var bu = document.getElementById('bu').value

    var dataString = encodeURI('bu='+bu+'&f=' + q +'&from='+start_date+'&to='+end_date);

    var time_interval = document.getElementById('time_interval').value
    var time_seg = document.getElementById('time_seg').value


    if (time_interval){
        dataString = dataString+'&interval='+time_interval+time_seg
    }


    $.ajax({
        type: "GET",
        url: window.location+'generate/',
        data: dataString,
        cache: false,
        success: function (data) {
            ctx.innerHTML=''
            if (myChart) {
                myChart.destroy();
            }
            document.getElementById('cwrapper').style.height = '62vh'
            if (data['type'] == 'horizontalBar'){
                if  (data['labels'].length < 20){
                    document.getElementById('cwrapper').style.height = '62vh'
                }

                else if (data['labels'].length < 40){
                    document.getElementById('cwrapper').style.height = '100vh'
                }

                else if (data['labels'].length < 60){
                    document.getElementById('cwrapper').style.height = '150vh'
                }

                else{
                    document.getElementById('cwrapper').style.height = '200vh'
                }
            }

            myChart = new Chart(ctx, getChartTemplate(data['title'],data['type'],data['labels'],data['datasets'],data['xlabel'],data['ylabel']));

        },
        error: function(err) {
            console.log(err);
            if (myChart) {
                myChart.destroy();
            }
        }
    });



}