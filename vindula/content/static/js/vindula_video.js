$j(document).ready(function(){
    $f("*").each(function(){
        this.getClip(0).update({
            autoBuffering: true, 
            start: 5
        })
    })
})