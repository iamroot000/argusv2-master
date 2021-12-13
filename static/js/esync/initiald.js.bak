String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};
tablez = {}
business_units= $("#business_unit").select2({
    tags:true,
    createTag: function (params) {
        var term = $.trim(params.term);

        if (term === '') {
          return null;
        }

        return {
          id: term,
          text: term,
          newTag: true // add additional parameters
        }
      }
})
server_functions= $("#server_function").select2({
    tags:true,
    createTag: function (params) {
        var term = $.trim(params.term);

        if (term === '') {
          return null;
        }

        return {
          id: term,
          text: term,
          newTag: true // add additional parameters
        }
      }
})
initialization_types= $("#initialization_types").select2()
service_providers= $("#service_providers").select2()
country_codes= $("#country_codes").select2()


$(document).ready(function(){
    generateView()
});
function generateView(){
    $.ajax({
        type: "GET",
        url: '/esync/initiald/?q=getConfig',
        cache: false,
        success: function (data) {
            for (var k in data['business_units']){
                var op = {
                    id: data['business_units'][k],
                    text: data['business_units'][k],
                    value: data['business_units'][k],
                }
                var business_unit = new Option(op.text, op.value, false, false);
                business_units.append(business_unit)
            }
            for (var k in data['server_functions']){
                var op = {
                    id: data['server_functions'][k],
                    text: data['server_functions'][k],
                    value: data['server_functions'][k],
                }
                var server_function = new Option(op.text, op.value, false, false);
                server_functions.append(server_function)
            }
            for (var k in data['initialization_types']){
                var op = {
                    id: data['initialization_types'][k],
                    text: data['initialization_types'][k]['initialization_name'],
                    value: data['initialization_types'][k]['initialization_type'],
                }
                var initialization_type = new Option(op.text, op.value, false, false);
                initialization_types.append(initialization_type)
            }
            for (var k in data['service_providers']){
                var op = {
                    id: data['service_providers'][k],
                    text: data['service_providers'][k]['service_provider'],
                    value: data['service_providers'][k]['service_provider_prefix'],
                }
                var service_provider = new Option(op.text, op.value, false, false);
                service_providers.append(service_provider)
            }
            for (var k in data['country_codes']){
                var op = {
                    id: data['country_codes'][k],
                    text: '{0} | {1}'.format(data['country_codes'][k]['country_code'],data['country_codes'][k]['location']),
                    value: data['country_codes'][k]['country_code'],
                }
                var country_code = new Option(op.text, op.value, false, false);
                country_codes.append(country_code)
            }
        },
        error: function(err) {
            console.log(err);
        },

    });

    tablez = $('#main_table').DataTable({
        pageLength: -1,
        columns: [
            //{'data':'hosts_id__hostname','title':'Hostname'},
            {
                "data":null,
                "title": 'Hostname',
                "render": function ( data, type, full, meta ) {
                    return '<a href="/esync/initiald/?q=getLogs&log={0}">{1}</a>'.format(data['logfile'],data['hosts_id__hostname'])
                }
            },
            {'data':'hosts_id__host_ip','title':'IP'},
            //{'data':'initialization_status','title':'Status'},
            {
                "data":null,
                "title": 'Status',
                "render": function ( data, type, full, meta ) {
                    var status = data['initialization_status']
                    if (status === 'ERROR_FAILED'){
                        status = '<p style="color:red">'+data['initialization_status']+'</p>'
                        status = status + ' <button class="btn btn-primary btn-sm" value="{0}" onclick="restart_initialization(this)">Retry</button>'.format(data['hosts_id__hostname'])
                    }
                    else if (status === 'COMPLETED'){
                        status = '<p style="color:green">'+data['initialization_status']+'</p>'
                    }
                    else {
                        status = '<p>'+data['initialization_status']+'</p>'
                    }
                    return status + ' <a href="/esync/initiald/?q=getLogs&log={0}" target="_blank"><i class="fa fa-edit"></i> Logs</a>'.format(data['logfile'])
                }
            },
            {'data':'initialization_type__initialization_name','title':'Type'},
            {'data':'service_provider','title':'Service Provider'},
            {'data':'created','title':'Date'},
            ],
        aaSorting: [[5,'desc']],

        bLengthChange: false,
        bDestroy:true,
        ajax:{
            url:'/esync/initiald/?q=getInitList',
            dataSrc:function ( json ) {

                return json.initialized_servers
            }
        },
    });
}

function start_initialization(){
    var sp = $('#service_providers').select2('data')[0]
    var cc = $('#country_codes').select2('data')[0]
    var bu = $('#business_unit').select2('data')[0]
    var fu = $('#server_function').select2('data')[0]
    var it = $('#initialization_types').select2('data')[0]

    var ip = document.getElementById('ip_address')
    var rp = document.getElementById('root_password')

    var newData = {
        "service_provider":sp.id,
        "country_code":cc.id,
        'business_unit':bu.text,
        'server_function':fu.text,
        'initialization_type':it.id,
        'ip_address':ip.value,
        'root_password':rp.value,
    }

    var prompt = confirm('Initialize Server? Please verify the parameters below:\n\nSERVICE_PROVIDER: {0}\nCOUNTRY CODE: {1}\nUNIT: {2}\nFUNCTION: {3}\nINIT TYPE: {4}\n\nIP: {5}\nPASS: {6}\n\n PROCEED?'.format(sp.text,cc.id,bu.text,fu.text,it.text,ip.value,rp.value))


    if (prompt){
        $.ajax({
            type: "POST",
            dataType: "json",
            url: '/esync/initiald/start',
            data: JSON.stringify(newData),
            success: function(result) {
                console.log(result)
                if(result['is_successful'] === false){
                    alert(result['result'])
                    console.log(result['result'])
                }
                else{
                    //tablez.ajax.reload()
                    //var win = window.open('/esync/initiald/?q=getLogs&log={0}'.format(result['result'][0][2]), '_blank');
                    //win.focus();
                    window.open('/esync/initiald/?q=getLogs&log={0}'.format(result['result'][0][2]), '_self');
                }
            },
            error: function(err) {
                console.log(err)
            }

        });
    }
}

function restart_initialization(elem){

    var newData = {
        "hostname":elem.value,
    }

    var prompt = confirm('Reinitialize Server?\n\nHostname: {0}'.format(newData['hostname']))


    if (prompt){
        $.ajax({
            type: "POST",
            dataType: "json",
            url: '/esync/initiald/start?retry=true',
            data: JSON.stringify(newData),
            success: function(result) {
                console.log(result)
                if(result['is_successful'] === false){
                    alert(result['result'])
                    console.log(result['result'])
                }
                else{
                    window.open('/esync/initiald/?q=getLogs&log={0}'.format(result['result'][0][2]), '_self');
                }
            },
            error: function(err) {
                console.log(err)
            }

        });
    }
}



setInterval(
    function(){
        //alert("Reload table");
        tablez.ajax.reload()

        }, 30000);