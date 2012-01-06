$j = jQuery.noConflict();
$j(document).ready(function(){
	
	$j("textarea[name='form.widgets.text']").addClass('ckeditor_plone');
        
	/*var variaveis = location.href
	var url = variaveis.search.split("/");
	//var quebra = variaveis[1].split("=");
	alert(variaveis[1])
	*/
	var html = ''
	html += '<input class="cke_config_url" type="hidden" value="/ckeditor_plone_config.js" name="cke_config_url">'	
	html += '<input class="cke_iswidget" type="hidden" value="True" name="cke_iswidget">' 	
		
	$j("textarea[name='form.widgets.text']").parent().append(html);

	
	

});

