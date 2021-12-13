domain_ranking_charts={}
domain_ranking_data_charts={}

overall_visits_charts={}
overall_visits_data_charts={}

from_date=''
to_date=''

function drawChartVERGIL(BU){;
    var options = {
        title: BU+' - Domain Rankings from '+ from_date +' to '+ to_date,
        colors:[color_production,color_marketing,color_other],
        animation:{
            duration: 1000,
            easing: 'out',
        },
    };
    domain_ranking_charts = new google.visualization.BarChart(document.getElementById(BU+'_domainrankingschart'));
    domain_ranking_charts.draw(domain_ranking_data_charts, options);

    var options = {
        title: BU+' - Overall Visits from '+ from_date +' to '+ to_date,
        colors:[color_production,color_marketing,color_other],
        lineWidth: 5,
        animation:{
            duration: 1000,
            easing: 'out',
        },
        legend: { position: 'bottom' },
        hAxis : {
            textStyle : {
                fontSize: 10 // or the number you want
            },
            title:'Time'
        },
        vAxis : {
            title:'Visits'
        }
    };
    overall_visits_charts = new google.visualization.AreaChart(document.getElementById(BU+'_overallvisits'));
    overall_visits_charts.draw(overall_visits_data_charts, options);
}



function generateChartsVERGIL(BU){

    $.ajax({
        type: "GET",
        url: "getvergilstats?BU="+BU,
        cache: false,
        success: function (data) {
           for (var k in data){
                var widget = '<div id="d_'+k+'" class="VERGIL_div">'
                    widget = widget + '<div class="row">'
                        widget = widget + '<div class="col-lg-12">'
                        widget = widget + '<div class="chart" id="'+k+'_domainrankingschart"></div>'
                        widget = widget + '</div>'
                        widget = widget + '<div class="col-lg-12">'
                        widget = widget + '<div class="chart" id="'+k+'_overallvisits"></div>'
                        widget = widget + '</div>'
                    widget = widget +'</div>'
                widget = widget +'</div>'
                from_date = data[k]['from']
                to_date = data[k]['to']
                content.innerHTML = content.innerHTML + widget
                domain_ranking_data_charts = google.visualization.arrayToDataTable(data[k]['function']['domain_rankings']);
                overall_visits_data_charts = google.visualization.arrayToDataTable(data[k]['function']['overall_visits']);
           }
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            drawChartVERGIL(BU)
        }
    });

}



