function executaAjax(b_size, b_start){
	var url = $j('input#absolute_url').val();
	var params = {}
	
	if (b_size==null)
        var b_size = $j('#b_size').val();
        
    if (b_start==null)
        var b_start = $j('#b_start').val();
			
	params['b_size'] = b_size;
	params['b_start'] = b_start;
	
	$j('#spinner').removeClass('display-none');
    $j('div.see_also_news').addClass('display-none');
	
	$j.get(url,params, function(data){
		var dom = $j(data);
		var content = dom.find('div.see_also')
		
        $j('.see_also').html(content);
    });
}

$j(document).ready(function(){
    $j('div#cycle-next, div#cycle-prev').live('click',function(){
        var b_start = parseInt($j(this).find('input').val());
        executaAjax(null,b_start);
    });
});