String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

function generateResults(data){

    var tableDIV = document.getElementById('searchResults')
    var table = '<table class="table table-responsive table-striped"><thead><tr><th>Results:</th></tr></thead><tbody>'
    for (var k in data['domains']){

        table = table + "<tr><td align='center'>"
        table = table + "<a href='https://www.{0}' target='_blank' id='{0}' >https://www.{0} |<i class='fa fa-link'></i> Open in new tab</a>".format(data['domains'][k])

        table = table + '| <a href="#" onclick="clipboard(\'{0}\')" ><i class="fa fa-clipboard"></i> Copy to Clipboard</a>'.format(data['domains'][k])

        table = table + "</td></tr>"
    }
    table = table + "</tbody></table>"
    tableDIV.innerHTML = table

}

function searchDomain(elem){
    var domain = document.getElementById('domain')


    userText = domain.value.replace(/^\s+/, '').replace(/\s+$/, '');
    if (userText === '') {
        alert('Please input a domain name')
    } else {
        var tableDIV = document.getElementById('searchResults')
        elem.disabled=true
        tableDIV.innerHTML = '<div class="col-lg-12"><h3>Fetching results...</h3></div>'
        $.ajax({
            type: "GET",
            url: '/dashboard/?q=searchSimilar&d={0}'.format(domain.value),
            cache: false,
            success: function (data) {

                generateResults(data)
                alert("Search Complete")
            },
            error: function(err) {
                tableDIV.innerHTML = ''
                alert("None Found")
            },
            complete: function(){
                elem.disabled=false
            }
    });
    }
}

function clipboard(elem){
    var clip = document.getElementById('clip')
    clip.style.display='block'
    clip.value='https://www.'+elem
    clip.select()
    document.execCommand("copy")
    clip.style.display='none'

    alert("https://www.{0} copied to clipboard".format(elem))
}