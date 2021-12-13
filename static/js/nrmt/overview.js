data = {}
content = document.getElementById('nrmt-content')
tables={}
data_fs = {}
function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x > y) ? -1 : ((x < y) ? 1 : 0));
    });
}
function createTableNRMT(tableName,data){
    var data_f = {
        "headers":[{'title':'_Service Name','data':'servicename'}],
        "data": []
    }
    var tName = tableName.replace(/ /g,'')
    for (var k in data){
        var key = k.replace(' // ','_')
        key = key.replace('10.167.11.','HK')
        key = key.replace('10.167.12.','HK')

        key = key.replace('10.168.11.','GDC')
        key = key.replace('10.168.12.','GDC')
        key = key.replace('.','-')

        data_f['headers'].push({
            "title":k,
            "data":key,
            'render':function ( d, type, row ) {

                    if (d == true){
                        var color = 'green'
                        var clas = 'mon-OK'
                        var msg = 'OK'

                    }
                    else if (d === false){
                        color = 'red'
                        clas = 'mon-NOTOK'
                        var msg = d

                    }

                    else if (d == null){
                        console.log('sadfsfd',row)
                        color = 'grey'
                        clas = 'mon-NOTOK'
                        var msg = 'Not monitored'

                    }
                    else {
                        color = 'black'
                        clas = 'mon-NOTOK'
                        var msg = d

                    }

                    return '<p style="color:'+color+'" class="'+clas+'">'+msg+'</p>'
                },
        })

    
}
    for (var k in data){
        for (var s in data[k]){
            var flag = false
            for (var i=0;i<data_f['data'].length;i++){
                if (data_f['data'][i]['servicename'] == s){
                    flag = true
                    break
                }
            }
            if (!flag){
                var row = {
                    'servicename':s
                }
                data_f['data'].push(row)
            }
        }
    }
    for (var k in data){
        var key = k.replace(' // ','_')
        key = key.replace('10.167.11.','HK')
        key = key.replace('10.167.12.','HK')

        key = key.replace('10.168.11.','GDC')
        key = key.replace('10.168.12.','GDC')

        for (var s in data[k]){
            for (var i=0;i<data_f['data'].length;i++){
                if (data_f['data'][i]['servicename'] == s){
                    data_f['data'][i][key] = data[k][s]
                }
            }
        }
    }



    var table = '<div class="col-lg-12 hosttype">'
    table = table + '<h2 class="hosttype" style="font-weight:bold">'+tableName+'</h2>'
    table = table + '<table class="table table-bordered table-responsive table-striped table-hover tablez" id="'+ tName +'" width="100%">'


    table = table + '</table>'
    table = table + '</div>'

    content.innerHTML = content.innerHTML + table

    data_f['headers'] = sortByKey(data_f['headers'],'title')
    data_fs[tName]=data_f

}

function createTableNRPE(tableName,data){
    var data_f = {
        "headers":[{'title':'IP','data':'IP'}],
        "data": []
    }
    var tName = tableName.replace(/ /g,'')
    for (var k in data){

        for (var ct in data[k]){
            var c = ct.replace('check_','')
            data_f['headers'].push({
                'title':c,
                'data':c,
                'render':function ( d, type, row ) {
                    var color = 'green'
                    var clas = 'mon-OK'
                    if (d[0] != 0){
                        color = 'red'
                         clas = 'mon-NOTOK'
                    }
                    return '<p style="color:'+color+'" class="'+clas+'">'+d[1]+'</p>'
                },
            })
        }
        break
    }

    for (var k in data){
        var row = {
            'IP':k
        }
        for (var ct in data[k]){
            var c = ct.replace('check_','')
            if (ct =='hostname'){
                 row[c]=data[k][ct]
            }
            else{
                row[c]=data[k][ct]
            }

        }
        data_f['data'].push(row)
    }

    var table = '<div class="col-lg-12 hosttype" id="'+ tName +'_d">'
    table = table + '<h2 class="hosttype"  style="font-weight:bold">'+tableName+'</h2>'
    table = table + '<table class="table table-bordered table-responsive table-striped table-hover tablez" id="'+ tName +'">'

    table = table + '</table>'
    table = table + '</div>'

    content.innerHTML = content.innerHTML + table

    data_fs[tName]=data_f



}

function displayData(){

    var sortobj = {}

    Object.keys(data['DATABASE']['data']).sort().forEach(function(key) {
      sortobj[key] = data['DATABASE']['data'][key];
    });

    for (var ht in sortobj){
        createTableNRPE(ht,data['DATABASE']['data'][ht])
    }

    var sortobj = {}

    Object.keys(data['PHYSICAL']['data']).sort().forEach(function(key) {
      sortobj[key] = sortobj[key];
    });


    for (var ht in sortobj){
        createTableNRPE(ht,data['PHYSICAL']['data'][ht])
    }

    var sortobj = {}

    Object.keys(data['CLOUDSERVER']['data']).sort().forEach(function(key) {
      sortobj[key] = data['CLOUDSERVER']['data'][key];
    });

    for (var ht in sortobj){
        createTableNRPE(ht,data['CLOUDSERVER']['data'][ht])
    }

    var sortobj = {}

    Object.keys(data['SERVICES']['data']).sort().forEach(function(key) {
      sortobj[key] = data['SERVICES']['data'][key];
    });

    for (var ht in sortobj){
        createTableNRMT(ht,data['SERVICES']['data'][ht])
    }
    for (var ht in data_fs){
        var t = ht.replace(/ /g,'')
        tables[t]=$('#'+t).DataTable({
        pageLength: -1,
        bLengthChange: false,
        columns: data_fs[t]['headers'],
        data:data_fs[t]['data']

    });
            //console.log('COLUMN',data_fs[t]['headers'])

    }
}



function procData(){
    console.log('START DATA')
    $.ajax({
        type: "GET",
        url: "/nrmt/data/?q=ALL",
        cache: false,
        success: function (res) {
            data = res

        },
        error: function(err) {
            console.log(err)
        },
        complete: function(){
            content.innerHTML = ''
            displayData(data)
            console.log('END DATA')
            console.log(data)
            poll()
        },
    });

}

function poll(){
   setTimeout(function(){
      procData()
  }, 60000);
}

procData()


function scrollSearch(elem){
    //console.log(elem.value)
    var hts = document.getElementsByClassName('hosttype')

        for (var i=0;i<hts.length;i++){

        if (hts[i].innerHTML.toLowerCase().includes(elem.value.toLowerCase()) || elem.value == ''){
            document.body.scrollTop = 0
            hts[i].style.display='block';

        }
        else{
            hts[i].style.display='none';
        }

        }




    //$(document).scrollTo('#MySQLMasterDB_d');
    //$(window).scrollTop($('#MySQLMasterDB_d').offset(500).top);



}