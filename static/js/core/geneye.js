domains_charts ={}
domains_data_charts ={}
server_util_charts={}
server_util_data_charts={}
sp_util_charts={}
sp_util_data_charts={}


function drawChartEYE(BU){;
    var options = {
        title: BU+' - Domains',
        colors:[color_production,color_marketing,color_other],
        animation:{
            duration: 1000,
            easing: 'out',
        },
    };
    domains_charts = new google.visualization.PieChart(document.getElementById(BU+'_domtypechart'));
    domains_charts.draw(domains_data_charts, options);

    var options = {
        title: BU+' - Domain - Server Utilization (Managed Servers)',
        colors:[color_default,color_production,color_marketing,color_other],
        is3D: true,
        animation:{
            duration: 1000,
            easing: 'out',
        },
    };
    server_util_charts = new google.visualization.BarChart(document.getElementById(BU+'_serverutilchart'));
    server_util_charts.draw(server_util_data_charts, options);

    var options = {
        title: BU+' - Cloud Service Providers',
        is3D: true,
        animation:{
            duration: 1000,
            easing: 'out',
        },
    };
    sp_util_charts = new google.visualization.PieChart(document.getElementById(BU+'_sputilchart'));
    sp_util_charts.draw(sp_util_data_charts, options);
}



function generateChartsEYE(BU){

    $.ajax({
        type: "GET",
        url: "geteyestats?BU="+BU,
        cache: false,
        success: function (data) {
            console.log(data)
           for (var k in data){
                var widget = '<div id="d_'+k+'" class="eye_div">'
                            widget = widget + '<div class="row">'
                                widget = widget + '<div class="col-lg-4">'
                                       widget = widget + '<div class="widget style1 lazur-bg">'
                                           widget = widget + '<div class="row">'
                                               widget = widget + '<div class="col-xs-4">'
                                                   widget = widget + '<i class="fa fa-cloud fa-4x"></i>'
                                               widget = widget + '</div>'
                                               widget = widget + '<div class="col-xs-8 text-right">'
                                                   widget = widget + '<h4> '+ k +' Domains </h4>'
                                                   widget = widget + '<h2 class="font-bold">'+data[k]['domains']+'</h2>'
                                               widget = widget + '</div>'
                                           widget = widget + '</div>'
                                    widget = widget + '</div>'
                                widget = widget + '</div>'
                                widget = widget + '<div class="col-lg-4">'
                                    widget = widget + '<div class="widget style1 navy-bg">'
                                           widget = widget + '<div class="row">'
                                               widget = widget + '<div class="col-xs-4">'
                                                   widget = widget + '<i class="fa fa-server fa-4x"></i>'
                                               widget = widget + '</div>'
                                               widget = widget + '<div class="col-xs-8 text-right">'
                                                   widget = widget + '<h4> '+ k +' Cloud Servers </h4>'
                                                   widget = widget + '<h2 class="font-bold">'+data[k]['server_count']+'</h2>'
                                               widget = widget + '</div>'
                                           widget = widget + '</div>'
                                    widget = widget + '</div>'
                                widget = widget + '</div>'
                                widget = widget + '<div class="col-lg-4">'
                                        if (data[k]['unmanaged_domain_count'] > 0){
                                           widget = widget + '<div class="widget yellow-bg p-lg text-center">'
                                               widget = widget + '<div class="m-b-md">'
                                                   widget = widget + '<i class="fa fa-bell fa-4x"></i>'
                                                   widget = widget + '<h1 class="m-xs">'+data[k]['unmanaged_domain_count']+'</h1>'
                                                   widget = widget + '<h4 class="font-bold no-margins">Unmanaged Domain(s) - '+ k +'</h4>'
                                               widget = widget + '</div>'
                                           widget = widget + '</div>'
                                        }
                                        else {
                                    widget = widget + '<div class="widget navy-bg p-lg text-center">'
                                           widget = widget + '<div class="m-b-md">'
                                               widget = widget + '<i class="fa fa-check fa-4x"></i>'
                                               widget = widget + '<h1 class="m-xs">0</h1>'
                                               widget = widget + '<h4 class="font-bold no-margins">Unmanaged Domain(s) - '+ k +'</h4>'
                                           widget = widget + '</div>'
                                    widget = widget + '</div>'
                                        }
                                 widget = widget + '</div>'
                            widget = widget + '</div>'
                                widget = widget + '<div class="col-lg-6">'
                                    widget = widget + '<div class="chart" id="'+k+'_serverutilchart"></div>'
                                widget = widget + '</div>'
                                widget = widget + '<div class="col-lg-6">'
                                    widget = widget + '<div class="chart" id="'+k+'_domtypechart"></div>'
                                widget = widget + '</div>'

                                widget = widget + '<div class="col-lg-6">'
                                    widget = widget + '<div class="chart" id="'+k+'_sputilchart"></div>'
                                widget = widget + '</div>'

                widget = widget +'</div>'

                content.innerHTML = content.innerHTML + widget
                domains_data_charts = google.visualization.arrayToDataTable([
                  ['Domains Types', 'Amount'],
                  ['Production',     data[k]['PROD_domains']],
                  ['Marketing',       data[k]['MKT_domains']],
                  ['Other',   data[k]['OTH_domains']],

                ]);


                data[k]['server_utilization'].unshift(['Server IP', 'Total Domains','Production','Marketing','Other'])
                server_util_data_charts = google.visualization.arrayToDataTable(data[k]['server_utilization'])

                var dt = [
                    ['Service Provider', 'Servers'],
                ]

                for (var l in data[k]['sp_utilization']){
                    var ar = []
                    ar.push(l)
                    ar.push(data[k]['sp_utilization'][l])
                    dt.push(ar)
                }
                sp_util_data_charts = google.visualization.arrayToDataTable(dt)
           }
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            drawChartEYE(BU)
        }
    });

}

