$j(document).ready(function(){

    $j('.accordion .title a').click(function(event){
        event.preventDefault();
        event.stopPropagation();
        
        var $accordion = $j(this).parents('.accordion');
        $accordion.toggleClass('active');
    });

    $j('.accordion').click(function(ev){
        $hide_ele = $j('[accordion-id="'+this.id+ '"]');
        $hide_ele.toggle(300);
        
        if($j(this).hasClass('arrow-left')) {
            $j(this).removeClass('arrow-left');
            $j(this).addClass('arrow-top');
        }else if($j(this).hasClass('arrow-top')) {
            $j(this).removeClass('arrow-top');
            $j(this).addClass('arrow-left');
        }
        
        return false;
    });
    
    $j('[accordion-collapse=true]')
      .each(function(){
          $j(this).hide();
      }); 
});