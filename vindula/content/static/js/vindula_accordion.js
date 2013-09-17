$j(document).ready(function(){

    $j('.accordion .title a').click(function(event){
        event.preventDefault();
        event.stopPropagation();
        
        var $accordion = $j(this).parents('.accordion');
        $accordion.toggleClass('active');
    });

    $('.accordion').click(function(ev){
        $hide_ele = $j('[accordion-id="'+this.id+ '"]');
        $hide_ele.toggle(300);
        
        return false;
    })
    
    $j('[accordion-collapse=true]')
      .each(function(){
          $j(this).hide();
      }); 
});