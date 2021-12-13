var ids = $('.sortedtable').map(function() {
    return this.id;
}).get();
msg = new SpeechSynthesisUtterance();
msg.lang = "en-GB"
$(document).ready(function() {

            var ids = $('.sortedtable').map(function() {
                return this.id;
            }).get();

             var arrayLength = ids.length;

                for (var i = 0; i < arrayLength; i++) {
                    table = $("[id='"+ ids[i] +"']").DataTable({
                    ajax : 'ajax/?btype='+encodeURIComponent(ids[i].trim()),
                    responsive: true,
                    aaSorting: [[0,'asc']],
                    pageLength: -1,
                    bLengthChange: false,
                    bPaginate: false,
                    bFilter: false,
                    bInfo: false,
                    responsive: false,
                    columnDefs: [{
                        type:'natural',
                        targets: 'no-sort',
                        orderable: true,
                        className: "dt-center",
                        targets: "_all"
                    }]
            });

                }


        });






function generateTable(id){
    $("[id='"+ id +"']").DataTable().ajax.reload();
}

function generateSpeech(){
window.speechSynthesis.cancel()
        $.ajax({
            type: "GET",
            url: 'ajax/?btype=speech',
            success: function(data) {
                msg.text = data['data']
                window.speechSynthesis.speak(msg)
            },
        });
}

function dbmonitor(){
        var div = document.getElementById('nagalerts_db_div')
        var d = document.getElementById('nagalerts_db')
        d.innerHTML =''
        $.ajax({
            type: "GET",
            url: "ajax/?btype=nagalerts_db",
            cache: false,
            success: function (data) {
                if (data['data'].length != 0){
                    div.style.display = 'block';
                    var inp = ''
                    for (var t=0;t<data['data'].length; t++){
                        for (var k in data['data'][t]){
                            inp = inp +	'<div class="col-lg-4 alert alert-danger">'
                            inp = inp + '<h1 style="font-weight:bold">'+ k +'</h1>'
                            for (var s in data['data'][t][k]['services']){
                                inp = inp + '<h2><span style="font-weight:bold">'+s+ '</span> <span style="font-weight:normal" > - '  +data['data'][t][k]['services'][s]['plugin_output']+'</span></h2><br/>'
                            }
                             inp = inp +	'</div>'
                        }
                    }
                    d.innerHTML = d.innerHTML + inp

                }
                else {
                    div.style.display = 'none';

                }
            },
            error: function(err) {
                console.log(err)
            }
        });

}
dbmonitor()
generateSpeech()
setInterval(function(){
    dbmonitor()



}, 20000);

setInterval(function(){
    dbmonitor()
    generateSpeech()


}, 60000);

$.fn.dataTable.ext.errMode = 'none';
window.onerror = function() {
    location.reload();
}

setInterval(function(){
   //window.location.reload(1);
    var ids = $('.sortedtable').map(function() {
        return this.id;
    }).get();

    var arrayLength = ids.length;

    for (var i = 0; i < arrayLength; i++) {
        generateTable(ids[i]);
    }

}, 10000);


setInterval(function(){

        var elements = document.getElementsByClassName("blink");

        for(var i = elements.length - 1; i >= 0; --i){
        // PERFORM STUFF ON THE ELEMENT

        if (elements[i].className.indexOf('danger') != -1){
            elements[i].classList.remove("btn-danger");
            elements[i].classList.add("btn-primary");
        }

        else{
            elements[i].classList.add("btn-danger");
            elements[i].classList.remove("btn-primary");
        }

        }

        var elements2 = document.getElementsByClassName("wrongver");
            for(var i = elements2.length - 1; i >= 0; --i){
        if (elements2[i].className.indexOf('warning') != -1){
            elements2[i].classList.remove("btn-warning");
            elements2[i].classList.add("btn-success");
        }

        else{
            elements2[i].classList.add("btn-warning");
            elements2[i].classList.remove("btn-success");
        }

        }

}, 100);
