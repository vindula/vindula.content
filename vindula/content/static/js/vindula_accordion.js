$j(document).ready(function(){

    $j('.accordion .title a').click(function(event){
        event.preventDefault();
        event.stopPropagation();
        
        var $accordion = $j(this).parents('.accordion');
        $accordion.toggleClass('active');
    });

    Código comentado pois está dando problema e não foi acahada utilidade para ele!!

    $j('.container-typologies .accordion, .container-services .accordion').click(function(ev){
        $hide_ele = $j('[accordion-id="'+this.id+ '"]');
        $hide_ele.toggle(300);
        
        $this = $j(this);
        
        direction = $this.attr('accordion-direction');
        
        if (!direction){
        	direction = "left-top";
        }
        
        if ($this.prev().hasClass('arrow')){
            moveArrow($this.prev(), direction);
        }else{
            moveArrow($this, direction);
        }

        return false;
    });
    
    $j('[accordion-collapse=true]')
    .each(function(){
        $j(this).hide();
    }); 
});

function moveArrow(ele, direction){
	direction = direction.split('-');
	
	if (direction.length == 2){
		dir1 = direction[0];
		dir2 = direction[1];
	}else{
		dir1 = "left";
		dir2 = "top";
	}
	
    if(ele.hasClass('arrow-'+dir1)) {
        ele.removeClass('arrow-'+dir1);
        ele.addClass('arrow-'+dir2);
    }else if(ele.hasClass('arrow-'+dir2)) {
        ele.removeClass('arrow-'+dir2);
        ele.addClass('arrow-'+dir1);
    }
}
