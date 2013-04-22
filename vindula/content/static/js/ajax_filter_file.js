function isEmpty(str) {
    return (!str || 0 === str.length);
};

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

    $ctx.find('.filter[name="structures"]').each(function(){
        if($j(this).is(':checked')){
          structures.push(this.value);
        };

   });

    params['subject'] = $ctx.find('input.filter[name="subject"]').val()

    params['keywords'] = $ctx.find('.filter[name="keywords"]').val()

	params['themes'] = themes;

    if (isEmpty(structures))
        structures = $ctx.find('.filter[name="structures"]').val()

    params['structures'] = structures;

	$ctx.find('.filterFile #spinner').removeClass('display-none');
	$ctx.find('div#list_file').addClass('display-none');

    $j.ajax({
    	  url: url,
    	  data: params,
    	  dataType: 'GET',
    	  success: function(data){
    			var dom = $j(data),
                    ctx_id = $ctx.attr('id'),
        	   	    content = dom.find('div#'+ctx_id+' div#itens'),
                    url = $j('base').val() + 'table_sorter.js';

                    $j.get(url, function(data){
                        $j.globalEval(data);
                    });

                $ctx.find('div#itens').html(content);

                $ctx.find('.filterFile #spinner').addClass('display-none');
                $ctx.find('div#list_file').removeClass('display-none');
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

        $j('.ui-multiselect-none').each(function(){
            $j(this).trigger('click');
        });

    });

});