$("#file").select2();

var commit = {
    "data":{}
    };

function removeCommit(id){
    delete commit['data'][id];
    console.log(commit)
}

function resetData(){
    //commit['data']={};
    var buttons = document.getElementsByClassName('revoke');
    for(var i = 0; i <= buttons.length; i++) {
    buttons[i].click();
    }
    console.log(commit);
}

$(document).ready(function(){

     var editor_one = CodeMirror.fromTextArea(document.getElementById("filehandler"), {
         lineNumbers: true,
         matchBrackets: true,
         styleActiveLine: true,
         theme:"monokai"
     });
     toastr.options = {
        "closeButton": true,
        "debug": false,
        "progressBar": true,
        "positionClass": "toast-bottom-right",
        "onclick": null,
        "showDuration": "400",
        "hideDuration": "-1",
        "timeOut": "-1",
        "extendedTimeOut": "-1",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut",
        //"closeHtml": '<button class="revoke" id="shit" onclick="removeCommit(this)">remove</button>',
        "onclick": false,
        "closeOnHover": false,
        "tapToDismiss": false,
        "preventDuplicates":true,
        'newestOnTop':true,

    }


});

function commitFile(){

    config = document.getElementById("filehandler").val;
    file =  $("#file").val();

    toastr.success(file,{"closeHtml": '<button class="revoke" id='+file+' onclick="removeCommit(this.id)" ><span class="fa fa-ban"> <i style="font-size:70%;">Remove</i></span></button>',});
     $('.CodeMirror').each(function(i, el){
                config = el.CodeMirror.getValue();
            });

    commit['data'][file]=config;
    console.log(commit);
}

function getConfig(filename){
    var dataString = 'filename=' + filename;
    document.getElementById('filehandler').innerHTML=''
    $.ajax({
        type: "GET",
        url: "/fwdcontrol/haproxy/data/",
        data: dataString,
        cache: false,
        success: function (data) {

            //document.getElementById('filehandler').innerHTML='shit'
             $('.CodeMirror').each(function(i, el){
                el.CodeMirror.setValue(data['content']);
            });
        },
        error: function(err) {
            console.log(err);
        }
    });

}

var initfile = $("#file").val();
getConfig(initfile);


function sync() {

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/fwdcontrol/haproxy/data/",
        data: JSON.stringify(commit),
        success: function(result) {
           if (result['result'][0].indexOf('FAILED') >= 0 || result['result'][0].indexOf('Invalid') >= 0 ){
            toastr.warning(result['result'][0],'ERROR',{"positionClass": "toast-top-left","preventDuplicates":false,});
           }

           else{
           toastr.success(result['result'],'Sync ',{"positionClass": "toast-top-left","preventDuplicates":false,});

           console.log(result['result']);
           resetData();
           }


        },
        error: function(err) {
        console.log(err);
    }


    });
}

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
