triggers = {}
events = {}
alert=false

String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x > y) ? -1 : ((x < y) ? 1 : 0));
    });
}

function procData(){
    console.log('START DATA')

    $.ajax({
        type: "GET",
        url: "/monitoring/?q=getTriggered",
        cache: false,
        success: function (res) {
            triggers = res
        },
        error: function(err) {
            console.log(err)
        },


        complete: function(){
            $.ajax({
                type: "GET",
                url: "/monitoring/?q=getEvents&p=1&l=0",
                cache: false,
                success: function (res) {
                    events = res
                },
                error: function(err) {
                    console.log(err)
                },
                complete: function(){
                    alert=false
                    setProblems()
                    setEvents()
                    if (alert == true){
                        document.getElementById('xyz').play();
                    }
                    poll()
                },
            });

        },
    });
}

function setEvents(){

    var otherInfo = document.getElementById('otherInfo')
    var hCount = document.getElementById('problemsPerHostgroupBody')
    var hHcount = {}
    var count = []
    var now = Date.now()

    var tbody = ''
    for (var k in events['data']){
        var etime = new Date(events['data'][k]['clock'])
        var secs = (Math.abs(now-etime))/1000
        var cls = ''
        //console.log(secs)
        if (secs < 600){
            cls = 'blink'
        }

        if (events['data'][k]['severity'] == 1){
            tbody = tbody + '<tr class="{0}">'.format(cls)
            tbody = tbody + '    <td><small>{0}</small></td>'.format(events['data'][k]['ip'])
            tbody = tbody + '    <td><small>{0}</small></td>'.format(events['data'][k]['groupname'])
            tbody = tbody + '    <td><small>{0}</small></td>'.format(events['data'][k]['clock'])
            tbody = tbody + '    <td><small>{0}</small></td>'.format(events['data'][k]['name'])
            tbody = tbody + '</tr>'
        }

        else{
            if (!hHcount.hasOwnProperty(events['data'][k]['groupname'])){
                hHcount[events['data'][k]['groupname']]=0
            }
            hHcount[events['data'][k]['groupname']]++
        }

    }
    otherInfo.innerHTML = tbody
    tbody = ''
    for (var k in hHcount){
        count.push({
            'name':k,
            'count':hHcount[k]
        })
    }

    count = sortByKey(count,'count')

    for (var k in count){
        tbody = tbody + '<tr>'
        tbody = tbody + '    <td><small>{0}</small></td>'.format(count[k]['name'])
        tbody = tbody + '    <td  style="color:red"> <i class="fa fa-level-up"></i> {0} </td>'.format(count[k]['count'])
        tbody = tbody + '</tr>'
    }
    hCount.innerHTML = tbody


}

function setProblems(){
    var pBody = document.getElementById('problemsBody')
    var wBody = document.getElementById('warnBody')
    var pCount = document.getElementById('problemsEncountered')

    pBody.innerHTML=''
    wBody.innerHTML=''

    for (var k in triggers['data']){
        var widget = createAlertWidget(triggers['data'][k])

        if (triggers['data'][k]['severity'] < 4 && triggers['data'][k]['severity'] > 1){
            wBody.innerHTML= wBody.innerHTML + widget
        }

        else if (triggers['data'][k]['severity'] >3 ){
            pBody.innerHTML= pBody.innerHTML + widget
        }
    }

    if (wBody.innerHTML == ''){
        var wid = '         <div id="warn-ok">'
        wid = wid +'            <div class="widget navy-bg p-lg text-center">'
        wid = wid +'                <div class="m-b-md">'
        wid = wid +'                    <h1 class="m-xs">No Warnings <i class="fa fa-check"></i></h1>'
        wid = wid +'                </div>'
        wid = wid +'            </div>'
        wid = wid +'        </div>'
        wBody.innerHTML= wBody.innerHTML + wid
    }

    if (pBody.innerHTML == ''){
        var wid = '         <div id="warn-ok">'
        wid = wid +'            <div class="widget navy-bg p-lg text-center">'
        wid = wid +'                <div class="m-b-md">'
        wid = wid +'                    <h1 class="m-xs">No Problems <i class="fa fa-check"></i></h1>'
        wid = wid +'                </div>'
        wid = wid +'            </div>'
        wid = wid +'        </div>'
        pBody.innerHTML= pBody.innerHTML + wid
    }
}

function createAlertWidget(data){
    var color = 'red'

    if (data['severity'] < 4){
        color = 'yellow'
    }
    else {
        color = 'red'
        alert=true
    }
    var widget = '<div class="widget style1 '+color+'-bg">'
    widget = widget + '<div class="row">'
    //widget = widget + '<div class="col-xs-1"><i class="fa fa-bell fa-4x"></i></div>'
    widget = widget + '<div class="col-xs-12 text-left"><h2 class="font-bold" style="font-size:40px"> '+data['name']+' </h2><hr/></div>'
    widget = widget + '<div class="col-xs-12 text-left"><h3 class="pull-left" style="font-size:35px"><i><b>IP: </b>'+data['ip']+'</i></h3></div>'
    widget = widget + '<div class="col-xs-12 text-left"><h3 class="pull-left" style="font-size:20px"><i><b>Hostname: </b>'+data['hostname']+'</i></h3></div>'
    widget = widget + '<div class="col-xs-12 text-left"><h3 class="pull-left" style="font-size:20px"><i><b>Group: </b>'+data['groupname']+'</i></h3></div>'
    widget = widget + '<div class="col-xs-12 text-left"><h3 class="pull-left" style="font-size:20px"><i><b>Alert Start: </b>'+data['clock']+'</i></h3></div>'
    widget = widget + '</div>'
    widget = widget + '</div>'
    return widget
}

function poll(){
   setTimeout(function(){
      procData()
  }, 30000);
}

procData()
startScrollwarn()
startScrollproblems()
function startScrollwarn(){
//if (scroll==true){
    $('#warnBody').scrollTop(0);
    $('#warnBody').animate({
        scrollTop: $('#warnBody')[0].scrollHeight,
    },{duration: 30000,queue: false,});
    $('#warnBody').promise().done(function(){
        startScrollwarn()
    });
//}

}

function startScrollproblems(){
//if (scroll==true){
    $('#problemsBody').scrollTop(0);
    $('#problemsBody').animate({
        scrollTop: $('#problemsBody')[0].scrollHeight,
    },{duration: 30000,queue: false,});
    $('#problemsBody').promise().done(function(){
        startScrollproblems()
    });
//}

}




setInterval(function(){
    var elements = document.getElementsByClassName("blink");
    for(var i = elements.length - 1; i >= 0; --i){
        if (elements[i].getAttribute("style") == null){
            elements[i].style.backgroundColor ='#1ab394'
        }
        else {
            elements[i].removeAttribute('style')
        }
    }

}, 1500);
