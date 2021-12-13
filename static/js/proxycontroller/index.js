String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; 
        var y = b[key];
        return ((x > y) ? -1 : ((x < y) ? 1 : 0));
    });
}

pagedata = {}
changesData = {}
COLUMNS = [
    {'title':'Channel','data':'channel'},
    {'title':'Local Port','data':'local_port'},
    {
        'data':'server',
        'title':'Server',
        'render':function ( data, type, row ) {
            return '<a style="font-weight:bold" value="'+data+'" onclick="showParams(\''+row['channel']+'\',\''+row['id']+'\')">'+data+' <i class="fa fa-info-circle"></i></a>'
        },
    },
    {'title':'Geolocation','data':'region'},
    {'title':'IDC','data':'idc'},
    {'title':'PID','data':'pid'}
]

serverlist = {}

socketsTable = $('#socketsTable').DataTable({
        pageLength: 20,
        aaSorting: [
            [ 1, "asc" ],

        ],
        //bLengthChange: false,
        autoWidth: false,
        columnDefs: [
                        { "width": "150px", "targets": 0 },
                        { "width": "100px", "targets": 1 },
                        //{ "width": "400px", "targets": 2 },
                        //{ "width": "60px", "targets": 3 },
                        //{ "width": "100px", "targets": 4 },
                      ],
        columns: COLUMNS,
        ajax:{
            url:'/proxycontroller/?q=getSockets',
            dataSrc:function ( json ) {
                pagedata = json
                var tableData = {
                    'data':[]
                }
                for (var k in json){
                    for (var p in json[k]){
                        if (!isEmpty(json[k][p])){
                            tableData['data'].push({
                                'channel':k,
                                'local_port':json[k][p]['params']['local_port'],
                                'server':json[k][p]['params']['server'],
                                'pid':json[k][p]['pid'],
                                'id':p,
                                'region':json[k][p]['region'],
                                'idc':json[k][p]['idc']
                            })
                        }
                    }
                }

                $.ajax({
                    type: "GET",
                    dataType: "json",
                    url: window.location+'?q=getServers',
                    success: function(result) {
                        serverlist['servers'] = result['servers']
                    },
                    error: function(err) {
                        console.log(err)
                    },
                    complete:function(){
                        for (var k in serverlist['servers']){
                            for (var l in tableData['data']){
                                if (tableData['data'][l]['server'] == serverlist['servers'][k]['server']){
                                    tableData['data'][l]['region'] = serverlist['servers'][k]['region']
                                }
                            }
                        }
                    }
               
                });

                console.log(tableData['data'])
                return tableData.data
            }
        }
    });


function getISP(){
    var ispbody = document.getElementById('isp')
    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getISP',
        success: function(result) {
            ispbody.innerHTML=''

            for (var channel in result['isp']){
                var ispdet = '<p><b>{0}: </b>{1}</p>'.format(channel,result['isp'][channel])
                ispbody.innerHTML = ispbody.innerHTML + ispdet
            }
        },
        error: function(err) {
            console.log(err)
        },


    });

}

$( document ).ready(function() {
    getChanges()
    getISP()
});

function poll(){
   setTimeout(function(){
      getChanges()
  }, 15000);
}



$(function () {
    $(".select2").select2();
});

function getChanges(){
    var changesBody = document.getElementById('changesBody')
    changesBody.innerHTML=''
    var fm = []
    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getHistory',
        success: function(result) {
            for (var channel in result['history']){
                for (var series in result['history'][channel]){
                    for (var event in result['history'][channel][series]){
                        result['history'][channel][series][event]['channel'] = channel
                        fm.push(result['history'][channel][series][event])
                    }
                }
            }
            fm = sortByKey(fm,'time')
            for (var k in fm){
      
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

                }
            }
        },
        error: function(err) {
            console.log(err)
        },
        complete:function(){
            poll()
        }
   
    });

}

function openDomainInfo(domain){
        window.open('/domains/'+domain,'newwindow','width=1000,height=700')
        return false;
}


function showParams(channel,id){

    console.log(pagedata[channel][id])

    var configPanel = document.getElementById('configBody')
    configPanel.innerHTML =''
    var clientTable = document.createElement('table')
    clientTable.className = 'table table-responsive'
    var tbody = document.createElement('tbody')



    var tr = document.createElement('tr')
    var td = document.createElement('td')

    td.innerHTML = 'PID'
    td.style.fontWeight='bold'
    tr.appendChild(td)
    var td = document.createElement('td')
    td.innerHTML = JSON.stringify(pagedata[channel][id]['pid'])
    tr.appendChild(td)


    tbody.appendChild(tr)


    for (var k in pagedata[channel][id]['params']){

        var tr = document.createElement('tr')
        var td = document.createElement('td')
        td.innerHTML = k
        td.style.fontWeight='bold'
        tr.appendChild(td)


        var td = document.createElement('td')
        td.innerHTML = pagedata[channel][id]['params'][k]
        tr.appendChild(td)

        tbody.appendChild(tr)

    }

    clientTable.appendChild(tbody)
    configPanel.appendChild(clientTable)

    var closeClientButton = document.createElement('button')
    closeClientButton.className = 'btn btn-danger btn-md'
    closeClientButton.innerHTML = '<i class="fa fa-stop-circle"></i> Close Client'
    closeClientButton.setAttribute('onclick','closeClient("'+channel+'","'+id+'")')

    var restartClientButton = document.createElement('button')
    restartClientButton.className = 'btn btn-primary btn-md pull-right'
    restartClientButton.innerHTML = '<i class="fa fa-sync"></i> Restart Client'
    restartClientButton.setAttribute('onclick','restartClient("'+channel+'","'+id+'")')

    var logsClientButton = document.createElement('a')
    logsClientButton.className = 'btn btn-default btn-md pull-right'
    logsClientButton.innerHTML = '<i class="fa fa-book"></i> SSR Client Log'
    logsClientButton.setAttribute('href','/proxycontroller/?q=getLogs&c={0}&s={1}'.format(channel,id))
    logsClientButton.setAttribute('target','_blank')

    var activitiesClientButton = document.createElement('a')
    activitiesClientButton.className = 'btn btn-default btn-md pull-right'
    activitiesClientButton.innerHTML = '<i class="fa fa-book"></i> Activity Log'
    activitiesClientButton.setAttribute('href','/proxycontroller/?q=getActivity&c={0}&s={1}'.format(channel,id))
    activitiesClientButton.setAttribute('target','_blank')

    configPanel.appendChild(closeClientButton)
    configPanel.appendChild(restartClientButton)
    configPanel.appendChild(logsClientButton)
    configPanel.appendChild(activitiesClientButton)



}


function closeClient(channel,id){
    console.log('close',channel,id)
    var rbody = {
        'close':{
            'channel':channel
        }
    }
    if (Array.isArray(id)){
        rbody['close']['id'] = id
        var prompt = true


    }
    else{
        rbody['close']['id']=[id]
        var prompt = confirm('Close Client Channel: {0} Port {1}?'.format(channel,id))
    }

    if (prompt){
        var configPanel = document.getElementById('configBody')
        configPanel.innerHTML ='<center><img src="/static/img/fluid-loader.gif"></center>'
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location+'process/',
            data: JSON.stringify(rbody),
            success: function(result) {
                configPanel.innerHTML ='<i class="fa fa-check" style="color:green"></i> Client: {0}, Channel: {1} - Closed'.format(id,channel)
                console.log(result)
                socketsTable.ajax.reload();
            },

            error: function(err) {
                configPanel.innerHTML ='<i class="fa fa-times" style="color:red"></i> Client: {0}, Channel: {1} Error in closing Client'.format(id,channel)
            },
       
        });
    }
    
}

function restartClient(channel,id){
    console.log('restart',channel,id)
    var rbody = {
        'restart':{
            'channel':channel
        }
    }
    if (Array.isArray(id)){
        rbody['restart']['id'] = id
        var prompt = true
    }
    else{
        rbody['restart']['id']=[id]
        var prompt  = confirm('Restart Client Channel: {0} Port {1}?'.format(channel,id))
    }
    
    if (prompt){
        console.log(rbody)

        var configPanel = document.getElementById('configBody')
        configPanel.innerHTML ='<center><img src="/static/img/fluid-loader.gif"></center>'
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location+'process/',
            data: JSON.stringify(rbody),
            success: function(result) {
                configPanel.innerHTML = '<i class="fa fa-check" style="color:green"></i> Client: {0}, Channel: {1} - Restarted'.format(id,channel)
                console.log(result)
                socketsTable.ajax.reload();
            },

            error: function(err) {
                configPanel.innerHTML ='<i class="fa fa-times" style="color:red"></i> Client: {0}, Channel: {1} Error in restarting Client'.format(id,channel)
            },
       
    });


    }
    
}

function restartAllClients(){
    console.log('restartAll')


    var prompt1 = confirm('Restart All Running Clients?')
    var prompt2 = false
    if (prompt1){
        prompt2 = confirm("Confirm Action (This is logged)")
    }

    if (prompt2){
        var rbody = {
            'restartAll':{}
        }

        $.ajax({
            type: "GET",
            dataType: "json",
            url: window.location+'?q=getSockets',

            success: function(result) {
                for (var channel in result){
                    for (var id in result[channel]){
                        if (!isEmpty(result[channel][id])){
                            if (!rbody['restartAll'].hasOwnProperty(channel)){
                            rbody['restartAll'][channel]={
                                'id':[]
                            }
                        }
                        rbody['restartAll'][channel]['id'].push(id)
                    }
                        
                    }
                }

                for (var channel in rbody['restartAll']){
                    restartClient(channel,rbody['restartAll'][channel]['id'])
                }
            },
            error: function(err) {
                console.log(result)
            },

        });

    }

}


function startClient(){
  
    var server = document.getElementById('server_address').value
    var channel_new = document.getElementById('channel').value
    var localport = document.getElementById('local_port').value
    var configPanel = document.getElementById('configBody')

    var flag = true
    var prompt = false
    for (var channel in pagedata){
        for (var ssid in pagedata[channel]){
            if (!isEmpty(pagedata[channel][ssid])){
                if (pagedata[channel][ssid]['params']['server'] == server ){
                    var prompt = confirm('This server is already allocated for Port: {0} Channel {1}. Creating multiple clients for a single SSR Server may produce undesirable results, continue?'.format(pagedata[channel][ssid]['params']['local_port'],channel))
                    if (prompt){
                        flag = true
                    }
                    else{
                        flag = false
                    }
                    break
                }
            }
        }
    }
    console.log(flag)
    if (flag){
        var rbody = {
            'start':{
                'channel':channel_new,
                'local_port':parseInt(localport),
                'server':server
            }
        }

        if(prompt){
            rbody['bypass'] = true
        }

        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location+'process/',
            data: JSON.stringify(rbody),
            success: function(result) {
                if (result['result'][0] == true){
                    configPanel.innerHTML ='<i class="fa fa-check" style="color:green"></i> Client: {0}, Channel: {1}, Server: {2} - Created'.format(localport,channel,server)
                    socketsTable.ajax.reload();
                }
                else {
                    configPanel.innerHTML ='<i class="fa fa-times" style="color:red"></i> Client: {0}, Channel: {1}, Server: {2} - Error: {3}'.format(localport,channel,server,result['result'][1])
                }
                console.log(result)
            },

            error: function(err) {
                alert('SERVER ERROR!')
            },
       
        });

        $('#clientModal').modal('hide');

        console.log('RESULT')

        console.log(rbody)

    }
    
}

function changeClient(){
  
    var server = document.getElementById('server_address').value
    var channel = document.getElementById('channel').value
    var localport = document.getElementById('local_port').value
    var configPanel = document.getElementById('configBody')

    closeClient(channel,'ss{0}'.format(localport))

    startClient()

}

function startClientModal(){
    $('#clientModal').modal('show');

    var servers = document.getElementById('server_address')
    var channels = document.getElementById('channel')
    var localports = document.getElementById('local_port')
    var applyChanges = document.getElementById('applyChanges')
    applyChanges.setAttribute('onclick','startClient()')

    servers.innerHTML=''
    channels.innerHTML=''
    localports.innerHTML=''

    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getServers',
        success: function(result) {
            for (var i=0;i<result['servers'].length;i++){
                var option = document.createElement('option')
                option.text = "{0} - {1} - {2} - {3}".format(result['servers'][i]['server'],result['servers'][i]['region'],result['servers'][i]['idc'],result['servers'][i]['status'])
                option.value = result['servers'][i]['server']

                servers.appendChild(option)
            }
        },
        error: function(err) {
            console.log(result)
        },
    });

    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getChannels',
        success: function(result) {
            for (var i=0;i<result['channels'].length;i++){
                var option = document.createElement('option')
                option.text = "{0} - {1}".format(result['channels'][i]['celery_queue'],result['channels'][i]['local_address'])
                option.value = result['channels'][i]['celery_queue']

                channels.appendChild(option)
            }
        },
        error: function(err) {
            console.log(result)
        },
   
    });

    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getPortRange',
        success: function(result) {
            for (var i=result['portrange']['min'];i<=result['portrange']['max'];i++){
                var option = document.createElement('option')
                option.text = i
                option.value = i

                localports.appendChild(option)

            }
        },
        error: function(err) {
            console.log(result)
        },
   
    });



}   


function changeClientModal(channel,id){
    $('#clientModal').modal('show');

    var servers = document.getElementById('server_address')
    var channels = document.getElementById('channel')
    var localports = document.getElementById('local_port')
    var applyChanges = document.getElementById('applyChanges')
    applyChanges.setAttribute('onclick','changeClient()')
    servers.innerHTML=''
    channels.innerHTML=''
    localports.innerHTML=''

    var selectedport = id.replace('ss','')

    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getServers',
        success: function(result) {
            for (var i=0;i<result['servers'].length;i++){
                var option = document.createElement('option')
                option.text = "{0} - {1}".format(result['servers'][i]['server'],result['servers'][i]['region'])
                option.value = result['servers'][i]['server']

                servers.appendChild(option)
            }
        },
        error: function(err) {
            console.log(result)
        },
    });

    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getChannels',
        success: function(result) {
            for (var i=0;i<result['channels'].length;i++){
                var option = document.createElement('option')
                option.text = "{0} - {1}".format(result['channels'][i]['celery_queue'],result['channels'][i]['local_address'])
                option.value = result['channels'][i]['celery_queue']

                channels.appendChild(option)
            }
        },
        error: function(err) {
            console.log(result)
        },
   
    });

    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getPortRange',
        success: function(result) {
            for (var i=result['portrange']['min'];i<=result['portrange']['max'];i++){
                var option = document.createElement('option')
                option.text = i
                option.value = i

                if (parseInt(selectedport) === i){
                    option.setAttribute ("selected", true);
                }
                localports.appendChild(option)
            }
        },
        error: function(err) {
            console.log(result)
        },
    });

    

}   

