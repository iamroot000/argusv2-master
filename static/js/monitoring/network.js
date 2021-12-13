data = {}

String.prototype.format = function () {
    var args = [].slice.call(arguments);
    return this.replace(/(\{\d+\})/g, function (a){
        return args[+(a.substr(1,a.length-2))||0];
    });
};


function showGraphs(){
    var content = document.getElementById('network-dashboard')

    content.innerHTML = ''

    for(var k in data){
        var column = '<div class="col-sm-3 scrollable" id="column-{0}"></div>'.format(k)
        content.innerHTML = content.innerHTML + column

        var columnElem = document.getElementById('column-{0}'.format(k))

        for (var p in data[k]){
            var row = '<div class="row"><img class="img-responsive" src="/monitoring/graph/{0}?m={1}"/></div>'.format(data[k][p],Math.floor(Math.random()*90000) + 10000)
            columnElem.innerHTML = columnElem.innerHTML + row
        }

    }

}


function procData(){
    console.log('START DATA')
    alert = false
    $.ajax({
        type: "GET",
        url: "/monitoring/?q=getNetworkDashboard",
        cache: false,
        success: function (res) {
            data = res['data']
        },
        error: function(err) {
            console.log(err)
        },
        complete: function(){
            showGraphs()
            poll()
        },
    });
}

function poll(){
   setTimeout(function(){
      procData()
  }, 30000);
}

procData()
