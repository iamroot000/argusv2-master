String.prototype.format = function () {
        var args = [].slice.call(arguments);
        return this.replace(/(\{\d+\})/g, function (a){
            return args[+(a.substr(1,a.length-2))||0];
        });
};

CONFIG = {}
APPLICATIONS = {}
CURRENT_APPLICATION_TYPE = ''
HOSTGROUPS = {}
DIRECTORY_TREE={}
CURRENT_FILE_CONTENT= {}

CURRENT_DIRECTORY = []

STREAM_LOG_END_FLAG = 'COMMAND END'
STREAM_FLAG = false

CURRENT_TEMPLATE = ''

host_control = $("#host_control").select2()
application_control = $("#application_control").select2()
hostgroup_control = $("#hostgroup_control").select2()

main_directory = $("#main_directory").select2()
create_path = $("#create_path").select2()
ip_search= $("#ip_search").select2()
template_name= $("#template_name").select2()

INCLUDE_FILES=[]

$("#COMMAND_MODAL").on("hide.bs.modal", function () {
    if (STREAM_FLAG == true){
        return false
    }
});

var texteditors={};

$(document).ready(function(){
     texteditors.editor_one = CodeMirror.fromTextArea(document.getElementById("filehandler"), {
         lineNumbers: true,
         matchBrackets: true,
         styleActiveLine: true,
         theme:"monokai",
         lineWrapping:true,
         autoRefresh: true,
         undoDepth:0
     });
     getConfig()

     $('#certstore').multiselect({
        beforeMoveToRight: function(left, right, options) {

            var h = $('#host_control').select2('data')[0]
            var a = $('#application_control').select2('data')[0]
            var hg =  $('#hostgroup_control').select2('data')[0]

            var resuls = false

            for(var i=0;i<options.length;i++){

                var nf = {
                    'source':options[i].value
                }
                $.ajax({
                    type: "POST",
                    dataType: "json",
                    url: '/esync/{0}/{1}/{2}/ssl/link/'.format(h.text,a.text,hg.text),
                    async:false,
                    data: JSON.stringify(nf),
                    success: function(result) {
                        if(result['is_successful'] == false){
                            alert('Failed to link '+options[i].value)
                        }
                        resuls= result['is_successful']

                    },
                    error: function(err) {
                        alert('Failed to link '+options[i].value)
                    }
                });
                if (resuls == false){
                    return false
                }
            }
            return true
        },
        beforeMoveToLeft: function(left, right, options) {
            var h = $('#host_control').select2('data')[0]
            var a = $('#application_control').select2('data')[0]
            var hg =  $('#hostgroup_control').select2('data')[0]

            var resuls = false

            for(var i=0;i<options.length;i++){

                var nf = {
                    'source':options[i].value
                }
                $.ajax({
                    type: "POST",
                    dataType: "json",
                    url: '/esync/{0}/{1}/{2}/ssl/unlink/'.format(h.text,a.text,hg.text),
                    async:false,
                    data: JSON.stringify(nf),
                    success: function(result) {
                        if(result['is_successful'] == false){
                            alert('Failed to unlink '+options[i].value)
                        }
                        resuls= result['is_successful']

                    },
                    error: function(err) {
                        alert('Failed to unlink '+options[i].value)
                    }
                });
                if (resuls == false){
                    return false
                }
            }
            return true
        },

    });
});

function changeHostgroupFocus(){
    var hg = $('#ip_search').select2('data')[0]

    $('#hostgroup_control').val(hg.id).trigger('change')

}

function setApplication(){
    var editSSL = document.getElementById('editSSL')
    var testButton = document.getElementById('testConfig')

    if (CURRENT_APPLICATION_TYPE === 'nginx'){
        editSSL.style.display = 'inline'
        testButton.style.display = 'inline'

    }
    else if (CURRENT_APPLICATION_TYPE === 'puppet'){
        editSSL.style.display = 'none'
        testButton.style.display = 'none'
    }


}

function getConfig(){
    $.ajax({
        type: "GET",
        url: '/esync/homeshit/?q=getConfig',
        cache: false,
        success: function (data) {
            CONFIG = data
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            getHostsFromConfig()
        }
    });
}

function getHostsFromConfig(){
    $('#host_control').html("")
    for (var k in CONFIG['config']['hosts']){
        var op = {
            id: CONFIG['config']['hosts'][k],
            text: CONFIG['config']['hosts'][k],
            value: CONFIG['config']['hosts'][k],
        }
        var new_host = new Option(op.text, op.id, false, false);
        host_control.append(new_host)
    }
    getApplications()
}

function getApplications(){
    $('#application_control').html("")
    var h = $('#host_control').select2('data')[0]

    $.ajax({
        type: "GET",
        url: '/esync/homeshit/?q=getApplications&h={0}'.format(h.text),
        cache: false,
        success: function (data) {
            APPLICATIONS = data
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            for (var k in APPLICATIONS['applications']){
                var op = {
                    id: k,
                    text: k,
                    value: APPLICATIONS['applications'][k],
                }
                var new_application = new Option(op.text, op.value, false, false);
                application_control.append(new_application)
            }
            getHostGroups()
        }
    });
}



function getHostGroups(){
    $('#hostgroup_control').html("")
    $('#ip_search').html("")

    var h = $('#host_control').select2('data')[0]
    var a = $('#application_control').select2('data')[0]

    CURRENT_APPLICATION_TYPE =a.id

    setApplication()
    $.ajax({
        type: "GET",
        url: '/esync/homeshit/?q=getHostGroups&h={0}&a={1}'.format(h.text,a.text),
        cache: false,
        success: function (data) {
            HOSTGROUPS = data
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            for (var k in HOSTGROUPS['hostgroups']){
                for (var l in HOSTGROUPS['hostgroups'][k]){
                    var op = {
                        id: l,
                        text: l,
                        value: l,
                    }
                    var new_hostgroup = new Option(op.text, op.value, false, false);
                    hostgroup_control.append(new_hostgroup)

                    var optgroup = '<optgroup label = "'+l.toUpperCase()+'">'
                    for (var ip in HOSTGROUPS['hostgroups'][k][l]){
                        var host = '<option value="'+l+'">'+HOSTGROUPS['hostgroups'][k][l][ip] +'</option>'
                        optgroup = optgroup + host
                    }
                    optgroup = optgroup + '</optgroup>'
                    ip_search.append(optgroup)
                }
            }
            getDirectoryTree(false)
        }
    });

}

function getHosts(){
    var h = $('#host_control').select2('data')[0]
    var hg =  $('#hostgroup_control').select2('data')[0]
    var hosts = document.getElementById('hosts')
    hosts.innerHTML=''

    $.ajax({
        type: "GET",
        url: '/esync/homeshit/?q=getHosts&h={0}&hg={1}'.format(h.text,hg.text),
        cache: false,
        success: function (data) {
            for (var k in data['hosts']){
                hosts.innerHTML = hosts.innerHTML + '<li>'+data['hosts'][k]+'</li>'
            }
        },
        error: function(err) {
            console.log(err);
        },
    });




}

function getDirectoryTree(focus){
    $('#main_directory').html("")
    $('#create_path').html("")


    var h = $('#host_control').select2('data')[0]
    var a = $('#application_control').select2('data')[0]
    var hg =  $('#hostgroup_control').select2('data')[0]
    $.ajax({
        type: "GET",
        url: '/esync/{0}/{1}/{2}/?q=getDirectoryTree'.format(h.text,a.text,hg.text),
        cache: false,
        success: function (data) {
            DIRECTORY_TREE = data['result']
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){

            var dirs = []
            getHosts()
            for (var k in DIRECTORY_TREE){
                var op = {
                    id: DIRECTORY_TREE[k],
                    text: DIRECTORY_TREE[k],
                    value: DIRECTORY_TREE[k],
                }



                var new_directory = new Option(op.text, op.id, false, false);
                main_directory.append(new_directory)

                if (k == 0){
                    $('#main_directory').val(DIRECTORY_TREE[k]).trigger('change')
                }

                var create_directory_arr = DIRECTORY_TREE[k].split('/')

                var new_dir = DIRECTORY_TREE[k].replace(create_directory_arr[create_directory_arr.length -1],'')
                if (!dirs.includes(new_dir)){

                    dirs.push(new_dir)
                    var new_path = new Option(new_dir,new_dir,false,false)
                    create_path.append(new_path)
                }

                if(DIRECTORY_TREE[k].endsWith('.include')== true){
                    INCLUDE_FILES.push(DIRECTORY_TREE[k])
                }


            }
            var current_dir = document.getElementById('main_directory').value


            var current_location= document.getElementById('current_location')
            current_location.innerHTML = '{0}/{1}/{2}'.format(h.text,a.text,hg.text)
            if (focus != false){
                $('#main_directory').val(focus).trigger('change')
            }


        getFile()

        }
    });
}

function setReadOnly(option){
    texteditors.editor_one.setOption('readOnly',option);
    var ro = document.getElementById('readonly')

    if (option == true){
        ro.style.display='inline'
    }
    else{
        ro.style.display='none'
    }
}

function getFile(){
    var h = $('#host_control').select2('data')[0]
    var a = $('#application_control').select2('data')[0]
    var hg = $('#hostgroup_control').select2('data')[0]
    var path = $('#main_directory').select2('data')[0]

    cancelEdit(false)
    texteditors.editor_one.getDoc().setValue("LOADING FILE...")

    $.ajax({
        type: "GET",
        url: '/esync/{0}/{1}/{2}/?q=readFile&path={3}'.format(h.text,a.text,hg.text,path.text),
        cache: false,
        success: function (data) {
            CURRENT_FILE_CONTENT = data['result']
        },
        error: function(err) {
            console.log(err);

            texteditors.editor_one.getDoc().setValue("ERROR LOADING FILE Error: {0}".format(err))
        },
        complete: function(){

            texteditors.editor_one.getDoc().setValue(CURRENT_FILE_CONTENT)
        }
    });
}

function editSSL_MODAL(){
    if (CURRENT_APPLICATION_TYPE == 'nginx'){
        var h = $('#host_control').select2('data')[0]
        var a = $('#application_control').select2('data')[0]
        var hg =  $('#hostgroup_control').select2('data')[0]
        var certstore = document.getElementById('certstore')
        var hoststore = document.getElementById('certstore_to')

        certstore.innerHTML=''
        hoststore.innerHTML=''
        $.ajax({
            type: "GET",
            url: '/esync/{0}/{1}/{2}/?q=getCertstore'.format(h.text,a.text,hg.text),
            cache: false,
            success: function (data) {
                var inp = ''
                for (var k in data['linked']){
                    inp = inp + '<option value="'+data['linked'][k]+'">'+data['linked'][k]+'</option>'
                }
                hoststore.innerHTML=inp
                inp = ''
                for (var k in data['not_linked']){
                    inp = inp + '<option value="'+data['not_linked'][k]+'">'+data['not_linked'][k]+'</option>'
                }
                certstore.innerHTML=inp
            },
            error: function(err) {
                console.log(err);
            },
            complete: function(){
                $("#SSL_MODAL").modal()
            }
        });
    }
}

function cancelEdit(reset){
    setReadOnly(true)
    var editButton = document.getElementById('editFile')
    var cancelButton = document.getElementById('cancelEdit')
    var deleteButton = document.getElementById('deleteFile')
    var saveButton = document.getElementById('saveFile')
    var createButton = document.getElementById('createFile')

    cancelButton.style.display='none'
    deleteButton.style.display='none'
    saveButton.style.display='none'

    editButton.style.display='inline'
    createButton.style.display='inline'

    if (reset != false){
        getFile()
    }
}

function editFile(){
    setReadOnly(false)
    var editButton = document.getElementById('editFile')
    var cancelButton = document.getElementById('cancelEdit')
    var deleteButton = document.getElementById('deleteFile')
    var saveButton = document.getElementById('saveFile')
    var createButton = document.getElementById('createFile')

    cancelButton.style.display='inline'
    deleteButton.style.display='inline'
    saveButton.style.display='inline'
    editButton.style.display='none'
    createButton.style.display='none'

}

function saveFile(){
    var prompt = confirm('Update File?')
    if (prompt){
        var h = $('#host_control').select2('data')[0]
        var a = $('#application_control').select2('data')[0]
        var hg =  $('#hostgroup_control').select2('data')[0]
        var path = $('#main_directory').select2('data')[0]

        var newData = {
            "path":path.text,
            "content":texteditors.editor_one.getValue()
        }
        $.ajax({
            type: "POST",
            dataType: "json",
            url: '/esync/{0}/{1}/{2}/?q=update'.format(h.text,a.text,hg.text),
            data: JSON.stringify(newData),
            success: function(result) {
                console.log(result)
            },
            error: function(err) {
                console.log(err)
            },
            complete: function() {
                getFile()
                alert('File Updated')
            }
        });
    }
}

function deleteFile(){
    var prompt = confirm('Delete File?')
    if (prompt){
        var h = $('#host_control').select2('data')[0]
        var a = $('#application_control').select2('data')[0]
        var hg =  $('#hostgroup_control').select2('data')[0]
        var path = $('#main_directory').select2('data')[0]

        var newData = {
            "path":path.text,
        }
        $.ajax({
            type: "POST",
            dataType: "json",
            url: '/esync/{0}/{1}/{2}/?q=delete'.format(h.text,a.text,hg.text),
            data: JSON.stringify(newData),
            success: function(result) {
                console.log(result)
            },
            error: function(err) {
                console.log(err)
            },
            complete: function() {
                alert('File Deleted')
                getDirectoryTree(false)
            }
        });
    }
}

function getTemplates(){
    $('#template_name').html("")

    $.ajax({
        type: "GET",
        url: '/esync/templates/{0}'.format(CURRENT_APPLICATION_TYPE),
        cache: false,
        success: function (data) {
            var op = {
                id: 'blank',
                text: '-',
                value: 'blank',
            }
            var new_template = new Option(op.text, op.value, false, false);

            template_name.append(new_template)

            for (var k in data['templates']){
                var op = {
                    id: data['templates'][k],
                    text: data['templates'][k],
                    value: data['templates'][k],
                }
                var new_template = new Option(op.text, op.value, false, false);
                template_name.append(new_template)
            }
        },
        error: function(err) {
            console.log(err);
        },

    });

}
function createFile_MODAL(){
    getTemplates()
    var vars_row = document.getElementById('vars_row')
    var create_content = document.getElementById('create_content')

    vars_row.innerHTML = ''
    create_content.innerHTML=''

    $("#CREATE_MODAL").modal()

}

function setTemplate(){
    var create_content = document.getElementById('create_content')
    var t = $('#template_name').select2('data')[0]
    var vars_row = document.getElementById('vars_row')
    var create_content = document.getElementById('create_content')

    vars_row.innerHTML = ''
    create_content.innerHTML=''
    if (t.text != '-'){
        $.ajax({
            type: "GET",
            url: '/esync/templates/{0}?q=getTemplate&t={1}'.format(CURRENT_APPLICATION_TYPE,t.text),
            cache: false,
            success: function (data) {
                create_content.innerHTML = data['template']
                CURRENT_TEMPLATE = data['template']
                for (var k in data['vars']){
                    if (data['vars'][k] == '{includepath}'){
                        var row = '<br/><div class="row"><select class="varss form-control select2" data-placeholder="{0}" style="width:100%;" maxlength=100 id="{0}" onChange="setVars()">'.format(data['vars'][k])
                        row = row + '<option value="">-</option>'
                        for (var s in INCLUDE_FILES){
                            row = row + '<option value={0}>{0}</option>'.format(INCLUDE_FILES[s])
                        }
                        row = row + '</select></div>'
                    }
                    else{
                        var row = '<br/><div class="row"><input class="varss form-control" placeholder="{0}" style="width:100%;" maxlength=100 id="{0}" onkeyup="setVars()"></div>'.format(data['vars'][k])
                    }
                    vars_row.innerHTML = vars_row.innerHTML + row
                }
            },
            error: function(err) {
                console.log(err);
            },
        });
    }
    else{
        create_content.innerHTML = 'NEW FILE'
    }
}

function setVars(){
    var varscls = document.getElementsByClassName('varss')
    var create_content = document.getElementById('create_content')
    var templ = CURRENT_TEMPLATE
    for (var k=0;k<varscls.length;k++){
        var r = varscls[k].id
        var re = new RegExp(r,"g")
        templ= templ.replace(re, varscls[k].value)
    }
    create_content.innerHTML = templ
}


function createFile(){
    var h = $('#host_control').select2('data')[0]
    var a = $('#application_control').select2('data')[0]
    var hg =  $('#hostgroup_control').select2('data')[0]
    var dir =  $('#create_path').select2('data')[0]
    var filename = document.getElementById('create_filename').value

    var t = $('#template_name').select2('data')[0]
    var varss = document.getElementsByClassName('varss')
    var cont = false
    var newData = {
            "path":"{0}{1}".format(dir.text,filename),
            'vars': {},
            'template': t.text,
        }
    for ( var i =0; i<varss.length;i++){
        newData['vars'][varss[i].id]=varss[i].value

    }
    if(newData['path'])

    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/esync/{0}/{1}/{2}/?q=create'.format(h.text,a.text,hg.text),
        data: JSON.stringify(newData),
        success: function(result) {

            if (result['isSuccessful'] == false){
                alert(result['result'])
            }
            else{
                alert('File Created')
                getDirectoryTree(newData['path'])
                $("#CREATE_MODAL").modal('hide')
            }
        },
        error: function(err) {
            console.log(err)
            alert(err)
        },
    });
}

function testConfig(){
    var h = $('#host_control').select2('data')[0]
    var a = $('#application_control').select2('data')[0]
    var hg =  $('#hostgroup_control').select2('data')[0]

    var execute_content = document.getElementById('execute_content')

    execute_content.innerHTML=''

    $("#COMMAND_MODAL").modal()
    STREAM_FLAG = true

    var newData = {
            "test":true,
        }
    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/esync/{0}/{1}/{2}/?q=test'.format(h.text,a.text,hg.text),
        data: JSON.stringify(newData),
        success: function(result) {
            if (result[0] === true){
                execute_content.innerHTML = execute_content.innerHTML + "TEST RESULT: <span style='color:green'>{0}</span>\n\nCOMMAND: {1}\n\nRESULT:\n{2}".format("OK!",result[1],result[2])
            }
            else {
                execute_content.innerHTML = execute_content.innerHTML + "TEST RESULT: <span style='color:red'>{0}</span>\n\nCOMMAND: {1}\n\nRESULT:\n{2}".format("FAILED",result[1],result[2])
            }
            STREAM_FLAG = false

        },
        error: function(err) {
            execute_content.innerHTML = err

        },
    });

}

function syncConfig(){
    var h = $('#host_control').select2('data')[0]
    var a = $('#application_control').select2('data')[0]
    var hg =  $('#hostgroup_control').select2('data')[0]
    var execute_content = document.getElementById('execute_content')

    execute_content.innerHTML=''

    $("#COMMAND_MODAL").modal()
    STREAM_FLAG = true

    var newData = {
            "sync":true,
        }

    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/esync/{0}/{1}/{2}/?q=sync'.format(h.text,a.text,hg.text),
        data: JSON.stringify(newData),
        success: function(result) {
            for (var k in result){
                if (result[k][0] === true || result[k][0] === false){
                    execute_content.innerHTML = execute_content.innerHTML + "{0}\n{1}\n\n".format(result[k][1],result[k][2])
                    if (result[k][0] === false){
                        STREAM_FLAG = false
                    }

                }
                else if (result[k][0] === 'stream'){
                    execute_content.innerHTML = execute_content.innerHTML + "START COMMAND {0}\n\n".format(result[k][1])
                    pollLog(result[k][2],0)
                }
            }

        },
        error: function(err) {
            execute_content.innerHTML = err
        },
    });

}

function getLog(logfile,offset){
    var h = $('#host_control').select2('data')[0]
    var execute_content = document.getElementById('execute_content')
    var command_modal = document.getElementById("COMMAND_MODAL");

    $.ajax({
        type: "GET",
        url: '/esync/homeshit/?q=getLog&h={0}&log={1}&o={2}'.format(h.text,logfile,offset),
        cache: false,
        success: function (data) {
            for (var k in data['log'][1]){
                execute_content.innerHTML = execute_content.innerHTML + data['log'][1][k]
                command_modal.scrollTop = command_modal.scrollHeight;

            }
            if (data['log'][1][data['log'][1].length -1] != STREAM_LOG_END_FLAG){
                pollLog(logfile,data['log'][0]+offset)
            }
            else {
                STREAM_FLAG = false
            }
        },
        error: function(err) {
            console.log(err);
        },
    });
}

function pollLog(logfile,offset){
    getLog(logfile,offset)
}


































