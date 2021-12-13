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

statuss = []

    
$.ajax({
        type: "GET",
        dataType: "json",
        url: '/proxycontroller/servers/?q=getStates',
        async:true,
        success: function(result) {
            for (var i in result['data']){
                statuss.push(result['data'][i]['state'])
            }
        },
        error: function(err) {
            console.log(result)
        },
    });

COLUMNS = [
    {'title':'Server','data':'server'},
    {'title':'Geolocation','data':'region'},
    {'title':'IDC','data':'idc'},
    {
        'data':'state',
        'title':'Action',
        'render':function ( data, type, row ) {
            var sel = '<select style="width:100%%" class="form-control" onchange="changeStatus(\''+row['server']+'\',this)">'
            for (var k=0; k < statuss.length ; k++){
                var currstatus='OK'
                if (statuss[k] == row['state']){
                    sel = sel + '<option value="'+statuss[k]+'" selected>'+statuss[k]+'</option>' 
                    currstatus=statuss[k]
                }
                else{
                    sel = sel + '<option value="'+statuss[k]+'">'+statuss[k]+'</option>' 
                }
            }
            sel = sel + '</select><p style="display:none">'+currstatus+'</p>'
            return sel
        },
    },

]

serversTable = $('#serversTable').DataTable({
        pageLength: -1,
        aaSorting: [
            [ 3, "desc" ],

        ],
        //bLengthChange: false,
        autoWidth: false,
        columnDefs: [
                        { "width": "200px", "targets": 3 },
                        //{ "width": "400px", "targets": 2 },
                        //{ "width": "60px", "targets": 3 },
                        //{ "width": "100px", "targets": 4 },
                      ],
        columns: COLUMNS,
        ajax:{
            url:'/proxycontroller/servers/?q=getServers',
            dataSrc:function ( json ) {
                return json.data
            }
        },
        initComplete: function(){
            $(".select2").select2();

        }
    });

               

function changeStatus(server,stat){
    var rbody = {}
    rbody[server]=stat.value
    console.log(rbody)
    $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location+server+'/',
            data: JSON.stringify(rbody),
            success: function(result) {
                serversTable.ajax.reload();
                alert('SUCCESS')
            },

            error: function(err) {
                console.log(err)            
            },
       
    });
}

function addServersModal(){
    document.getElementById('server_address').value = ''
    var idcs = document.getElementById('idc')
    idcs.innerHTML=''
    $('#addServersModal').modal('show');

    $.ajax({
        type: "GET",
        dataType: "json",
        url: window.location+'?q=getIDCs',
        success: function(result) {
            for (var i=0;i<result['data'][0].length;i++){
                console.log(result['data'][0][i])
                var option = document.createElement('option')
                option.text = result['data'][0][i]['idc']
                option.value = result['data'][0][i]['idc']

                idcs.appendChild(option)
            }
        },
        error: function(err) {
            console.log(result)
        },
    });
}


function addServers(){
    var rbody = {
        'add':document.getElementById('server_address').value,
        'idc':document.getElementById('idc').value
    }
    
    console.log(rbody)

    $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location,
            data: JSON.stringify(rbody),
            success: function(result) {
                alert('SUCCESS')
                serversTable.ajax.reload();
                $('#addServersModal').modal('hide');

            },

            error: function(err) {
                console.log(err)            
            },
       
    });


}