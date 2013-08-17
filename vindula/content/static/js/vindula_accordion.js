$j(document).ready(function(){

    $j('.accordion .title a').click(function(event){
        event.preventDefault();
        event.stopPropagation();
        
        var $accordion = $j(this).parents('.accordion');
        $accordion.toggleClass('active');
    });

});