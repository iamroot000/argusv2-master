 $("#redis_key").select2();
var texteditors={};
data_p = {}
$(document).ready(function(){

     /*texteditors.editor_one = CodeMirror.fromTextArea(document.getElementById("redishandler"), {
         lineNumbers: true,
         matchBrackets: true,
         styleActiveLine: true,
         theme:"monokai",
         lineWrapping:true,
         autoRefresh: true,
     });*/


 $("#redis_key").trigger('change')

});

function expandTextarea(id) {
    document.getElementById(id).addEventListener('keyup', function() {
        this.style.overflow = 'hidden';
        this.style.height = 0;
        this.style.height = this.scrollHeight + 'px';
    }, false);
}



function getConfig(filename){

    if (filename != ''){

        $.ajax({
            type: "GET",
            url: window.location+'?key='+filename,
            async: false,
            cache: false,
            success: function (data) {
                console.log()
                data_p = data
            },
            complete:function(){
                //texteditors.editor_one.getDoc().setValue(JSON.stringify(data_p,null,4));
                document.getElementById("redishandler").innerHTML = JSON.stringify(data_p,null,4)

                 document.getElementById("redishandler").style.height='900px'
            }

        });
    }

}


function saveConfig(){
    var val = document.getElementById("redishandler")
    var k = document.getElementById("redis_key").value
    var nf = {
        'key': k,
        'value':null
    }
    try{
        json = JSON.parse(val.value)  

        nf['value']=json

        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location,
            async:false,
            data: JSON.stringify(nf),
            success: function(data) {
               if (data['STATUS'] == true){
                    alert('Saved')

               }
               else{
                    alert(data['ERROR'])

               }
               

            },
            error: function(err) {
                alert(err)
            }
        });
    }
    
    catch(err){
        alert(err)
    }

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
