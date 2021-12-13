file = $("#file").select2()
dirs = $("#dir").select2();
dirs_new = $("#dir_new").select2();


standard_dirs = ['80','443','80-443']
FILELIST = {}
requestHandler = false
pagecounter = 0

currentfilehash = ''


entity = $("#entity").select2()
entity_function = $("#entity_function").select2()

sip = $("#sip").select2();

ENTITYLIST = {}
getentities()

HOSTGROUP = ''

r = 0;
lline = '';


url = new URL(window.location.href);
get_ip = url.searchParams.get("ip");

function getentities(){

    $.ajax({
        type: "GET",
        url: '/esync/?entitylist=get',
        cache: false,
        success: function (data) {
            ENTITYLIST = data
            for (var k in ENTITYLIST['ENTITYLIST']){
                var op = {
                    id: k,
                    text: k.toUpperCase(),
                    value: k,
                }

                var e = new Option(op.text, op.id, false, false);
                entity.append(e)

            }
        },
        error: function(err) {
            console.log(err);
        },
        complete: function(){
            getFunction()
            var entity_selected = document.getElementById('entity').value
            var entity_function_selected = document.getElementById('entity_function').value
            HOSTGROUP = entity_function_selected
            getfileset(HOSTGROUP)
            var title = document.getElementById('hgr').innerHTML=HOSTGROUP

            h = '<option disabled selected>IP...</option>'
            sip.append(h)

            for (var k in ENTITYLIST['ENTITYLIST']){
                for (var l in ENTITYLIST['ENTITYLIST'][k]){
                    var jumpflag = false
                    var opt = '<optgroup label = "'+l.toUpperCase()+'">'
                    for (var p=0;p<ENTITYLIST['ENTITYLIST'][k][l]['ip'].length;p++){
                        h = '<option value="'+k+'" f="'+l+'">'+ENTITYLIST['ENTITYLIST'][k][l]['ip'][p]+'</option>'
                        opt = opt + h
                       }
                    opt = opt + '</optgroup>'
                    sip.append(opt)

                    if (get_ip){
                   
                        if (ENTITYLIST['ENTITYLIST'][k][l]['ip'].includes(get_ip)){
                            console.log(get_ip,k,l)
                                $('#entity').val(k).trigger('change')
                                $('#entity_function').val(l).trigger('change')
                        }
                    }
                    

                }
            }
            var title = document.getElementById('hgr').innerHTML=HOSTGROUP

        }

    });
}


function getFunction(){
    var entity_selected = document.getElementById('entity').value
    $('#entity_function').html('')

    for (var k in ENTITYLIST['ENTITYLIST'][entity_selected]){

        var op = {
            id: k,
            text:ENTITYLIST['ENTITYLIST'][entity_selected][k]['type'].toUpperCase(),
            value: k,
        }

        var e_f = new Option(op.text, op.value, false, false);
        entity_function.append(e_f)

    }

    var entity_selected = document.getElementById('entity').value
    var entity_function_selected = document.getElementById('entity_function').value
    HOSTGROUP = entity_function_selected
    getfileset(HOSTGROUP)

    var title = document.getElementById('hgr').innerHTML=HOSTGROUP

    document.getElementById('searchDiv').style.display='none'



}

function getfileset(){
    $('#dir').html("")
    $('#dir_new').html("")
    var entity_selected = document.getElementById('entity').value
    var entity_function_selected = document.getElementById('entity_function').value
    HOSTGROUP = entity_function_selected

    $.ajax({
        type: "GET",
        url: '/esync/'+HOSTGROUP+'/?getfilelist=get',
        cache: false,
        success: function (data) {

            FILELIST = data

            for (var k in data['FILES']){
                var op = {
                    id: k,
                    text: k,
                    value: k,
                }

                var newDir = new Option(op.text, op.id, false, false);
                var newDir2 = new Option(op.text, op.id, false, false);
                dirs_new.append(newDir2)
                dirs.append(newDir)
            }
            getfilefromdir(document.getElementById('dir'))

        },
        error: function(err) {
            console.log(err);
        },

    });

    var hostip = document.getElementById('hostip')
    hostip.innerHTML=''

    //console.log(ENTITYLIST['ENTITYLIST'][entity_selected][entity_function_selected]['ip'])

    for (var i = 0;i<ENTITYLIST['ENTITYLIST'][entity_selected][entity_function_selected]['ip'].length;i++){
        hostip.innerHTML = hostip.innerHTML + '<li>'+ENTITYLIST['ENTITYLIST'][entity_selected][entity_function_selected]['ip'][i]+'</li>'
    }
    document.getElementById('searchDiv').style.display='none'
    document.getElementById('hgr_count').innerHTML = ENTITYLIST['ENTITYLIST'][entity_selected][entity_function_selected]['ip'].length

    document.getElementById('au').innerHTML='Allowed Users:'

    if (ENTITYLIST['ENTITYLIST'][entity_selected][entity_function_selected].hasOwnProperty('users')){
        for (var i=0;i<ENTITYLIST['ENTITYLIST'][entity_selected][entity_function_selected]['users'].length;i++){
            document.getElementById('au').innerHTML =document.getElementById('au').innerHTML + ' ' +ENTITYLIST['ENTITYLIST'][entity_selected][entity_function_selected]['users'][i]
        }
    }
    else{
        document.getElementById('au').innerHTML='Allowed Users: ALL'

    }

    var title = document.getElementById('hgr').innerHTML=HOSTGROUP


}



function getConfig(filename){
    texteditors.editor_one.setOption('readOnly',true);
    if (filename != ''){
        document.getElementById('cancelEditDIV').style.display='none'
        document.getElementById('saveEditDIV').style.display='none'
        var dir = document.getElementById('dir').value
        var destfile = filename
        var dataString = 'dir=' + dir +'&file='+destfile;


        $.ajax({
            type: "GET",
            url: '/esync/'+HOSTGROUP+'/',
            data: dataString,
            async: false,
            cache: false,
            success: function (data) {
                if(FILELIST['W']){
                        document.getElementById('deleteDIV').style.display='inline'
                    }
                if (standard_dirs.includes(dir)){
                    document.getElementById('editCodeDIV').style.display='none'
                }
                else{
                    if(FILELIST['W']){
                        document.getElementById('editCodeDIV').style.display='inline'
                    }
                }
                currentfilehash=data['hash']
                texteditors.editor_one.getDoc().setValue(data['content']);
            },
        });
    }
    else{
        texteditors.editor_one.getDoc().setValue('Select a file');
    }
}


function getfilefromdir(dir){
        var file_select = document.getElementById('filediv')
        var textrow = document.getElementById('textrow')
        var sslrow = document.getElementById('sslrow')

        document.getElementById('cancelEditDIV').style.display='none'
        document.getElementById('editCodeDIV').style.display='none'
        document.getElementById('saveEditDIV').style.display='none'


        if(dir.value == 'ssl'){
            document.getElementById('deleteDIV').style.display='none'
            file_select.style.display='none'
            textrow.style.display='none'
            sslrow.style.display='block'

            var certstore = document.getElementById('certstore')
            var hoststore = document.getElementById('certstore_to')
            var inp = ''
            for (var i=0;i<FILELIST['FILES']['ssl'].length;i++){
                inp = inp + '<option value="'+FILELIST['FILES']['ssl'][i]+'">'+FILELIST['FILES']['ssl'][i]+'</option>'
            }
            hoststore.innerHTML=inp

            $.ajax({
                type: "GET",
                url:'/esync/'+HOSTGROUP+'/'+'?certstore=get',
                cache: false,
                success: function (data) {
                    var inp = ''
                    for (var i=0;i<data['certstore'].length;i++){
                        if (!FILELIST['FILES']['ssl'].includes(data['certstore'][i])){
                        inp = inp + '<option value="'+data['certstore'][i]+'">'+data['certstore'][i]+'</option>'
                        }
                    }
                    certstore.innerHTML=inp
                },
                error: function(err) {
                    console.log(err);
                }


            });
        }

        else{

            if(standard_dirs.includes(dir.value) == false){
             document.getElementById('readonly').style.display='inline'
                if(FILELIST['W'] ==true){
                    document.getElementById('readonly').style.display='none'
                    document.getElementById('editCodeDIV').style.display='inline'
                    document.getElementById('deleteDIV').style.display='inline'
                }
            }

            file_select.style.display='block'
            textrow.style.display='block'
            sslrow.style.display='none'
            $('#file').empty()
            for(var i=0;i<FILELIST['FILES'][dir.value].length;i++){

                var os = {
                    id: FILELIST['FILES'][dir.value][i],
                    text: FILELIST['FILES'][dir.value][i],
                    value: FILELIST['FILES'][dir.value][i],
                }
                var newfile = new Option(os.text, os.id, false, false);
                file.append(newfile);
            }
            file.trigger('change')
        }

}

var texteditors={};

$(document).ready(function(){

     texteditors.editor_one = CodeMirror.fromTextArea(document.getElementById("filehandler"), {
         lineNumbers: true,
         matchBrackets: true,
         styleActiveLine: true,
         theme:"monokai",
         lineWrapping:true,
         autoRefresh: true,
     });

     texteditors.editor_two = CodeMirror.fromTextArea(document.getElementById("filehandler_new"), {
         lineNumbers: true,
         matchBrackets: true,
         styleActiveLine: true,
         theme:"monokai",
         lineWrapping:true,
         autoRefresh: true,
     });


});

$(document).ready(function() {

    $('#certstore').multiselect({
        beforeMoveToRight: function(left, right, options) {
            var resuls = false

            for(var i=0;i<options.length;i++){

                var nf = {
                    'source':options[i].value
                }
                $.ajax({
                            type: "POST",
                            dataType: "json",
                            url: '/esync/'+HOSTGROUP+'/link/',
                            async:false,
                            data: JSON.stringify(nf),
                            success: function(result) {
                                if(result['status'] == false){
                                    alert('Failed to link '+options[i].value)
                                }
                                resuls= result['status']

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
            var resuls = false

            for(var i=0;i<options.length;i++){

                var nf = {
                    'source':options[i].value
                }
                $.ajax({
                            type: "POST",
                            dataType: "json",
                            url: '/esync/'+HOSTGROUP+'/link/?remove=true',
                            async:false,
                            data: JSON.stringify(nf),
                            success: function(result) {
                                if(result['status'] == false){
                                    alert('Failed to unlink '+options[i].value)
                                }
                                resuls= result['status']

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



function editCode(){
    if(FILELIST['W'] ==true){
        document.getElementById('cancelEditDIV').style.display='inline'
        document.getElementById('editCodeDIV').style.display='none'
        document.getElementById('saveEditDIV').style.display='inline'
        document.getElementById('deleteDIV').style.display='none'

        texteditors.editor_one.setOption('readOnly',false);
    }
}
function cancelEdit(){
    if(FILELIST['W'] ==true){
        document.getElementById('cancelEditDIV').style.display='none'
        document.getElementById('editCodeDIV').style.display='inline'
        document.getElementById('saveEditDIV').style.display='none'
        document.getElementById('deleteDIV').style.display='inline'
        file.trigger('change')
    }
    texteditors.editor_one.setOption('readOnly',true);
}

function saveEdit(){
    if(FILELIST['W'] ==true){
        document.getElementById('cancelEditDIV').style.display='none'
        document.getElementById('editCodeDIV').style.display='inline'
        document.getElementById('saveEditDIV').style.display='none'
        document.getElementById('deleteDIV').style.display='inline'
        texteditors.editor_one.setOption('readOnly',true);

        var d = document.getElementById('dir').value
        nf={
            'dir':d,
            'conf':[],
            'edit':true,
        }
        nd={}

        nd[document.getElementById('file').value]=texteditors.editor_one.getValue()
        nf['conf'].push(nd)
        var dummy = document.createElement('p')
        dummy.setAttribute('file',document.getElementById('file').value)
        dummy.setAttribute('dir',nf['dir'])
        sendBody(nf)
        setTimeout(function() {
            changeFocus(dummy)
        }, 500);

    }

}





function changeFocus(elem){
    $("#dir").val(elem.getAttribute("dir")).trigger('change')
    $("#file").val(elem.getAttribute("file")).trigger('change')
}

function createFileInvoke(){
    document.getElementById('newDomainDiv').innerHTML='';
    $('#dir_new').trigger('change');
    texteditors.editor_two.getDoc().setValue('\n\n\n\n');

            setTimeout(function() {
                     texteditors.editor_two.refresh()
                    }, 100);

    $("#newFile_MODAL").modal()
}


function resetCode(){
    var codeblock = document.getElementById('generatedCode')
    var createButton = document.getElementById('createButton')
    codeblock.innerHTML=''
    var s = document.getElementById('dir_new').value
    if(standard_dirs.includes(s)){
        createButton.disabled = true
    }
}

function changeNewForm(elem){
    resetCode()
    document.getElementById('newDomainDiv').innerHTML='';
    var dir = elem.value
    var createButton = document.getElementById('createButton')
    var generateButton = document.getElementById('generateButton')
    var formDiv = document.getElementById('newDomainDiv');
    var codeblock = document.getElementById('generatedCode')
    var filehandler = document.getElementById('filehandler_container')

    if (standard_dirs.includes(dir)){

        codeblock.style.display = 'block'
        filehandler.style.display = 'none'
        inp = '<hr/><form id=newConfigForm onkeypress="resetCode()" onchange="resetCode()">'
        inp = inp + '<div class="form-group"><label>Http Host</label><input class="form-control newBlock" id="http_host" required></div>'

        inp = inp + '<div class="form-group"><label>Include</label><select class="form-control newBlock" id="include_file">'
        for (var l = 0; l<FILELIST['FILES']['include'].length;l++){
            inp = inp + '<option value="'+FILELIST['FILES']['include'][l]+'">'
            inp = inp +FILELIST['FILES']['include'][l]+'</option>'
        }
        inp = inp + '</select></div>'

        inp = inp + '</form>'
        formDiv.innerHTML=inp
        createButton.style.display='inline'
        generateButton.style.display='inline'
    }
    else if(dir =='ssl'){
            var dummy = document.createElement('p')
            dummy.setAttribute('dir','ssl')
            $("#newFile_MODAL").modal('hide')
            changeFocus(dummy)
    }
    else {
        var formDiv = document.getElementById('filename_container')
        inp = '<form id=newConfigForm">'

        if(['global','other'].includes(dir)){
            inp = inp + '<label>Filename? <i>$filename.conf</i></label><input class="form-control" id="filename" >'
        }
        else{
            inp = inp + '<label>Filename? <i>$filename.include</i></label><input class="form-control" id="filename" >'
        }
        inp = inp + '</form><hr/>'
        formDiv.innerHTML = inp

        if (FILELIST['W'] == false){
            texteditors.editor_two.setOption('readOnly',true);
            texteditors.editor_two.getDoc().setValue('You are not authorized to create non standard configurations');
        }
        else{
            texteditors.editor_two.getDoc().setValue('\n\n\n\n');
            texteditors.editor_two.setOption('readOnly',false);
            texteditors.editor_two.refresh()

            createButton.disabled=false
        }
        texteditors.editor_two.refresh();
        codeblock.style.display = 'none'
        filehandler.style.display = 'block'
        createButton.style.display='inline'
        generateButton.style.display='none'
    }
}

function re_match(str,rtype){
    var d_new = document.getElementById('dir_new').value
    if(rtype == 'http_host' ){
        var patt = /(^(([a-zA-Z0-9\-\_]+)\.)+([a-zA-Z]+)$)/g
    }
    return patt.test(str)
}

function generateConfig(){

    var d_new = document.getElementById('dir_new').value
    var codeblock = document.getElementById('generatedCode')
    codeblock.innerHTML=''

    var createButton = document.getElementById('createButton')
    var nc = document.getElementsByClassName('newBlock')
    var nf = {
            'dir':d_new,
            'conf':[]
        }

    var nd = {}
    for (var i=0;i<nc.length;i++){
        var d = null
        if (nc[i].type == 'text'){
            var par = nc[i].parentNode
            if (re_match(nc[i].value,nc[i].id) || par.style.display =='none' || nc[i].disabled == true){
                par.className = par.className.replace('has-error','')
            }
            else{
                alert('Invalid '+nc[i].id)
                codeblock.innerHTML = 'INVALID PARAMETERS!'
                par.className += ' has-error'
                createButton.disabled=true
                return
            }
        }
        if (nc[i].type == 'checkbox'){
            d = nc[i].checked
        }
        else{
            d = nc[i].value
        }
        nd[nc[i].id] = d
    }

    nf['conf'].push(nd)
    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/esync/'+HOSTGROUP+'/generate/',
        data: JSON.stringify(nf),
        success: function(result) {

             if (result['status'] == true){
                 for(var k in result['code']){
                    var path = k + ' '

                    while (path.length < 116) {
                        path = '#' + path + '#'
                    }
                    codeblock.innerHTML = codeblock.innerHTML + path

                    var add = document.createElement('p')
                    var addlist =  result['code'][k]['add'].split('\n')
                    for (var i=0; i < addlist.length;i++){
                        add.innerHTML = add.innerHTML + '+   ' + addlist[i]  + '\n'

                    }
                    add.style.color = 'green'
                    codeblock.append(add)

                    var remv = document.createElement('p')
                    var remvlist =  result['code'][k]['remove'].split('\n')
                    for (var i=0; i < remvlist.length;i++){
                        remv.innerHTML = remv.innerHTML + '-   ' + remvlist[i]  + '\n'

                    }
                    remv.style.color = 'red'
                    codeblock.append(remv)

                    var ret = document.createElement('p')
                    ret.innerHTML = result['code'][k]['remain']
                    codeblock.append(ret)


                 }
                 createButton.disabled = false
             }

             else{
                codeblock.innerHTML = result['message']
                createButton.disabled = true
             }
        },
    });

}

function sendBody(body){
    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/esync/'+HOSTGROUP+'/generate/?create=true',
        async:false,
        data: JSON.stringify(body),
        success: function(result) {

                if (result['status'] == true){
                    createButton.disabled=true
                    alert('Configurations applied, sync hostgroup to apply to globally')
                    $("#newFile_MODAL").modal('hide')
                    getfileset()
                }
                else{
                    createButton.disabled=true
                    alert(result['message'])
                }
        },
    });


}

function createConfig(){

    var d_new = document.getElementById('dir_new').value
    var codeblock = document.getElementById('generatedCode')
    codeblock.innerHTML=''

    var createButton = document.getElementById('createButton')
    var nc = document.getElementsByClassName('newBlock')
    var nf = {
            'dir':d_new,
            'conf':[]
        }
    var nd = {}
    if (standard_dirs.includes(d_new)){

        for (var i=0;i<nc.length;i++){
            var d = null
            if (nc[i].type == 'text'){
                var par = nc[i].parentNode

                if (re_match(nc[i].value,nc[i].id) || par.style.display =='none' || nc[i].disabled == true){
                    par.className = par.className.replace('has-error','')
                }

                else{
                    alert('Invalid '+nc[i].id)
                    codeblock.innerHTML = 'INVALID PARAMETERS!'
                    par.className += ' has-error'
                    createButton.disabled=true
                    return
                }
            }
            if (nc[i].type == 'checkbox'){
                d = nc[i].checked
            }
            else{
                d = nc[i].value
            }
            nd[nc[i].id] = d
        }


    }

    else{
        nd[document.getElementById('filename').value] = texteditors.editor_two.getValue()

    }
    nf['conf'].push(nd)
    sendBody(nf)

    var oldlist = FILELIST['FILES'][d_new]
    var newlist=''
    setTimeout(function() {
        newlist = FILELIST['FILES'][d_new]
        var res = newlist.filter( function(n) { return !this.has(n) }, new Set(oldlist) );
        var dummy = document.createElement('p')
        dummy.setAttribute('file',res[0])
        dummy.setAttribute('dir',d_new)
        changeFocus(dummy)
    }, 500);
}

function deleteFile(){
    var dir = document.getElementById('dir').value
    var file = document.getElementById('file').value
    if (dir != '' && file != ''){
        prompt = confirm('Delete File?')

        if(prompt){
            var df = {
                'dir':dir,
                'file':file
            }

            $.ajax({
                type: "POST",
                dataType: "json",
                url:'/esync/'+HOSTGROUP+'/delete/',
                async:false,
                data: JSON.stringify(df),
                success: function(result) {
                    if (result['status'] == true){
                        alert(result['message'])
                        getfileset()
                    }
                    else{
                        alert('Failed to Delete '+df['file'])
                    }

                },
                error: function(err) {
                    alert('Failed to link '+options[i].value)
                }
            });


        }
    }

}

function checkConfig(){
    $("#progress_MODAL").modal()

    var prog = document.getElementById('prog')

    prog.innerHTML=''
    $.ajax({
        type: "GET",
        url: '/esync/'+HOSTGROUP+'/check/',
        cache: false,
        success: function (data) {
            prog.innerHTML=data['message']

        },
        error: function(err) {
            console.log(err)
        },
    });
}




function poll_command(rkey) {

    var prog = document.getElementById('prog')

    var objDiv = document.getElementById("progress_MODAL");

	if (lline != 'ESYNC_WORKER1_COMMAND_END'){
		setTimeout(function() {
	       $.ajax({
		       		url: "https://argus.omtools.me/esync/"+HOSTGROUP+"/?r="+rkey+"&rf="+r+"&rt="+r,
		       		success: function(data) {
		            	lline = data
		       		},

		       		dataType: "text",

		       		complete: function() {

                        console.log(lline)
                        prog.innerHTML = prog.innerHTML+ lline
                        r = r + 1
                        objDiv.scrollTop = objDiv.scrollHeight;
		            	poll_command(rkey);
		       		},
	       		});
	    }, 50);

	}

	else{
	    requestHandler = false
		console.log('DONE')
	}

}


function sync() {
    if (requestHandler == false){
        requestHandler = true
        var prog = document.getElementById('prog')
        prog.innerHTML=''
        prompt = confirm('Execute Sync? (Test, Sync, Clear Cache)')
        if(prompt){

            r=0
            lline=''

            $.ajax({
                type: "GET",
                url: '/esync/'+HOSTGROUP+'/sync/?execute=True',
                cache: false,
                success: function(data){
                    if (data['status'] == true){
                        poll_command(data['key'])
                        console.log(data['key'])
                        $("#progress_MODAL").modal()

                    }
                    else{
                        alert("Sync ERROR")
                    }

                },
                error: function(err) {
                    console.log(err)
                    requestHandler = false
                },

            });
        }
    }
}


function clearCache(){
    if (requestHandler == false){
        requestHandler = true
        var prog = document.getElementById('prog')
        prog.innerHTML=''
        prompt = confirm('Execute Sync? (Test, Sync, Clear Cache)')
        if(prompt){

            r=0
            lline=''

            $.ajax({
                type: "GET",
                url: '/esync/'+HOSTGROUP+'/clear/?execute=True',
                cache: false,
                success: function(data){
                    if (data['status'] == true){
                        poll_command(data['key'])
                        console.log(data['key'])
                        $("#progress_MODAL").modal()

                    }
                    else{
                        alert("Sync ERROR")
                    }

                },
                error: function(err) {
                    console.log(err)
                    requestHandler = false
                },

            });
        }
    }

}

function changeipFocus(){

    //console.log($("#sip option:selected")[0].value)
    //console.log($("#sip option:selected")[0].getAttribute('f'))

    $('#entity').val($("#sip option:selected")[0].value).trigger('change')
    $('#entity_function').val($("#sip option:selected")[0].getAttribute('f')).trigger('change')

}

function showActivity(){
    var r = document.getElementById('activityROW')
    var b = document.getElementById('showActivity')

    var s = document.getElementById('activities')

    s.innerHTML=''
    if (r.style.display == 'none'){
        r.style.display='block'
        b.innerHTML = '<i class="fa fa-times"></i> Hide History Bar'

        $.ajax({
            type: "GET",
            url: '/esync/history',
            cache: false,
            success: function (data) {

                var val=''
                for (var i=0;i<data['data'].length;i++){
                    val = val + '<li><a href="/esync/history?file='+ data['data'][i] +'" target="_blank"><strong >'+data['data'][i]+'</strong>'
                    val = val + '</a></li><hr/>'
                }
                s.innerHTML=val

            },
            error: function(err) {
                console.log(err)
            }
        });

    }
    else {
        r.style.display = 'none'
        b.innerHTML = '<i class="fa fa-check"></i> Show History Bar'

    }



}

function findString(){
    var search = document.getElementById('findstring').value
    var dataString = 'search=' + search ;
    resultPanel = document.getElementById('searchResults')
    resultDiv = document.getElementById('searchDiv')
    resultPanel.innerHTML=''

    $.ajax({
        type: "GET",
        url: '/esync/'+HOSTGROUP+'/',
        data: dataString,
        cache: false,
        success: function (data) {
            if (data['data'].length > 0){
                for(var i = 0; i < data['data'].length; i++) {
                    a=document.createElement('li')
                    b = document.createElement('a')

                    b.setAttribute('onclick','changeFocus(this)')
                    b.setAttribute('file',data['data'][i]['file'])
                    b.setAttribute('dir',data['data'][i]['dir'])
                    b.innerHTML=data['data'][i]['dir']+"/"+data['data'][i]['file']
                    a.appendChild(b)
                    if (data['data'].length == 1){
                        changeFocus(b)
                    }

                    resultPanel.appendChild(a)
                }
                resultDiv.style.display = 'block'
            }

            else {
                alert('String not Found')
                resultDiv.style.display='none'
            }


        },
        error: function(err) {
            console.log(err)
        }
    });
}


function filechecker(){

    var dir = document.getElementById('dir').value
    var filename = document.getElementById('file').value
    if (filename != ''){
        var dataString = 'dir=' + dir +'&file='+filename+'&sha1=true';
        $.ajax({
            type: "GET",
            url: '/esync/'+HOSTGROUP+'/',
            data: dataString,
            success: function(data) {

                if (data['hash'] != currentfilehash){

                    alert('The file has changed, the content will reload')
                    file.trigger('change')
                }
            },
        });
    }
}


setInterval(function() {
    if(FILELIST['W']){
    console.log('asdfadsf')
    filechecker()
    }
    pagecounter = pagecounter + 1
    if (pagecounter == 100){
        alert('No activity detected, the page will reload')
        location.reload()
    }
}, 5000);


function resetCounter(){
    pagecounter=0
}

$("#findstring").on('keyup', function (e) {
    if (e.keyCode == 13) {
        findString()
    }
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));

        }
    }
});


$("#progress_MODAL").on("hide.bs.modal", function () {
    if (requestHandler == true){
        return false
    }
});