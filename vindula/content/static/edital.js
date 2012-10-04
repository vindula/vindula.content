$j = jQuery.noConflict();

//pega o form do elemento input
function getSuperForm(el){
	var form = el.parentElement;
	if (form.tagName != 'FORM')
	{
		form = getSuperForm(form);
	}
	
	return form;
}

function setParams(el){
	var button_clicked = el;
	var form = getSuperForm(el);
	var url = form.action;
	var select_list = $j(form).find('select');
	var params = {}
	
	$j(form)
	.find('input:checked, option:selected, input[type="text"], input[type="hidden"], input[type="password"]')
	.each(function(){
		var name = this.name || this.parentNode.name || this.id || this.parentNode.id;
		params[name] = this.value;
	});
	
	if (el.id == "cycle-next")
		b_start = params['next']
	else if (el.id == "cycle-prev")
		b_start = params['prev']
	else if (el.id == "page_selector")
		b_start = params['page_selector'].split('=')[1]
	else if (el.id == 'itenspage')
		b_size = parseInt(el.text);
	
	if (b_size==null)
        var b_size = $j('#b_size').val();
    
    if (b_start==null)
        var b_start = $j('#b_start').val();
    
    params['b_size'] = b_size;
    params['b_start'] = b_start;
	
	params[button_clicked.name] = button_clicked.value;
	
	$j('#spinner').removeClass('display-none');
	$j('#content-itens').addClass('display-none');
	
	$j.post(
		url,
		params,
		function(data){
			var dom = $j(data);
			var content = dom.find('#content-itens');
	        $j('#content-itens').html(content);
	        $j('#content-itens').removeClass('display-none');
	        $j('#spinner').addClass('display-none');
		}
	);
}

$j(document).ready(function(){
	
	$j('form').submit(function(){
		return false;
	})

	$j('input[name="submitted"], div#cycle-next, div#cycle-prev, a#itenspage').live('click', function(){
		setParams(this);
		return false;
	});
	
	$j('select#page_selector').change(function(){
		setParams(this);
		return false;
	});
});