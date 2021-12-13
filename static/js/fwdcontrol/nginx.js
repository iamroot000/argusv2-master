$("#file").select2();


var config_src = document.getElementById("config_src").innerHTML;
var hostgroup = document.getElementById("hostgroup").innerHTML;
var alertflag = 0;
var commit = {
    "data":{},
    "config_src":config_src,
    "hostgroup":hostgroup
    };

var texteditors={};
$(document).ready(function(){

     texteditors.editor_one = CodeMirror.fromTextArea(document.getElementById("filehandler"), {
         lineNumbers: true,
         matchBrackets: true,
         styleActiveLine: true,
         theme:"monokai",
         lineWrapping:true,
         autoRefresh: true,
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
        "closeHtml": '<button class="revoke" id="shit" onclick="removeCommit(this)">x</button>',
        "onclick": false,
        "closeOnHover": false,
        "tapToDismiss": false,
        //"preventDuplicates":true,
        'newestOnTop':true,
    }
    var initfile = $("#file").val();
    getConfig(initfile);
});


function createFile(){
    if (alertflag == 1){
        toastr.clear();
        alertflag=0;
    }
    var filename = prompt("Please enter the new filename (must end in .conf or .include or .cfg Max of 30 Characters");
    if (filename != null && (filename.endsWith('.conf') == true || filename.endsWith('.include') == true || filename.endsWith('.cfg') == true )) {

        newfile = {
            'filename':filename
        }

        $.ajax({
        type: "POST",
        dataType: "json",
        url: window.location+'create/',
        data: JSON.stringify(newfile),
        success: function(result) {
            alert(result['result']);
            sel = document.getElementById('file')
            sel.innerHTML = sel.innerHTML + '<option id="'+filename+'" value="'+filename+'" >'+filename+'</option>'
            $('#file').val(filename).trigger('change');

        },
        error: function(err) {
        console.log(err);
        alert('Invalid filename!');
        }

        });
    }
    else if (file != null){
        alert('Invalid filename!');
    }



}


function removeCommit(elem){
    var parent = elem.parentNode;
    var id = parent.childNodes[2].innerHTML;
    delete commit['data'][id];

}

function resetData(){
    //commit['data']={};
    var buttons = document.getElementsByClassName('revoke toast-close-button');
    for(var i = 0; i <= buttons.length; i++) {
    buttons[i].click();
    }

}



function commitFile(){
    if (alertflag == 1){
        toastr.clear();
        alertflag=0;
    }

    config = document.getElementById("filehandler").val;
    file =  $("#file").val();

    toastr.success(file.replace(config_src,''));
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
        url: window.location,
        data: dataString,
        cache: false,
        success: function (data) {
            texteditors.editor_one.getDoc().setValue(data['content']);
            document.getElementById('commit').disabled=false
        },
        error: function(err) {
            console.log(err);
            texteditors.editor_one.getDoc().setValue("This is a directory");
            document.getElementById('commit').disabled=true

        }
    });

}




function sync(elem) {
    prompt = confirm("Execute Sync?");

    if (prompt == true){

     elem.disabled=true;
     com=document.getElementById('commit');
     com.disabled=true;
     $('#file').attr('disabled','disabled');
     $('#textrow').attr('hidden','hidden');
     $('#syncrow').removeAttr('hidden');

     $.ajax({
        type: "POST",
        dataType: "json",
        url: window.location,
        data: JSON.stringify(commit),
        success: function(result) {

        toastr.clear();
        for (i=0; i<result['result'].length; i++){

            if (result['result'][i].indexOf('FAILED') >= 0){
                toastr.warning(result['result'][i],'ERROR',{"positionClass": "toast-top-left","preventDuplicates":false,}).css("width","500px");
            }
            else{
                toastr.success(result['result'][i],'Action ',{"positionClass": "toast-top-left","preventDuplicates":false,}).css("width","500px");
            }
            commit['data']={};

        }

        alertflag = 1;
        com.disabled=false
        $('#file').removeAttr('disabled');
        $('#textrow').removeAttr('hidden');
        $('#syncrow').attr('hidden','hidden');
        elem.disabled=false;

        },
        error: function(err) {
        console.log(err);
    }

    });
    }

}

function changeFocus(elem){
    $("#file").val(elem.innerHTML).trigger('change')
}

function findString(){
//var search = prompt("Search for string:");

//if (search != null) {
    var search = document.getElementById('findstring').value
    var dataString = 'search=' + search ;
    resultPanel = document.getElementById('searchResults')
    resultDiv = document.getElementById('searchDiv')
    resultPanel.innerHTML=''



    $.ajax({
        type: "GET",
        url: window.location,
        data: dataString,
        cache: false,
        success: function (data) {
            //alert(data['data']);


            if (data['data'].length > 0){
                for(var i = 0; i < data['data'].length; i++) {
                    a=document.createElement('li')

                    b = document.createElement('a')
                    b.setAttribute('href','#')
                    b.setAttribute('onclick','changeFocus(this)')
                    b.innerHTML=data['data'][i]

                    a.appendChild(b)

                    if (data['data'].length == 1){
                        console.log(b)
                        changeFocus(b)
                    }

                    resultPanel.appendChild(a)
                }
                resultDiv.style.display = 'block'
            }

            else {
                alert('String not Found')
                resultDiv.style.display='none'
            }


        },
        error: function(err) {
            console.log(err)
        }
    });
    }


//}

$("#findstring").on('keyup', function (e) {
    if (e.keyCode == 13) {
        findString()
    }
});

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


