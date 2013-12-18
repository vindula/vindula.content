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
        
        $this = $j(this);
        
        if ($this.prev().hasClass('arrow')){
            moveArrow($this.prev());
        }else{
            moveArrow($this);
        }

        return false;
    });
    
    $j('[accordion-collapse=true]')
    .each(function(){
        $j(this).hide();
    }); 
});

function moveArrow(ele){
    if(ele.hasClass('arrow-left')) {
        ele.removeClass('arrow-left');
        ele.addClass('arrow-top');
    }else if(ele.hasClass('arrow-top')) {
        ele.removeClass('arrow-top');
        ele.addClass('arrow-left');
    }
}
