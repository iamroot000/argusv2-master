String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

$("#escalate").select2();

function isEmptyOrSpaces(str){
    return str === null || str.match(/^ *$/) !== null;
}

function submitChanges(){
    var rbody ={}
    var eids = []
    var eventobj = document.getElementsByClassName('eid')

    var escalateusers = $('#escalate').val()

    var msg = document.getElementById('message').value
    for (var i=0;i<eventobj.length;i++){
        eids.push(eventobj[i].innerHTML)
    }

    rbody = {
        "eventids":eids,
        "message":msg,
        "escalateusers":escalateusers
    }

    if(isEmptyOrSpaces(msg)){
        alert('Please Enter a message...')
    }
    else{
        $.ajax({
            type: "POST",
            dataType: "json",
            url: '/monitoring/event/',
            data: JSON.stringify(rbody),

            error: function(err) {
                console.log(err)
                alert(err)
            },
            complete: function(){
                alert('Acknowledge sumbitted, reloading page')
                location.reload()
            }
        });

    }
    console.log(rbody)
}