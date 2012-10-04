$j = jQuery.noConflict();

$j(document).ready(function(){	
	$j('li.trigger-sublinks').click(function(){
		$j.post($j("#url").attr('value') + '/ajax-areas-empresa',
           {categoria:$j(this).children('p').text()},
            function(data) {
			  /*$j('.spinner').addClass('display-none');
                $j('select#area-destino option').css("width", "100%")*/
				$j('div#conteudo-areas').html(data);
				
        });
		$j('#listagem-areas li').removeClass('select');
		$j(this).addClass('select');
		$j('#conteudo-areas').css('min-height', $j('#listagem-areas').height() - 10)
		$j('#conteudo-areas').show();
	});
	
	$j('#conteudo-areas').hide();
});