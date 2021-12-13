$(document).ready(function(){
    $("#hostgroup_filter").select2();

    $('#jstree1').jstree({
        'core' : {
            'data' : getData('JINSHENG_TIANHE')
        }
    });
});

function getData(hostgroup){
    var returnHtml = {};
    $.ajax({
        type: "GET",
        url: '/provisioner/hostgroup/'+hostgroup,
        async:false,
        cache: false,
        success: function(html){
            returnHtml = html;
        }
    });
    return returnHtml;
}

function getConfig(domain,hostgroup){
    var returnHtml = {};
    $.ajax({
        type: "GET",
        url: '/provisioner/config/'+hostgroup+'/'+domain,
        async:false,
        cache: false,
        success: function(html){
            returnHtml = html;
        }
    });
    return returnHtml;
}

function showConfig(config){
    document.getElementById('tab-raw-pre').innerHTML = config['raw']

    out = {}
    console.log(config['config'])


    for (var key in config['config']){
        divpanel = document.createElement('div')
        divpanel.className = 'panel panel-default'

        panel = document.createElement('div')
        panel.className = 'panel-body'

        portLabel = document.createElement('h3')
        portLabel.innerHTML = " Listening Port: "+key

        divpanel.appendChild(portLabel)

        for (var i = 0; i < config['config'][key].length; i++) {

            row = document.createElement('div')
            row.setAttribute('class','row')


            serverNameDiv = document.createElement('div')
            serverNameDiv.setAttribute('class','col-lg-3')
            serverName = document.createElement('input')
            serverName.className='form-control'
            serverName.setAttribute('id',key+'-'+config['config'][key][i]['serverName'])
            serverName.setAttribute('style','font-weight:bold;')
            serverName.value = config['config'][key][i]['serverName']
            serverNameLabel = document.createElement('label')
            serverNameLabel.innerHTML='Server Name'
            serverNameDiv.appendChild(serverNameLabel)
            serverNameDiv.appendChild(serverName)
            row.appendChild(serverNameDiv)


            if (key != '80') {

                certPathDiv = document.createElement('div')
                certPathDiv.setAttribute('class','col-lg-4')
                certPath = document.createElement('input')
                certPath.className='form-control'
                certPath.setAttribute('id',key+'-'+config['config'][key][i]['certPath'])
                certPath.value = config['config'][key][i]['certPath']
                certPathLabel = document.createElement('label')
                certPathLabel.innerHTML='Certificate Path'
                certPathDiv.appendChild(certPathLabel)
                certPathDiv.appendChild(certPath)
                row.appendChild(certPathDiv)

                keyPathDiv = document.createElement('div')
                keyPathDiv.setAttribute('class','col-lg-4')
                keyPath = document.createElement('input')
                keyPath.className='form-control'
                keyPath.setAttribute('id',key+'-'+config['config'][key][i]['keyPath'])
                keyPath.value = config['config'][key][i]['keyPath']
                keyPathLabel = document.createElement('label')
                keyPathLabel.innerHTML='Private Key Path'
                keyPathDiv.appendChild(keyPathLabel)
                keyPathDiv.appendChild(keyPath)
                row.appendChild(keyPathDiv)
            }


			rewriteSourceDiv = document.createElement('div')
            rewriteSourceDiv.setAttribute('class','col-lg-4')
            rewriteSource = document.createElement('input')
            rewriteSource.className='form-control'
            rewriteSource.setAttribute('id',key+'-'+config['config'][key][i]['rewriteSource'])
            rewriteSource.value = config['config'][key][i]['rewriteSource']
            rewriteSourceLabel = document.createElement('label')
            rewriteSourceLabel.innerHTML='Rewrite Source'
            rewriteSourceDiv.appendChild(rewriteSourceLabel)
            rewriteSourceDiv.appendChild(rewriteSource)
            row.appendChild(rewriteSourceDiv)

            rewriteDestDiv = document.createElement('div')
            rewriteDestDiv.setAttribute('class','col-lg-4')
            rewriteDest = document.createElement('input')
            rewriteDest.className='form-control'
            rewriteDest.setAttribute('id',key+'-'+config['config'][key][i]['rewriteDest'])
            rewriteDest.value = config['config'][key][i]['rewriteDest']
            rewriteDestLabel = document.createElement('label')
            rewriteDestLabel.innerHTML='Rewrite Destination'
            rewriteDestDiv.appendChild(rewriteDestLabel)
            rewriteDestDiv.appendChild(rewriteDest)
            row.appendChild(rewriteDestDiv)

            includeNameDiv = document.createElement('div')
            includeNameDiv.setAttribute('class','col-lg-3')
            includeName = document.createElement('input')
            includeName.className='form-control'
            includeName.setAttribute('id',key+'-'+config['config'][key][i]['includeName'])
            includeName.value = config['config'][key][i]['includeName']
            includeNameLabel = document.createElement('label')
            includeNameLabel.innerHTML='Include Config'
            includeNameDiv.appendChild(includeNameLabel)
            includeNameDiv.appendChild(includeName)
            row.appendChild(includeNameDiv)


            line = document.createElement('hr')


            panel.appendChild(row)
            panel.appendChild(line)

            //serverNameLabel = document.createElement('label')
            //serverNameLabel.setAttribute('for')


        }

        divpanel.appendChild(panel)
        document.getElementById('tab-config').appendChild(divpanel)
    }

    /*for (var i = 0; i < config['config'].length; i++) {
        console.log(config['config'][i])


        //document.getElementById('tab-config').appendChild(inp)
    }*/




}

function reloadTree(elem){
    console.log(elem)

}

$('#jstree1').on('changed.jstree', function (e, data) {
    var i, j, r = [];
    for(i = 0, j = data.selected.length; i < j; i++) {
        r.push(data.instance.get_node(data.selected[i]).text);
    }
    dom = r.join(', ')
    hostgroup = document.getElementById('hostgroup_filter').value
    document.getElementById('tab-raw-pre').innerHTML = ''
    document.getElementById('tab-config').innerHTML = ''
    if (dom == 'Root Hosts' || dom == 'Configs' || dom == hostgroup){
    }
    else{
        showConfig(getConfig(r.join(', '),hostgroup))
    }

})




