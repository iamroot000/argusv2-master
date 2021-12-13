google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(getData);


loc = $("#slocation").select2()
dom = $("#sdomain").select2();
color_production='#53f441'
color_marketing='#f44b42'
color_other='#cc1212'
color_default='#7a7a7a'

data_charts={}

content = document.getElementById('sChart')

$(document).ready(function(){
    $.ajax({
        type: "GET",
        url: window.location+'?q=GetDistinctDomains',
        cache: false,
        success: function (data) {
            for (var i=0;i<data['data'].length;i++){
                var op = {
                    id: data['data'][i],
                    text: data['data'][i],
                    value: data['data'][i],
                }
                var e = new Option(op.text, op.id, false, false);
                dom.append(e)
            }
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            var domain = document.getElementById('sdomain').value
            getLocation(domain)
        }
    });
});


function getLocation(domain){

    $("#slocation").empty();

    $.ajax({
        type: "GET",
        url: window.location+'?q=GetGroupsContainingDomain&d='+domain,
        cache: false,
        success: function (data) {
            for (var i=0;i<data['data'].length;i++){
                var op = {
                    id: data['data'][i],
                    text: data['data'][i],
                    value: data['data'][i],
                }
                var e = new Option(op.text, op.id, false, false);
                loc.append(e)
            }
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            getData()
        }
    });

}


function getData(){
    var sdomain = document.getElementById('sdomain').value
    var sloc = document.getElementById('slocation').value

    $.ajax({
        type: "GET",
        url: window.location+'?q=data&d='+sdomain+'&r='+sloc,
        cache: false,
        success: function (data) {
            console.log(data)
            content.innerHTML = ''

            var widget = '<div class="col-lg-12">'
            widget = widget + '<div class="chart" id="chartq"></div>'
            widget = widget + '</div>'

            var datas = new google.visualization.DataTable();
            datas.addColumn('string', 'Time');
            datas.addColumn('number', 'Inbound');
            datas.addColumn('number', 'Outbound');
            datas.addRows(data['data'])

            data_charts = datas

            content.innerHTML = widget
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            generateChart()
        }
    });
}

function generateChart(){
    var sdomain = document.getElementById('sdomain').value
    var sloc = document.getElementById('slocation').value
    var options = {
        title: 'Host: '+ sdomain + ' | Location: ' + sloc,
        colors:[color_production,color_marketing,color_other],

        legend: { position: 'bottom' },
        hAxis : {
            textStyle : {
                fontSize: 11, // or the number you want

            },
            slantedText:true,
                slantedTextAngle:60,

            title:'Time'
        },
        vAxis : {
            title:'Transmission (kB/s)',

        },
        //curveType: 'function',
    };
    charts =new google.visualization.LineChart(document.getElementById('chartq'));
    charts.draw(data_charts, options);
}


setInterval(function(){
getData()
}, 10000);


$(window).resize(function(){
        generateChart();

});