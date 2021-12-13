setInterval(function(){

        var elements = document.getElementsByClassName("blink");

        for(var i = elements.length - 1; i >= 0; --i)
        {
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


        }, 100);