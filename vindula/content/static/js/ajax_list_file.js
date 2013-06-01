function executaAjax(ctx, b_start, b_size, sort_on){
	var url = ctx.find('input#absolute_url').val(),
		theme = ctx.find('input#theme').val(),
        structures = ctx.find('input#structures').val()
        portal_type = ctx.find('input#portal_type').val(),
        fields = ctx.find('input#fields').val(),
        title_box = ctx.find('input#title_box').val(),
		params = {};


	if (b_start==null)
        b_start = parseInt(ctx.find('input#b_start').val())

    if (sort_on==null)
    	sort_on = 'access'
    
    if (b_size==null)
        b_size = parseInt(ctx.find('input#b_size').val())
    
	params['b_size'] = b_size;
	params['b_start'] = b_start;
	params['theme'] = theme;
    params['structures'] = structures;
	params['sort_on'] = sort_on
    params['title_box'] = title_box;
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
    			var content = dom.filter('div#list_file').contents();
    	        ctx.html(content);
    	    },
    	});
}


//TODO: Criar um arquivo javacript para uma navegacao por ajax GENERICA, atualmente eh preciso criar um arquivo js para cada navegacao por ajax (news, biblioteca e servicos)
$j(document).ready(function(){
    $j('.list_file div#cycle-next, .list_file div#cycle-prev').live('click',function(){
    	var $conteiner = $j(this).parents('.list_file'),
    		b_start = parseInt($j(this).find('input').val());
        executaAjax($conteiner,b_start,null,null);
    });
    $j('select.order_by').live('change',function(){
    	var $conteiner = $j(this).parents('.list_file'),
    		sort_on = $j(this).val();

    	executaAjax($conteiner,null,null,sort_on);
    });
    $j('.list_file div#size-nav a').live('click',function(event){
        event.preventDefault();
        event.stopPropagation();
        var $conteiner = $j(this).parents('.list_file'),
            b_size = parseInt($j(this).text());
        executaAjax($conteiner,null,b_size,null);
    });
});