data = {}
scroll = true
alert=false

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; 
        var y = b[key];
        return ((x > y) ? -1 : ((x < y) ? 1 : 0));
    });
}
String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};
function createAlertWidget(label, data){
    var color = 'red'
    alert=true
    var widget = '<div class="widget style1 '+color+'-bg">'
    widget = widget + '<div class="row">'
    widget = widget + '<div class="col-xs-1"><i class="fa fa-bell fa-4x"></i></div>'
    widget = widget + '<div class="col-xs-11 text-right"><h1 class="font-bold" style="font-size:40px"> '+data+' </h1>'
    widget = widget + '<h3 class="font-bold">'+label+'</h3>'
    widget = widget + '</div>'
    widget = widget + '</div>'
    widget = widget + '</div>'
    return widget
}

function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}

function displayData(data){
    alert = false
    var SOCKS5 = document.getElementById('SOCKS5-notok')
    var changesBody = document.getElementById('changesBody')
    var connectedBody = document.getElementById('connectedBody')


    SOCKS5.innerHTML =''
    changesBody.innerHTML =''
    connectedBody.innerHTML =''

    var fm = []

    var now = Date.now()
    for (var channel in data['history']){
        for (var series in data['history'][channel]){
            if (data['history'][channel][series].length == 0){
                fm.push({
                    'params':{},
                    'change':'N/A',
                    'type':'NO_ALERTS',
                    'time':series,
                    'channel':channel
                })
            }
            for (var event in data['history'][channel][series]){
                data['history'][channel][series][event]['channel'] = channel
                fm.push(data['history'][channel][series][event])
            }
        }
    }
    //console.log(fm)
    fm = sortByKey(fm,'time')
    var latest 
    if (fm.length !=0){
        
        for (var k in fm){
            if (!latest){
                latest = fm[k]['time']
            }

            var sdate = new Date(fm[k]['time'])
            if (fm[k]['type'] == 'ERROR_NO_OUTBOUND_CONNECTION'){
                var color = 'red'
                var icon = 'times'
                
            }
            else{
                var color = 'orange'
                var icon = 'flag'
            }
            if (fm[k]['type'] != 'NO_ALERTS'){
                var l = '<li>'
                l=l+'    <h4>'
                l=l+'        <strong>{0}</strong> - <i class="fa fa-{1}" style="color:{2}"></i> '.format(fm[k]['time'],icon,color)
                l=l+'        Channel: <strong>{0}</strong>'.format(fm[k]['channel'])
                l=l+'        Event: <strong>{0}</strong>'.format(fm[k]['type'])
                l=l+'        Message: <strong>{0}</strong> '.format(fm[k]['change'])
                l=l+'    </h4><hr/>'
                l=l+'</li>'
                changesBody.innerHTML= changesBody.innerHTML + l
                if (fm[k]['type'] == 'ERROR_NO_OUTBOUND_CONNECTION' && fm[k]['time']==data['time'][fm[k]['channel']]){
                    //console.log(latest)
                    alert = true
                    
                    SOCKS5.innerHTML = SOCKS5.innerHTML + createAlertWidget(
                        '{0} - {1}'.format(fm[k]['time'],fm[k]['type']),
                        '{0} - {1}'.format(fm[k]['channel'],fm[k]['change'])
                    )
                }
            }
        }
    }
    var connected_count = 0
    for (var channel in data['connected']){

        for (var ssname in data['connected'][channel]){
            var count = data['connected'][channel][ssname].length
            connected_count = connected_count + count
            var color = 'green'
            var bg = ''
            var flag = false
            if (count > 3){
                color = 'red'
                bg='orange'
                flag = true

            }
            var l = '<li style="background:{0}">'.format(bg)
                l=l+'    <h4>'
                l=l+'        Channel: <strong>{0}</strong>'.format(channel)
                l=l+'        Port: <strong>{0}</strong>'.format(ssname)
                l=l+'        Connected Clients: <strong style="color:{0}">{1}</strong> - {2} '.format(color,count,JSON.stringify(data['connected'][channel][ssname]))
                l=l+'    </h4><hr/>'
                l=l+'</li>'

            if (flag){
                 connectedBody.innerHTML=  l + connectedBody.innerHTML 
            }
            else{
                 connectedBody.innerHTML= connectedBody.innerHTML + l
            }
           

        }
    }
    document.getElementById('connected_count').innerHTML = connected_count
}


function procData(){
    //console.log('START DATA')
   alert = false

    $.ajax({
        type: "GET",
        url: "/proxycontroller/?q=getHistory",
        cache: false,
        success: function (res) {
            data = res
        },
        error: function(err) {
            //console.log(err)
        },
        complete: function(){
            displayData(data)

            if (alert === true){
                document.getElementById('xyz').play();
                document.getElementById('SOCKS5-ok').style.display='none'
            }
            else{
                document.getElementById('SOCKS5-ok').style.display='block'
            }
            poll()
        },
    });

}



function poll(){
   setTimeout(function(){
      procData()
  }, 15000);
}

$( document ).ready(function() {
    procData()
});
