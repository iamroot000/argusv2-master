$(function () {
$("#tablefilter").select2();
});


var datenow = new Date(Date.now());
$(document).ready(function () {
                $('.i-checks').iCheck({
                    checkboxClass: 'icheckbox_square-green',
                    radioClass: 'iradio_square-green',
                });
            });
table = $('#domains').DataTable({
        autoWidth: false,
        pageLength: 50,
        bLengthChange: false,
        aaSorting: [[3,'desc']],
        columnDefs: [
            { "type": "date-de", targets: 2 },
                {
                    targets: [0],
                    width: "15%",
                },
                {
                    targets: [2],
                    width: "14%",
                },
                {
                    targets: [3],
                    width: "15%",
                },
                {
                    targets: [4],
                    width: "5%",
                },
            ],
        columns: [
                {
                "data":null,
                 "render": function ( data, type, full, meta ) {

                     return '<p style="font-weight:bold;color:green">'+data['CN']+'</p>'
                 }
               },
               {
                "data":null,
                 "render": function ( data, type, full, meta ) {
                        var CN=''
                        for (var i = 0; i < data['alt'].length; i++) {
                            CN=CN+data['alt'][i]+'<br/>';
                        }

                     return '<p style="font-style:italic;">'+CN+'</p>'
                 }
               },
               { "data": "updated" },
                { "data": "last_activity" },
               {
                "data":null,
                 "render": function ( data, type, full, meta ) {

                     return '<button id="'+ data['CN'] +'" class="btn btn-primary btn-sm" href="#" onclick="renewCert(this)"> Renew</button>&nbsp;'
                     +'<button id="'+ data['CN'] +'" class="btn btn-success btn-sm" href="#" onclick="updateCertInvoke(this)"> Update</button>&nbsp;'
                     +'<a id="'+ data['CN'] +'" class="btn btn-default btn-sm" href="/LEManager/history/'+data['CN']+'" target="_blank"> History</a>&nbsp;'
                 }
               },
        ],
        ajax: {
            url: '/LEManager/data/?select=ALL',
            success: function(data){
                table.rows.add(data['data']).draw();
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Error loading data, please contact the very handsome System Administrator")
            }
        }
    });



function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

if (getParameterByName('getcert',window.location) != null){

    var temp = getParameterByName('getcert',window.location).split('.').reverse();
    var root_domain = temp[1] + '.' + temp[0];
    t={
        id:root_domain
    }
    $.ajax({
        type: "GET",
        url: '/LEManager/data/?CN='+t['id'],
        cache: false,
        success: function (data) {
            updateCertInvoke(t)
        },
        error: function(err) {
            alert('Domain not yet registered in the DB');
            newCertInvoke()
            document.getElementById('MODAL-commonNameCREATE').value=t['id']

        }
    });

}

function reloadTable(){
    table.ajax.url('/LEManager/data/?select=ALL')
    table.clear();
    table.load();
}


function updateCertInvoke(elem){
    document.getElementById('MODAL-domainName').innerHTML = elem.id;

    CN='';
    $('#MODAL-DNSCheck2').iCheck('uncheck');

    $.ajax({
        type: "GET",
        url: '/LEManager/data/?CN='+elem.id,
        cache: false,
        async: false,
        success: function (data) {
            for (var i = 0; i < data.length; i++) {


                document.getElementById('MODAL-altNameRow2').style.display='inline';
                CN=CN+data[i]+'\n';


            }
            document.getElementById('MODAL-altNameUPDATE').value= CN;


        },
        error: function(err) {
            console.log(err);
        }
    });
    reloadTable();
    $("#LEUpdateModal").modal()
}


function bulkCertInvoke(){
    $("#LEBulkModal").modal()
}

function bulkCert(){
    prompt = confirm("Bulk request SSL?");


    if (prompt == true){

        commit={
            'domains':document.getElementById('MODAL-BulkCreate').value
        }

        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/LEManager/bulkcreate",
            data: JSON.stringify(commit),
            /*success: function(result) {
               alert('OK!');
               showAlert(commit['domains'],result)

            },

            error: function(err) {
            alert('err');
            },
            timeout: 300000*/
        });
        reloadTable();
        $("#LEBulkModal").modal('hide')

    }

}


function newCertInvoke(){
    $('#MODAL-DNSCheck').iCheck('uncheck');
    $("#LECreateModal").modal()
}

function newCert(){
    prompt = confirm("Request SSL?");

    if (prompt == true){

        commit = {
            "CN":document.getElementById('MODAL-commonNameCREATE').value,
            'alt':document.getElementById('MODAL-altNameCREATE').value
        }


        if ( document.getElementById('MODAL-DNSCheck').checked ==true ){
            commit['bypass']=true;
        }

        console.log(commit)
       $.ajax({
            type: "POST",
            dataType: "json",
            url: "/LEManager/create",
            data: JSON.stringify(commit),
            /*success: function(result) {
               showAlert(commit['CN'],result)

            },
            error: function(err) {
                alert('ERROR');
            },*/
            timeout: 300000
        });

        reloadTable();
        $("#LECreateModal").modal('hide')

        document.getElementById('MODAL-commonNameCREATE').value='';




    }


}


function updateCert(){
    domain = document.getElementById('MODAL-domainName').innerHTML;
    prompt = confirm("Update "+domain+" SSL?");


    if (prompt == true){

        commit={
            'CN':domain,
            'alt':document.getElementById('MODAL-altNameUPDATE').value
        }

        if ( document.getElementById('MODAL-DNSCheck2').checked ==true ){
            commit['bypass']=true;
        }

        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/LEManager/update",
            data: JSON.stringify(commit),
            /*success: function(result) {
               alert('OK!');
               showAlert(domain,result)

            },

            error: function(err) {
            alert('err');
            },
            timeout: 300000*/
        });
        reloadTable();
        $("#LEUpdateModal").modal('hide')

    }

}


function renewCert(elem){
    prompt = confirm("Renew "+elem.id+" SSL?");

    if (prompt == true){
        commit={
            'CN':elem.id
        }
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/LEManager/renew",
            data: JSON.stringify(commit),
            /*success: function(result) {
               console.log(result)

               showAlert(elem.id,result)
            },

            error: function(err) {
            alert('err');
            },
            timeout: 300000*/
        });
        reloadTable();
    }
}
function clearAlert(elem){
    elem.style.display='none';
}
function showAlert(domain,response){

    if(response['status']=='success'){
        alertmsg =  '<div class="widget navy-bg p-lg text-center" id="dnsAlertColor" onclick="clearAlert(this)">'
                   +'     <div class="m-b-md">'
                   +'         <i class="fa fa-check fa-3x" id="alert-'+domain+'"></i>'
                   +'         <h3 class="m-xs" id="sslAlertMessage">'+response['msg']+'</h3>'
                   +'         <small>(Click to dismiss this message)</small>'
                   +'     </div>'
                   +'</div>'
    }

    else {
        alertmsg =  '<div class="widget red-bg p-lg text-center" id="dnsAlertColor" onclick="clearAlert(this)">'
                   +'     <div class="m-b-md">'
                   +'         <i class="fa fa-exclamation-triangle fa-3x" id="alert-'+domain+'"></i>'
                   +'         <h3 class="m-xs" id="sslAlertMessage">'+response['msg']+'</h3>'
                   +'         <small>(Click to dismiss this message)</small>'
                   +'     </div>'
                   +'</div>'
    }

    row=document.getElementById('alertRow')
    row.innerHTML=row.innerHTML+alertmsg

}

function getPending(){
    $.ajax({
        type: "GET",
        url: '/LEManager/data/?pending=ALL',
        cache: false,
        success: function (data) {
          val='';
          pendingDIV=document.getElementById('pendingDIV');
          pendingJobs=document.getElementById('pendingJobs');


          if (data['data']){

              pendingDIV.style.display='inline';

              for (var i in data['data']){
                 var color = 'green'

                 if (data['data'][i]['activity'].toLowerCase().includes('failed')){
                    color='red'
                 }

                 val=val+'<li><strong style="color:'+color+'">'+data['data'][i]['domain']+'</strong><i style="padding-left:3em;"> - '+data['data'][i]['activity']+'</i><span class="pull-right">'+data['data'][i]['created_on']+'</span></li><hr/>'

              }

              pendingJobs.innerHTML=val;
          }




        },
        error: function(err) {
            console.log(err);
        }
    });

}


getPending()
setInterval(reloadTable, 20000);
setInterval(getPending, 5000);

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
