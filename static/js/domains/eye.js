String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};


$( document ).ready(function() {
    $(".select2").select2();
    $('#business_units').trigger('change.select2');

});



tablez={}
tdata ={}

function genTable(tableID,count,details){
    var t = '<div class="col-lg-6"id="w_'+tableID+'">'
    t = t + '<div  id="h_'+tableID+'"><h2>'+ tableID.replace(/P/g,'.') +'</h2><h4>Server FQDN: '+details+' ('+ count +' domains)</h4><hr/></div>'
    t = t + '<table id="'+tableID+'" class="table table-striped table-responsive table-bordered table-hover" width="100%"></table></div>'
    return t
}

function clearContent(){
    document.getElementById('content').innerHTML =''
}

function changeBU(elem){
    var curr_SEL = elem.value

    var sel = document.getElementsByClassName('d_SEL')
    clearContent()
    var midpayc = document.getElementById('midpay')

    var content = document.getElementById('content')
    tablez={}
    tdata={}
    $.ajax({
        type: "GET",
        url: window.location+elem.value,
        cache: false,
        success: function (data) {
            console.log(data)
            for (var server in data['data']){
                var p = server.replace(/\./g,'P')
                content.innerHTML = content.innerHTML + genTable(p,data['data'][server]['domains'].length,data['data'][server]['fqdn'])

                tdata[p]=data['data'][server]['domains']
            }

        },
        complete : function(){
            for (var k in tdata){
                var cols =  [
                        {'data':'domain','title':'Domain'},
                    ]
                if (k == 'Undetermined'){
                    cols.push({'data':'value','title':'IP'})
                }
                else{
                     cols.push({'data':'nginx','title':'Config'})
                }
                tablez[k] = $('#'+k).DataTable({
                    pageLength: 25,
                    columns: cols,
                    //bLengthChange:false,
                    data:tdata[k],
                    aLengthMenu: [
                        [25, 50, 100, 200, -1],
                        [25, 50, 100, 200, "All"]
                    ],
                });
            }
        }
    });
    if (curr_SEL == 'MIDPAY'){
        midpayc.style.display='block'
    }
    else {
        midpayc.style.display='none'
    }
}

function filterTables(q){
    q = q.replace(/^\s+/, '').replace(/\s+$/, '');
    for (var k in tablez){
        tablez[k].search(q).draw()
        var tl = document.getElementById('w_'+k)
        if (q == ''){
            tl.style.display='block'
        }
        else{
            if (tablez[k].rows( { filter : 'applied'} ).nodes().length >0){
                tl.style.display='block'
            }
            else {
                tl.style.display='none'
            }
        }

    }
}

