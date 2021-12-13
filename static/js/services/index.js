page_data ={}


dirs = $("#asset_type").select2();

tablez={}
String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

String.prototype.matchAll = function(regexp) {
    var matches = [];
    this.replace(regexp, function() {
        var arr = ([]).slice.call(arguments, 0);
        var extras = arr.splice(-2);
        arr.index = extras[0];
        arr.input = extras[1];
        matches.push(arr);
    });
    return matches.length ? matches : null;
};

$( document ).ready(function() {
    generateView()
});

function generateView(){
    document.getElementById('content').innerHTML = genTable()
    tablez = $('#main_table').DataTable({
    pageLength: -1,
    columns: [
            {'data':'name','title':'Service Name'},
            //{'data':'type','title':'Type'},
            {'data':null,'title':'Test Version'},
            {'data':'version','title':'Production Version'},
            {
                "data":null,
                 "render": function ( data, type, full, meta ) {

                     return '<button id="'+ data['CN'] +'" class="btn btn-primary btn-sm" href="#" onclick="renewCert(this)"> Restart</button>&nbsp;'
                     +'<button id="'+ data['CN'] +'" class="btn btn-success btn-sm" href="#" onclick="updateCertInvoke(this)"> Update</button>&nbsp;'
                     +'<a id="'+ data['CN'] +'" class="btn btn-default btn-sm" href="/LEManager/history/'+data['CN']+'" target="_blank"> History</a>&nbsp;'
                 }
               },

            //{'data':'ip','title':'IP'},
            ],
    bLengthChange: false,
    ajax:{
        url:'/services?q=getServices&format=list',
        dataSrc:function ( json ) {

            return json.data
        }
        },
        bDestroy:true,
    });
}

function genTable(){
    return '<table id="main_table" class="table table-striped table-responsive table-bordered table-hover" width="100%"></table>'
}

function clearContent(){
    document.getElementById('content').innerHTML =''
}

function filterTable(key){
    tablez.search("{0}".format(key)).draw()
}

function getTree(groups) {
    data = []

    for (var k in groups){
        var parent = {
            'text':"  {0}".format(k),
            'nodes':[],
            'parent':'',
            'value':k,
            'icon': "fa fa-bookmark",
        }
        for (var p in groups[k]){
            var c1 = {
                'text':'  {0}'.format(p),
                'parent':k,
                'value':'{0} {1}-'.format(k,p),
                'icon': "fa fa-circle",
            }
            if (groups[k][p].length!=0){
                c1['nodes']=[]
            }
            for (var l in groups[k][p]){
                var c2 = {
                    'text':'  {0}'.format(groups[k][p][l]),
                    'parent':k,
                    'value':'{0} {1}-{2}'.format(k,p,groups[k][p][l]),
                }
                c1['nodes'].push(c2)
            }
            parent['nodes'].push(c1)
        }
        data.push(parent)
    }
    return data;
}
