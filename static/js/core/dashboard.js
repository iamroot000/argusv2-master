color_production='#1ab394'
color_marketing='#2d4ef7'
color_other='#cc1212'
color_default='#7a7a7a'

curr_BU=''
curr_APP = ''
content = document.getElementById('argus-d-content')

$( document ).ready(function() {
    document.getElementsByClassName('d_BU')[0].click()

});

$(window).resize(function(){
    if (curr_APP=='EYE'){
        drawChartEYE(curr_BU);

    }
    else if (curr_APP=='VERGIL'){
        drawChartVERGIL(curr_BU);
    }


});

function changeBU(elem){
    curr_BU = elem.value
    elem.className = elem.className.replace('white','primary')
    var sel = document.getElementsByClassName('d_BU')

    for (var i = 0;i < sel.length; i++){
        if (sel[i].value != curr_BU){
            sel[i].className = sel[i].className.replace('primary','white')
        }
    }
    content.innerHTML=''
    document.getElementsByClassName('tab_q')[0].click()
}


function changeToEYE(elem){
    elem.className = elem.className.replace('white','primary')

    var sel = document.getElementsByClassName('tab_q')

    for (var i = 0;i < sel.length; i++){
        if (sel[i].value != 'EYE'){
            sel[i].className = sel[i].className.replace('primary','white')
        }
    }
    console.log('EYE'+curr_BU)
    content.innerHTML=''
    curr_APP='EYE'
    generateChartsEYE(curr_BU)
}

function changeToVERGIL(elem){
    elem.className = elem.className.replace('white','primary')

    var sel = document.getElementsByClassName('tab_q')

    for (var i = 0;i < sel.length; i++){
        if (sel[i].value != 'VERGIL'){
            sel[i].className = sel[i].className.replace('primary','white')
        }
    }
    console.log('VERGIL'+curr_BU)
    content.innerHTML=''
    curr_APP='VERGIL'

    generateChartsVERGIL(curr_BU)

}