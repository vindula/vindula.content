$j = jQuery.noConflict();

function AjaxNewsItens (b_size,b_start,limpa_cookie, sort) {
       
    var url = $j('#portal_url').val() + "/vindula_news_result_view";
    var parametro = {};
    
    if ((!$j.cookie("find-news",{ path: window.location.pathname })) || (limpa_cookie)){

        var cookie_parametro = ''
        
        parametro['size_image_height'] = $j("#size_image_height").val();
        cookie_parametro += "size_image_height="+parametro['size_image_height']+"|";
        
        parametro['size_image_width'] = $j("#size_image_width").val();
        cookie_parametro += 'size_image_width='+parametro['size_image_width']+'|';
        
        parametro['com_image'] = $j("#com_image").val();
        cookie_parametro += 'com_image='+parametro['com_image']+'|';
             
        parametro['sorted'] = $j("#sortfield").val();
        cookie_parametro += 'sorted='+parametro['sorted']+'|';
        
        parametro['keyword'] = $j("#keyword").val();
        cookie_parametro += 'keyword='+parametro['keyword']+'|';
		
		if (sort) {
			parametro['invert:boolean'] = sort;
            cookie_parametro += 'invert:boolean='+parametro['invert:boolean']+'|';
		}

        if (b_size==null)
            var b_size = $j('#b_size').val();
        
        if (b_start==null)
            var b_start = $j('#b_start').val();
        
        parametro['b_size'] = b_size;
        cookie_parametro += 'b_size='+parametro['b_size']+'|';
        
        parametro['b_start'] = b_start;
        cookie_parametro += 'b_start='+parametro['b_start']+'|';
        
        parametro['submitted:boolean'] = true
        cookie_parametro += 'submitted:boolean='+parametro['submitted:boolean']+'|';
        
        
        $j.cookie("find-news", cookie_parametro, { path: window.location.pathname });
    
    }else{
        var cookie_parametro = $j.cookie("find-news",{expires: 7, path: window.location.pathname });
        
        var list_parametros = cookie_parametro.split('|');
        for (i=0; i<list_parametros.length; i++){
            var dados = list_parametros[i].split('='); 
            parametro[dados[0]] = dados[1];
        }
        $j("#sortfield").val(parametro['sorted']);
        $j("#keyword").val(parametro['keyword'])
        
        if (parametro['invert:boolean']){
            $j('#reversed').attr('checked','checked')
        }
        
    };
    
    $j('#spinner').removeClass('display-none');
    $j('#content-itens').addClass('display-none');
    

    $j.get(url,parametro, function(data){
        $j('#content-itens').html(data);
        $j('#content-itens').removeClass('display-none');
        $j('#spinner').addClass('display-none');
		if ($j("#keyword").val())
			$j('#content-itens').highlight($j("#keyword").val());
    });
}

function clearCookies () {
	$j.cookie("find-news", '', { path: window.location.pathname });
}

$j(document).ready(function(){
	
	$j('.imgSort').click(function(){
		if ($j(this).hasClass('imgDescend'))
			var sort = '';
		else
			var sort = 'True';	
			
		AjaxNewsItens(null,null,true, sort);
		$j(this).toggleClass('imgDescend');
		$j(this).toggleClass('imgAscend');
	});
	
	$j('#vindula_folder_summary_imgBig_view, #vindula_folder_summary_imgSmall_view, #vindula_folder_summary_noImg_view').click(function(){
	  clearCookies();
	});
/*

	AjaxNewsItens();
	
*/
    $j('input#searchItems').click(function(){
		if ($j('.imgSort').hasClass('imgDescend'))
			var sort = 'True';
		else
			var sort = '';	
        AjaxNewsItens(null,null,true, sort);
    });
    
    $j('a#itenspage').live('click',function(){
       var quant = parseInt($j(this).text());
       AjaxNewsItens(quant,0,true);
       
       return false;
    });    
    
    $j('select#page_selector').live('change', function(){
        var page = parseInt($j(this).val().split('=')[1]);
        AjaxNewsItens(null,page,true);
    });
    
    $j('div#cycle-next').live('click',function(){
        var page = parseInt($j(this).find('input').val());
        AjaxNewsItens(null,page,true);
    });
    
    $j('div#cycle-prev').live('click',function(){
        var page = parseInt($j(this).find('input').val());
        AjaxNewsItens(null,page,true);
    });
	
});