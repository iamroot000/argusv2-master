String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};
function getJson(data) {
    return data ? typeof(data) == "string"? JSON.parse(data) : data : [];
}
function refreshgroupcontacts() {
    $.ajax({
        type: "GET",
        url: "/smsalerts/ajax/contacts",
        data: {
            "name" : $('#grouplist').find(":selected").text()
        },
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {

            lizt = getJson(data);
            htmldata = "";
            for (var i in lizt) {
                htmldata += '<li>{0}</li>'.format(lizt[i]);
            }
            $('#group_contacts').html(htmldata);
        }
    });
}

function refreshgroups() {
    $.ajax({
        type: "GET",
        url: "/smsalerts/ajax/groups",
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {
            lizt = getJson(data);
            htmldata = '<option disabled="" selected="">...</option>';
            for (var i in lizt) {
                htmldata += '<option>{0}</option>'.format(lizt[i]);
            }
            $('#grouplist').html(htmldata);
        }
    });
}

function refreshannouncers() {
    var templ8 = '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td><button class=\'btn btn-primary\' onclick=\'haltAlert({0});\'>Stop Alert</button></td></tr>'
    $.ajax({
        type: "GET",
        url: "/smsalerts/ajax/announcers",
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {
            lizt = getJson(data);

            htmldata = '';
            for (var i in lizt) {
                elem = lizt[i];
                htmldata += templ8.format(elem[0],elem[1],elem[2],elem[3]);
            }
            $('#alertlist').html(htmldata);
        }
    });
}


function addAlert(is_single) {
    if (confirm(is_single? "Do you confirm sending this text?" : "Do you confirm raising this alert broadcast?"))
        $.ajax({
            type: "PUT",
            url: "/smsalerts/ajax/announcers",
            data : {
                "group_name" : $('#grouplist').find(":selected").text(),
                "text" : $("#txttitle").val() + " - "+ $('#txt').val(),
                "just_once" : is_single? 1 : 0
            },
            xhrFields: {
                withCredentials: true
            },
            success: function(data) {
                refreshannouncers();
                is_single? alert("The message has been sent!") : alert("Your alert has now been raised!")
            }
        });
}

function haltAlert(alert_id) {
    var goodbye_message = prompt("What is your reason for ending this alert?");
    $.ajax({
        type: "DELETE",
        url: "/smsalerts/ajax/announcers",
        data : {
            "id" : alert_id,
            "message" : goodbye_message
        },
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {
            refreshannouncers();
        }
    });
}


$(document).ready(function(){
    refreshgroups();
    refreshannouncers();
    setInterval(refreshannouncers,5000);
});