function executaAjaxFilter($ctx){
	var url = document.URL, //$j('base').val() + 'biblioteca-view',
        id = $ctx.attr('id'),
        themes = [],
        structures = [],
		params = {};

   $ctx.find('input.filter[name="theme"]').each(function(){
        if($j(this).is(':checked')){
          themes.push(this.value);
        };

   });

    $ctx.find('input.filter[name="structures"]').each(function(){
        if($j(this).is(':checked')){
          structures.push(this.value);
        };

   });

    params['subject'] = $ctx.find('input.filter[name="subject"]').val()


	params['themes'] = themes;
    params['structures'] = structures;

	$ctx.find('.filterFile #spinner').removeClass('display-none');
	$ctx.find('div#list_file').addClass('display-none');

    $j.ajax({
    	  url: url,
    	  data: params,
    	  dataType: 'GET',
    	  success: function(data){
    			var dom = $j(data);
    			var content = dom.find('div#'+id);

    	        $ctx.html(content);
    	    },
    	});
}




$j(document).ready(function(){

    $j('.execFilter').live('click',function(){
        var $conteiner = $j(this).parents('.conteiner');
        executaAjaxFilter($conteiner);

    });


    $j('.clearFilter').live('click',function(){
        $j('input.filter[type="checkbox"]').each(function(){
            $j(this).attr('checked', false);
        });

        $j('input.filter[type="text"]').each(function(){
            $j(this).attr('value', '');
        });

    });

});