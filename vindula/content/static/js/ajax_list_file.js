function executaAjax(ctx, b_start, b_size, sort_on){
	var url = ctx.find('input#absolute_url').val(),
        url_base = $j('base').attr('href'),
		theme = ctx.find('input#theme').val(),
        structures = ctx.find('input#structures').val(),
        portal_type = ctx.find('input#portal_type').val(),
        fields = ctx.find('input#fields').val(),
        title_box = ctx.find('input#title_box').val(),
        services = ctx.find('input#services').val(),
        list_files = ctx.find('input#list_files').val(),
        path = ctx.find('input#path').val(),
		params = {},
        ctx_id = "#"+ctx.attr('id');


	if (b_start==null) {
        b_start = parseInt(ctx.find('input#b_start').val());
        if (isNaN(b_start)) {
            b_start = parseInt(ctx.children().find('input#b_start').val());
        }
    }

    if (sort_on==null) {
        sort_on = ctx.find('select.order_by');
        if(sort_on.length) {
            sort_on = sort_on.val();
        } else {
            sort_on = 'access';
        }
    }
        
    if (b_size==null) {
        b_size = parseInt(ctx.find('input#b_size').val());
        if (isNaN(b_size)) {
            b_size = parseInt(ctx.children().find('input#b_size').val());
        }
    }
    
	params['b_size'] = b_size;
	params['b_start'] = b_start;
	params['theme'] = theme;
    params['services'] = services;
    params['structures'] = structures;
	params['sort_on'] = sort_on
    params['title_box'] = title_box;
    params['portal_type'] = portal_type
    params['fields'] = fields
    params['absolute_url'] = url
    params['list_files'] = list_files               
    params['context_path'] = path

	ctx.find('.ajax_loader').show();
	ctx.find('div.see_also_news').addClass('display-none');
    ctx.find('div.content-pagination').css('opacity', '0.2');

    $j.ajax({
        url: url,
        data: params,
        type: 'POST',
        success: function(data){
            var dom = $j(data);
            
            // Feito assim pois tem fez que o dom retorna com o FIND e tem vez que retorna com o FILTER
            var content = dom.find(ctx_id+' .container')
            
            if (content.length >= 2){
                content = content.eq(0);
            }
            
            content = content.contents();
            
            if (content.length) {
                var paginator = dom.find(ctx_id+' .ajax_pagination');
                if (paginator.length >= 2){
                    paginator = paginator.eq(0);
                }
                paginator = paginator.contents();
            } else {
                content = dom.filter(ctx_id).find('.container').contents();
                var paginator = dom.filter(ctx_id).find('.ajax_pagination').contents();
            }
            
            var list_js = ['/table_sorter.js'], //'/++resource++vindula.myvindula.views/js/vindula_modal.js'],
                url_js = '';
            
            if (dom.find('.social-box').length){
                dom.find('.social-box').vindula(null, {user_token: window.token});    
            }
            
            $('a.button-action', dom).click(function(event){
                event.preventDefault();
                event.stopPropagation();
                var url = '/vindula-api/social/combo/action_tabular/';
                url = url.concat(window.token+'/'+$(this).attr('type_object')+'/'+this.id);
                
                $j(window.parent.document).vindula('add_combo_action_tabular', {'id': this.id, 'src': url, 'iframe_class': 'new_combo_action_tabular', 'left': '-17px'});
            });
            
            for(var i=0;i<list_js.length;i++){
                url_js = url_base + list_js[i];
                $j.get(url_js, function(data){
                    $j.globalEval(data);
                });
            }
            
            ctx.find('.container').html(content);
            ctx.find('.ajax_pagination').html(paginator);
            ctx.find('.ajax_loader').hide();
            ctx.find('div.content-pagination').css('opacity', '1');
    	}
    });
}


//TODO: Criar um arquivo javacript para uma navegacao por ajax GENERICA, atualmente eh preciso criar um arquivo js para cada navegacao por ajax (news, biblioteca e servicos)
$j(document).ready(function(){
    $j('.list_file div#cycle-next, .list_file div#cycle-prev').live('click',function(){
    	var $conteiner = $j(this).parents('.list_file'),
    		b_start = parseInt($j(this).find('input').val());
            sort_on = $j("#sortfield").val();

        executaAjax($conteiner,b_start,null,sort_on);
    });
    
    $j('select.order_by').live("change", function(ev){
        var $conteiner = $j(this).parents('.list_file'),
            sort_on = $j("#sortfield").val();
            
        executaAjax($conteiner,null,null,sort_on);
    });

    $j('.list_file div#size-nav a').live('click',function(event){
        event.preventDefault();
        event.stopPropagation();
        var $conteiner = $j(this).parents('.list_file'),
            b_size = parseInt($j(this).text()),
            sort_on = $j(this).val();
        executaAjax($conteiner,null,b_size,sort_on);
    });
});