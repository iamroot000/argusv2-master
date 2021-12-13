data = {}
content = document.getElementById('network')
scroll = true
alert=false

String.prototype.format = function () {
    var args = [].slice.call(arguments);
    return this.replace(/(\{\d+\})/g, function (a){
        return args[+(a.substr(1,a.length-2))||0];
    });
};


function generateLink(config,id,alertcode){
    var link = '{0}://{1}:{2}/chart.svg?type=graph&width=500&height=160&graphid=0&id={3}&username={4}&passhash={5}&x={6}&hide=-1'.format(
       config['scheme'],
       config['host'],
       config['port'],
       id,
       config['username'],
       config['passhash'],
       Math.floor(Math.random()*90000) + 10000
    )

    console.log(id,alertcode)
    if (alertcode == 1) {
        link = link + '&bgcolor=%23e5f442'

    }

    if (alertcode == 2) {
        link = link + '&bgcolor=%23ff9696'
        alert=true
    }

    if (alertcode == 3){
        link = link + '&bgcolor=%23ffa500'
    }

    return link

}
function generateGraphs(){
    var notok = document.getElementsByClassName('notok')
    for (var i=0;i<notok.length;i++){
            notok[i].innerHTML = ''
        }



    for (var k in data['data']){
        var column = document.getElementById(k)
        for (var i=0;i<data['data'][k].length;i++){
            if (data['data'][k][i]){
                var imp = '<img class="img fluid" src="{0}">'.format(generateLink(data['config'],data['data'][k][i]['id'],data['data'][k][i]['alert']))
                column.innerHTML = column.innerHTML +  '<div class="row">'+ imp + "</div>"
            }
        }
    }

}


function startScroll(){
    if (scroll == true){
        console.log('startscr')
        $('#network').animate({
        scrollTop: $('#network')[0].scrollHeight,
        }, { duration: 30000, queue: false });
    }
}


function scrollSet(){
    console.log(scroll)
    if (scroll == true){
            $('#network').stop()
            scroll=false

    }
    else{
        scroll=true
        startScroll()
    }
}

function procData(){
    console.log('START DATA')
    alert = false
    $.ajax({
        type: "GET",
        url: "/nrmt/network/?graphlist=get",
        cache: false,
        success: function (res) {
            data = res
        },
        error: function(err) {
            console.log(err)
        },
        complete: function(){
            $('#network').scrollTop(0);
            generateGraphs()
            //startScroll()
            if (alert == true){
                document.getElementById('xyz').play();

            }
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
//startScroll()