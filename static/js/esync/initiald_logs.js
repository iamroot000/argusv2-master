String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

STREAM_LOG_END_FLAG = 'PLAY RECAP'
LOGFILE = ''

$(document).ready(function(){
    const urlParams = new URLSearchParams(window.location.search);
    LOGFILE = urlParams.get('log');
    document.getElementById('current_path').innerHTML = LOGFILE
    getLog(LOGFILE,0)

});

function getLog(logfile,offset){
    var execute_content = document.getElementById('execute_content')
    var command_modal = document.getElementById("COMMAND_MODAL");

    $.ajax({
        type: "GET",
        url: '/esync/initiald/?q=getLogs&log={0}&o={1}'.format(logfile,offset),
        cache: false,
        success: function (data) {
            var cont = ''
            var poll = true
            cont = cont +  data['log'][1]
            if (data['log'][0].includes(STREAM_LOG_END_FLAG)){
                    console.log(data['log'][1])
                    poll=false
                }
            else if(data['log'][0] == "MISSING"){
                    console.log(data['log'][1])
                    poll=false
            }

            $(execute_content).html(data['log'][0])
            execute_content.scrollTop =execute_content.scrollHeight

            console.log('tute',poll)
            if (poll === true){
                pollLog(logfile,data['log'][0]+offset)
                   setTimeout(function(){
                       location.reload();
                   },5000);
            }
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){


        }
    });
}

function pollLog(logfile,offset){
    getLog(logfile,offset)
}

