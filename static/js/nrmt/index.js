data = {}
scroll = true
alert=false
function createAlertWidget(label, data){
    var color = 'red'
    for (var k in data){
        if (data[k]['code'] == 1){
            color = 'yellow'

        }
        else if (data[k]['code'] == 2 || data[k]['code'] == 99999 ){
            color = 'red'
            alert=true
            break
        }

    }

    var widget = '<div class="widget style1 '+color+'-bg">'
    widget = widget + '<div class="row">'
    widget = widget + '<div class="col-xs-1"><i class="fa fa-bell fa-4x"></i></div>'
    widget = widget + '<div class="col-xs-11 text-right"><h1 class="font-bold" style="font-size:50px"> '+label+' </h1>'
    for (var k in data){
        widget = widget + '<h2 class="font-bold">'+k+' - '+data[k]['result']+'</h2>'
    }
    widget = widget + '</div>'
    widget = widget + '</div>'
    widget = widget + '</div>'
    return widget
}

function createZGraph(graphID){
    var widget = '<img class="img-fluid" style="width:100%" src="https://argus.omtools.me/nrmt/data/graph/'+ graphID.toString() +'?x='+Math.random()+'">'
    return widget

}
function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}

function displayData(){
    var d = document.getElementsByClassName('notok')
    var ts_nrpe = document.getElementById('ts-nrpe')
    //console.log(ts_sf)
    //console.log(data['SERVICES']['timestamp'])
    var now = Date.now()
    var t_sf = new Date(data['SERVICES']['timestamp'])
    var t_nrpe = new Date(data['PHYSICAL']['timestamp'])

    ts_nrpe.innerHTML=data['PHYSICAL']['timestamp']
    console.log((Math.abs(now-t_sf))/1000)


    if ((Math.abs(now-t_nrpe))/1000 > 300 ){
        document.getElementById('ts-nrpe-time').className = 'widget style1 red-bg'
    }

    else {
        document.getElementById('ts-nrpe-time').className = 'widget style1 navy-bg'

    }

    for (var i=0;i<d.length;i++){
        var t=d[i].id

        if (!isEmpty(data[t]['data'])){
            document.getElementById(t+'-ok').style.display = 'none'
            //console.log(t)
            //console.log(d[i])

            d[i].style.display = 'block'
            d[i].innerHTML=''
            for (var ip in data[t]['data']){
                d[i].innerHTML = d[i].innerHTML + createAlertWidget(ip, data[t]['data'][ip])
                for (var ct in data[t]['data'][ip]){
                    if(data[t]['data'][ip][ct].hasOwnProperty('graph')){
                        d[i].innerHTML = d[i].innerHTML + createZGraph(data[t]['data'][ip][ct]['graph'])
                    }
                }
                }

        }
        else{
            d[i].style.display = 'none'
            document.getElementById(t+'-ok').style.display = 'block'
        }

    }
}

function startScrollDATABASE(){
if (scroll==true){
    $('#nrmt-DATABASE').scrollTop(0);

    $('#nrmt-DATABASE').animate({
        scrollTop: $('#nrmt-DATABASE')[0].scrollHeight,
        },  { duration: 30000, queue: false });

    $('#nrmt-DATABASE').promise().done(function(){
        startScrollDATABASE()
    });
}


}

function startScrollCLOUDSERVER(){
if (scroll==true){
    $('#nrmt-CLOUDSERVER').scrollTop(0);

    $('#nrmt-CLOUDSERVER').animate({
        scrollTop: $('#nrmt-CLOUDSERVER')[0].scrollHeight,
        }, { duration: 30000, queue: false });

    $('#nrmt-CLOUDSERVER').promise().done(function(){
        startScrollCLOUDSERVER()
    });
}


}



function startScrollPHYSICAL(){
if (scroll==true){
    $('#nrmt-PHYSICAL').scrollTop(0);

    $('#nrmt-PHYSICAL').animate({
        scrollTop: $('#nrmt-PHYSICAL')[0].scrollHeight,
        }, { duration: 30000, queue: false });

    $('#nrmt-PHYSICAL').promise().done(function(){
        startScrollPHYSICAL()
    });
}


}


function startScrollSERVICES(){
if (scroll==true){
    $('#nrmt-SERVICES').scrollTop(0);
    $('#nrmt-SERVICES').animate({
        scrollTop: $('#nrmt-SERVICES')[0].scrollHeight,
        },{duration: 30000,queue: false,});

        $('#nrmt-SERVICES').promise().done(function(){
        startScrollSERVICES()
    });
}

}




function procData(){
    console.log('START DATA')
   alert = false

    $.ajax({
        type: "GET",
        url: "/nrmt/data/",
        cache: false,
        success: function (res) {
            data = res
        },
        error: function(err) {
            console.log(err)
        },
        complete: function(){
            displayData(data)
                console.log('END DATA')
            if (alert == true){
                document.getElementById('xyz').play();

            }

            poll()
        },
    });

}

function scrollSet(){
    console.log(scroll)
    if (scroll == false){
        startScroll()

    }

    else {
        scroll = false
        $('#nrmt-PHYSICAL').stop()
        $('#nrmt-DATABASE').stop()
        $('#nrmt-CLOUDSERVER').stop()
        $('#nrmt-SERVICES').stop()
    }



}

function startScroll(){
    scroll = true
    startScrollDATABASE()
    startScrollPHYSICAL()
    startScrollCLOUDSERVER()
    startScrollSERVICES()
}

function poll(){
   setTimeout(function(){
      procData()
  }, 30000);
}

procData()
startScroll()