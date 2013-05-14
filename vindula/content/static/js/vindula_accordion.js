$j(document).ready(function(){

    $j('.accordion .title').click(function(event){
        event.preventDefault();
        event.stopPropagation();
        
        var $accordion = $j(this).parent();
        $accordion.toggleClass('active');
    });

});