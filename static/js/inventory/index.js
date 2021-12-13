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
            {'data':'hostname','title':'Hostname'},
            {'data':'host_ip','title':'IP'},
            {'data':'groups','title':'Groups'},
            {'data':'service_provider','title':'Provider'},
            {'data':'cpu','title':'CPU Cores'},
            {
            "data":null,
            "title": "Memory",
             "render": function ( data, type, full, meta ) {
                var valu = ''
                if (data['memory'] != ''){
                    valu = '{0} GB'.format(data['memory'])
                }
                 return valu
             }
            },
            ],
    bLengthChange: false,
    ajax:{
        url:'/inventory/data/',
        dataSrc:function ( json ) {
            document.getElementById('content').className = 'col-md-9'
            var filtertype = document.getElementById('filtertype').value

            var reg = /(\S+)-([a-zA-Z_]+[a-zA-Z_0-9]+[a-zA-Z_]+)(\d+)\.(\S+)\.(\S+)\.(monaco1\.me)/g


            var groups = {}
            if (filtertype == 'bhost'){
                for (var k in json['data']){
                    var hname = json['data'][k]['hostname']
                    for (var g in json['data'][k]['groups']){
                        var gname = json['data'][k]['groups'][g]
                        if (!gname.toLowerCase().includes('system')){
                            if (!groups.hasOwnProperty(gname)){
                                groups[gname]={}
                            }
                            var matches = hname.matchAll(reg)
                            if (matches != null){
                                var bunit = matches[0][1].toUpperCase()
                                var func = matches[0][2].toUpperCase()
                                if (!groups[gname].hasOwnProperty(bunit)){
                                    groups[gname][bunit]=[]
                                }
                                if (!groups[gname][bunit].includes(func)){
                                    groups[gname][bunit].push(func)
                                }
                            }
                        }
                    }
                }
            }
            if (filtertype == 'bsys'){
                for (var k in json['data']){
                    var hname = json['data'][k]['hostname']
                    for (var g in json['data'][k]['groups']){
                        var gname = json['data'][k]['groups'][g]
                        if (gname.toLowerCase().includes('system')){
                            if (!groups.hasOwnProperty(gname)){
                                groups[gname]={}
                            }
                            var matches = hname.matchAll(reg)
                            if (matches != null){
                                var bunit = matches[0][3].toUpperCase()
                                var func = matches[0][4].toUpperCase()
                                if (!groups[gname].hasOwnProperty(bunit)){
                                    groups[gname][bunit]=[]
                                }
                                if (!groups[gname][bunit].includes(func)){
                                    groups[gname][bunit].push(func)
                                }
                            }
                        }
                    }
                }
            }
            var initSelectableTree = function() {
                return $('#treeview-selectable').treeview({
                    data: getTree(groups),
                    onNodeSelected: function(event, node) {
                        filterTable(node.value)
                        $('#treeview-selectable').treeview('expandNode', [ node.nodeId, { levels: 1, silent: true } ]);
                    },
                    onNodeUnselected: function (event, node) {
                        filterTable('')
                        //$('#treeview-selectable').treeview('collapseNode', [ node.nodeId, { levels: 1, silent: true } ]);

                    }
                });
            };
            var $selectableTree = initSelectableTree();

            page_data = json
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
