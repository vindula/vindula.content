
function executaAjax(ctx, b_start, sort_on){
	var url = ctx.find('input#absolute_url').val(),
		b_size = parseInt(ctx.find('input#b_size').val()),
		theme = ctx.find('input#theme').val(),
        structures = ctx.find('input#structures').val()
        portal_type = ctx.find('input#portal_type').val(),
        fields = ctx.find('input#fields').val(),
		params = {};


	if (b_start==null)
        b_start = parseInt(ctx.find('input#b_start').val())

    if (sort_on==null)
    	sort_on = 'access'

	params['b_size'] = b_size;
	params['b_start'] = b_start;
	params['theme'] = theme;
    params['structures'] = structures;
	params['sort_on'] = sort_on
    params['portal_type'] = portal_type
    params['fields'] = fields

	ctx.find('#spinner').removeClass('display-none');
	ctx.find('div.see_also_news').addClass('display-none');

    $j.ajax({
    	  url: url,
    	  data: params,
    	  dataType: 'GET',
    	  success: function(data){
    			var dom = $j(data);
                dom.filter('script').each(function(){
                    var content_script = this.text || this.textContent || this.innerHTML || ''
                    if (content_script)
                        $j.eval(content_script);
                    else
                        $j.get(this.src, function(data){
                            $j.eval(data);
                        })
                });
    			var content = dom.filter('div#list_file');
    	        ctx.html(content);


    	    },
    	});
}


//TODO: Criar um arquivo javacript para uma navegacao por ajax GENERICA, atualmente eh preciso criar um arquivo js para cada navegacao por ajax (news, biblioteca e servicos)
$j(document).ready(function(){
    $j('div#cycle-next, div#cycle-prev').live('click',function(){
    	var $conteiner = $j(this).parents('.list_file'),
    		b_start = parseInt($j(this).find('input').val());
        executaAjax($conteiner,b_start,null);
    });
    $j('select.order_by').live('change',function(){
    	var $conteiner = $j(this).parents('.list_file'),
    		sort_on = $j(this).val();

    	executaAjax($conteiner,null,sort_on);

    });
});