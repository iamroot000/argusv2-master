String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

deployable = $("#deployable").select2();


function testRE(hostgroup){
    var patt = new RegExp(/^(\S+)-([a-zA-Z_]+[a-zA-Z_0-9]+[a-zA-Z_]+)$/g);

    //alert(patt.test(hostgroup))
    return patt.test(hostgroup);
}

function startDeploy(){
    var prompt = confirm('Deploy Hostgroup?')
    if (prompt){
        var hostgroup = document.getElementById('deployable')

        if (testRE(hostgroup.value)){
            var newData = {
                "hostgroup":hostgroup.value,
            }
            $.ajax({
                type: "POST",
                dataType: "json",
                url: window.location,
                data: JSON.stringify(newData),
                success: function(result) {
                    showResults(result)
                },
                error: function(err) {
                    console.log(err)
                },
                complete: function() {
                    alert('Process Finished, see results.')
                }
            });
        }

        else{
            alert("Invalid, follow ^(\\S+)-([a-zA-Z_]+[a-zA-Z_0-9]+[a-zA-Z_]+)$")
        }
    }
}


function reloadHosts(){
    $.ajax({
        type: "GET",
        url: '/puppet/reload',
        cache: false,
        success: function (data) {
            var res = document.getElementById('results')
            res.innerHTML=JSON.stringify(data)
            alert("Hosts reloaded, refreshing page...")
            location.reload()
        },
        error: function(err) {
            console.log(err)
        },
    });

}


function showResults(result){
    var res = document.getElementById('results')
    res.innerHTML = result['result']

}