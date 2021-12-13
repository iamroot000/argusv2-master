String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};


COLUMNS = [
    {
        'data':'domain',
        'title':'Domain',
        'render':function ( data, type, row ) {
            return '<a href="/domains/'+data+'" value="'+data+'" target="_blank">'+data+' <i class="fa fa-info-circle"></i></a>'
        },
    },
    {'data':'registrar_username','title':'Source Account'},
    {'data':'registrar','title':'Registrar'},
    {'data':'expiry','title':'Expiry'},
    {
        'data':'business_unit',
        'title':'Business Unit',
        'render':function ( data, type, row ) {
            return '<a href="#">'+data+'</a>'
        }
    },
    {'data':'tags','title':'Tags'},
]

tagstore = {}

domainsTable = $('#domainsTable').DataTable({
        pageLength: 20,
        //bLengthChange: false,
        autoWidth: false,
        columnDefs: [
                        { "width": "150px", "targets": 0 },
                        { "width": "100px", "targets": 1 },
                      ],
        columns: COLUMNS,
        ajax:{
            url:'/domains/?q=getAllDomains',
            dataSrc:function ( json ) {
                tagstore={}
                for (var i=0;i<json.data.length;i++){
                    var account = json.data[i]['registrar_username']
                    if(!tagstore.hasOwnProperty(account)){
                        tagstore[account] = 0
                    }
                    tagstore[account] ++

                    var provider = json.data[i]['registrar']

                    if(!tagstore.hasOwnProperty(provider)){
                        tagstore[provider] = 0
                    }
                    tagstore[provider] ++

                    var bu = json.data[i]['business_unit']

                    if(!tagstore.hasOwnProperty(bu)){
                        tagstore[bu] = 0
                    }
                    tagstore[bu] ++
                    if(json.data[i]['tags']){
                        var tag = json.data[i]['tags'].split(" ")
                        for (var p=0;p<tag.length;p++){
                            if(!tagstore.hasOwnProperty(tag[p])){
                                tagstore[tag[p]] = 0
                            }
                            tagstore[tag[p]] ++
                        }
                    }
                }
                for (var k in tagstore){
                    //console.log(k,tagstore[k])
                    var tags = document.getElementById('tags')
                    tags.innerHTML = tags.innerHTML + createTag(k,tagstore[k])
                }
                return json.data
            }
        }

    });

function filterTable(q){
    domainsTable.search(q).draw()
}

function openDomainInfo(domain){
        window.open('/domains/'+domain,'newwindow','width=1000,height=700')
        return false;
}

function createTag(tag,val){
    return '<a href=# class="btn btn-success btn-outline" value="'+tag+'" onclick="filterTable(\''+tag+'\')">'+'{0} ({1})'.format(tag,val)+'</a>&nbsp'

}

function invokeSearchByIP(){
    $('#searchByIPModal').modal('show');
     var ip = document.getElementById('ip')
     ip.value =''
     var res = document.getElementById('ipresults')
     res.innerHTML = ''
}

function searchByIP(){
    var ip = document.getElementById('ip')
    var res = document.getElementById('ipresults')
    $.ajax({
        type: "GET",
        url: '/domains/?q=getByIP&ip='+ip.value,
        cache: false,
        success: function (data) {
            res.innerHTML = ''
            res.innerHTML = data['result'].replace(/\,/g,'<br>').replace(/DOMAIN/g,'<b>DOMAIN: </b>').replace(/TYPE/g,'|<b>TYPE: </b>').replace(/HOST/g,'|<b>HOST: </b>').replace(/VALUE/g,'| <b>VALUE: </b>')
            alert('Search Done')
        },
        complete : function(){

        }
    });
}


function invokeBulkChangeByIP(){
    $('#bulkChangeByIPModal').modal('show');
    var ipfrom = document.getElementById('ipfrom')
    ipfrom.value =''
    var ipto = document.getElementById('ipto')
    ipto.value =''

    var res = document.getElementById('recordVerify')
    res.innerHTML = ''
}

function bulkSearchByIP(){
    var ipfrom = document.getElementById('ipfrom')
    var res = document.getElementById('recordVerify')

    $.ajax({
        type: "GET",
        url: '/domains/?q=getByIPStrict&ip='+ipfrom.value,
        cache: false,
        success: function (data) {
            res.innerHTML = ''
            res.innerHTML = data['result'].replace(/\,/g,'<br>').replace(/TYPE/g,'<b>TYPE: </b>').replace(/HOST/g,'| <b>HOST: </b>').replace(/VALUE/g,'| <b>VALUE: </b>')
            alert('Search Done')

        },
        complete : function(){
        }
    });
}

function bulkUpdate(){

    var prompt = confirm('Execute Bulk Changes? (This event is logged)')

    if (prompt){
        var ipfrom = document.getElementById('ipfrom')
        var ipto = document.getElementById('ipto')
        var rbody = {
            'from': ipfrom.value,
            'to': ipto.value
        }
        console.log(rbody)
        $.ajax({
                type: "POST",
                dataType: "json",
                url: '/domains/bulkprocess/',
                data: JSON.stringify(rbody),
                success: function(result) {
                    alert('Bulk Process started')
                },
                error: function(err) {
                    console.log(err)
                },
                complete: function(){
                    ipfrom.value =''
                    ipto.value =''
                    $('#bulkChangeByIPModal').modal('hide');
                }
        });

    }



}