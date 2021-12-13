$('#addspecialDomainModal').on('show.bs.modal', function (event) {
        var myNode = document.getElementById("special_domains");
        while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
        }
        var project = $('#project').val();
      var dataString = 'id=' + project;

        $.ajax({
            type: "GET",
            url: "getspecialdomains/",
            data: dataString,
            cache: false,
            success: function (data) {
                   var domlen = data.length;

                for (var i =0; i<domlen; i++){

                    $('#special_domains').append($('<option>', {
                        id : data[i]['text'],
                        value: data[i]['text'],
                        text : data[i]['text'],
                        selected : 'selected',
                    }));

                }

            },
            error: function(err) {
                console.log(err);
            }
        });
})

$('#addfunctionDomainModal').on('show.bs.modal', function (event) {
        var myNode = document.getElementById("function_domains");
        while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
        }
        var project = $('#project').val();
      var dataString = 'id=' + project;

        $.ajax({
            type: "GET",
            url: "getfunctiondomains/",
            data: dataString,
            cache: false,
            success: function (data) {
                   var domlen = data.length;

                for (var i =0; i<domlen; i++){

                    $('#function_domains').append($('<option>', {
                        id : data[i]['text'],
                        value: data[i]['text'],
                        text : data[i]['text'],
                        selected : 'selected',
                    }));

                }

            },
            error: function(err) {
                console.log(err);
            }
        });
})

$('#addblockedDomainModal').on('show.bs.modal', function (event) {
        var myNode = document.getElementById("blocked_domains");

        if (myNode.firstChild){
        while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
        }}
        var project = $('#project').val();
      var dataString = 'id=' + project;

        $.ajax({
            type: "GET",
            url: "getblockeddomains/",
            data: dataString,
            cache: false,
            success: function (data) {
                   var domlen = data.length;

                for (var i =0; i<domlen; i++){

                    $('#blocked_domains').append($('<option>', {
                        id : data[i]['text'],
                        value: data[i]['text'],
                        text : data[i]['text'],
                        selected : 'selected',
                    }));

                }

            },
            error: function(err) {
                console.log(err);
            }
        });
})


$(".select2").select2({
        tags:true,
});

$("#blocked_domains").select2({


        minimumInputLength: 3,

        ajax: {
        url: 'getdomains/',
        dataType: "json",
        type: "GET",
        data: function (params) {


            var queryParameters = {
                term: params.term
            }
            return queryParameters;
        },
        processResults: function (data) {
            return {
                results: $.map(data.items, function (item) {

                    return {
                        text: item.id,
                        id: item.id
                    }
                })
            };
        },

    }


});

$('#DomainDetailsModal').on('show.bs.modal', function (event) {
         document.getElementById("domaindet").disabled = true;

         document.getElementById("editdet").style.visibility = 'visible';
         document.getElementById("addDomaindet").disabled = true;
         document.getElementById("domaindet").innerHTML = '';




        var button = $(event.relatedTarget) // Button that triggered the modal
          var recipient = button.data('value') // Extract info from data-* attributes
          var modal = $(this);
          var dataString = 'domain=' + recipient;
      document.getElementById("detail_title").innerHTML = recipient;
      document.getElementById("domain_name").value = recipient;

        $.ajax({
            type: "GET",
            url: "getdomaindetails/",
            data: dataString,
            cache: false,
            success: function (data) {

                document.getElementById("domaindet").innerHTML=data['details']

            },
            error: function(err) {
                console.log(err);
            }
        });
})


function enabletext(){
    document.getElementById("domaindet").disabled = false;
    document.getElementById("editdet").style.visibility = 'hidden';
    document.getElementById("addDomaindet").disabled = false;


}

$('*[data-poload]').hover(function() {
    var e=$(this);

    e.unbind('hover');
    $.get(e.data('poload'),function(d) {
        e.popover({content: d['details']}).popover('show');
    });
});

$('html').on('mouseup', function(e) {
    if(!$(e.target).closest('.popover').length) {
        $('.popover').each(function(){
            $(this.previousSibling).popover('hide');
        });
    }
});