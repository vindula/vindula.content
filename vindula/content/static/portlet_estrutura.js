$j = jQuery.noConflict();

$j(document).ready(function(){	
	$j('.nivel1 p').each(function(){
		var id_obj = '#nivel2-'+ this.id;
		$j(id_obj).remove();
		
		
	});
	

});