$j = jQuery.noConflict();

function AjaxNewsItens (b_size,b_start) {
       
    var url = $j('#portal_url').val() + "/vindula_news_result_view";
    var parametro = {};
    
    parametro['size_image_height'] = $j("#size_image_height").val();
    parametro['size_image_width'] = $j("#size_image_width").val();
    parametro['com_image'] = $j("#com_image").val();
         
    parametro['sorted'] = $j("#sortfield").val();
    parametro['keyword'] = $j("#keyword").val();
    
    if ($j('#reversed').attr('checked'))
        parametro['invert:boolean'] = 'True';

    if (b_size==null)
        var b_size = $j('#b_size').val();
    
    if (b_start==null)
        var b_start = $j('#b_start').val();
    
    parametro['b_size'] = b_size;
    parametro['b_start'] = b_start;
    parametro['submitted:boolean'] = true
    
    $j('#spinner').removeClass('display-none');
    $j('#content-itens').addClass('display-none');
    
    $j.get(url,parametro, function(data){
        $j('#content-itens').html(data);
        $j('#content-itens').removeClass('display-none');
        $j('#spinner').addClass('display-none');
    });
}
$j(document).ready(function(){
    $j('input#searchItems').click(function(){
        AjaxNewsItens();
    });
    
    $j('a#itenspage').live('click',function(){
       var quant = parseInt($j(this).text());
       AjaxNewsItens(quant,0);
    });    
    
    $j('select#page_selector').live('change', function(){
        var page = parseInt($j(this).val().split('=')[1]);
        AjaxNewsItens(null,page);
    });
    
    $j('div#cycle-next').live('click',function(){
        var page = parseInt($j(this).find('input').val());
        AjaxNewsItens(null,page);
    });
    
    $j('div#cycle-prev').live('click',function(){
        var page = parseInt($j(this).find('input').val());
        AjaxNewsItens(null,page);
    });
});