events ={}
triggers={}
tablediv = document.getElementById('tablediv')
maintable = {}

String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};


COLUMNS = {
    'EVENTS':[
        {
            'data':'eventid',
            'title':'#',
            'render':function ( data, type, row ) {
                return '<input type="checkbox" class="eventcheck" value="{0}"/></label>'.format(data)
            },
        },
        {
            'data':'eventid',
            'title':'Event ID',
            'render':function ( data, type, row ) {
                return "{0}".format(data)
            },
        },
        {'data':'groupname','title':'Group'},
        {'data':'ip','title':'Host'},
        {
            'data':'severity',
            'title':'Severity',
            'render':function ( data, type, row ) {
                if (data == 0){
                    return '<span class="badge">Not Classified</span>'
                }
                else if (data == 1){
                    return '<span class="badge badge-success">Information</span>'
                }
                else if (data == 2){
                    return '<span class="badge badge-warning">Warning</span>'
                }
                else if (data == 3){
                    return '<span class="badge badge-warning">Average</span>'
                }
                else if (data == 4){
                    return '<span class="badge badge-danger">High</span>'
                }
                else if (data == 5){
                    return '<span class="badge badge-danger">Disaster</span>'
                }
                return '???'
            },
        },
        {'data':'name','title':'Message'},
        {'data':'clock','title':'Time'},
        /*{
            'data':'acknowledged',
            'title':'Acknowledges',
            'render':function ( data, type, row ) {
                var ackbutton = '<a href="/monitoring/event/?eventid={0}" target="_blank"> <i class="fa fa-share-square"></i></a>'.format(row['eventid'])
                if (data != false){
                    console.log('tite')
                    var acks = '<small>'
                    for (var k in data){
                        acks = acks + '{0} - {1}'.format(data[k]['clock'],data[k]['message'])
                        if (data[k].hasOwnProperty('params')){
                            if (data[k]['params'].hasOwnProperty('USER')){
                                acks = acks + '<br/>User: {0}'.format(data[k]['params']['USER'])
                            }
                            if (data[k]['params'].hasOwnProperty('ESCALATE')){
                                acks = acks + '<br/>Escalate: {0}'.format(data[k]['params']['ESCALATE'])
                            }
                        }
                        acks = acks + '<br/><br/>'
                    }
                    acks = acks + '</small>'
                    return acks + ackbutton
                }
                return '<small>No Acknowledgement</small>'+ackbutton
            },
        },*/
        {
            'data':'value',
            'title':'Status',
            'render':function ( data, type, row ) {
                if (data != 1){
                    return '<span class="label label-primary pull-center">RESOLVED</span> <br/>Recovery ID:{0} - {1}'.format(row['r_eventid'],row['resolvetime'])
                }
                return '<span class="label label-danger pull-center">PROBLEM</span>'

            },
        },
    ]
}

function clearTable(){
    tablediv.innerHTML = '<table id="main_table" class="table table-striped table-responsive table-bordered table-hover" width="100%"></table>'
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
                url: "/monitoring/?q=getEvents&p=3&l=0",
                cache: false,
                success: function (res) {
                    events = res
                },
                error: function(err) {
                    console.log(err)
                },
                complete: function(){
                console.log('END DATA')
                    generateTable()
                    poll()
                },
            });
        },
    });
}

function poll(){
   setTimeout(function(){
      procData()
  //}, 60000);
    }, 6000000000);
}

function generateTable(){
    console.log(events)
    maintable = $('#main_table').DataTable({
        pageLength: -1,
        aaSorting: [[ 6, "desc" ]],
        columns: COLUMNS['EVENTS'],
        data:events['data'],
        /*ajax:{
            url:'https://argus.omtools.me/inventory/data/?q='+curr_SEL,
            dataSrc:function ( json ) {
            }
        },*/
        bDestroy:true,
    });

}


$( document ).ready(function() {
    clearTable()
    procData()
});