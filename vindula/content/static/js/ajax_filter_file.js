function isEmpty(str) {
    return (!str || 0 === str.length);
};

$j(document).ready(function(){
    var url = document.URL
    
    $j('.execFilter').live('click',function(event){
        var $data_box = $j(this).parents('.filterFile').nextAll('div'),
            $container = $data_box.find('.container'),
            $filter = $j(this).parents('.container-button-group').prev('.content-filter'),
            url_base = $j('base').attr('href'),
            url_filter = url_base  + '/searchfilter-view',
            url_display = $data_box.find('#absolute_url').val(),
            searchableText = $filter.prev('.title-filter').find('input[name="SearchableTextFilter"]').val(),
            fields = $data_box.find('input[name="fields"]').val(),
            form = $filter.find('form'),
            params = {};
            
        event.preventDefault();
        event.stopPropagation();
            
        // FONTE: http://be.twixt.us/jquery/formSubmission.php
        $j(form)
        .find("input:checked, input[type='text'], input[type='hidden'], input[type='password'], option:selected, textarea")
        .each(function() {
            var name = this.name || this.parentNode.name || this.id || this.parentNode.id;
            if ((this.type == 'checkbox' || this.type == 'text' || name.split(':').length == 2) && params[this.name]) {
                if (params[name] instanceof Array){
                    params[name].push(this.value);
                }
                else{
                    var old_value =  params[name];
                    
                    params[name] = new Array();
                    params[name].push(old_value);
                    params[name].push(this.value);
                }
            }
            else{
                if(this.value.indexOf(',') != -1 && this.value[0] != '('){
                    params[name] = this.value.split(',');
                }else{
                    params[name] = this.value;
                }
            }
        });
        
        if (searchableText)
            params['SearchableText'] = searchableText;
        
        $j.ajax({
            url: url_filter,
            data: params,
            type: 'POST',
            success: function(data){
                var params_container = {};
                params_container['list_files'] = data;
                params_container['fields'] = fields;
                params_container['type'] = $data_box.find('#type').val();
                params_container['document-theme'] = params['document-theme'];
                params_container['portal_type'] = params['portal-type'];
                
                $j.post(
                    url_display,
                    params_container,
                    function(data){
                        var $dom = $j(data);
                        var $contents = $dom.find('.container');
                        if (!$dom.find('.container').length)
                            $contents = $dom.filter('.container');
                        
                        var list_js = ['/table_sorter.js'] //, '/++resource++vindula.myvindula.views/js/vindula_modal.js'],
                            url_js = '';
                            
                        for(var i=0;i<list_js.length;i++){
                            url_js = url_base + list_js[i];
                            $j.get(url_js, function(data){
                                $j.globalEval(data);
                            });
                        }
                        
                        $container.html($contents.contents());
                        
                        if ($container.hasClass('hide')){
                            $container.removeClass('hide');
                        }
                    }
                );
            },
        });

    });
    
    $j('.title-filter a').click(function(){
        $j(this).parents('.section-biblioteca-accordion').toggleClass('active')
        
        var $icon = $j(this).find('i');
        
        if($icon.hasClass('vindula-icon-plus-sign')){
            $icon.removeClass('vindula-icon-plus-sign')
            $icon.addClass('vindula-icon-minus');
        }
        else{
            $icon.removeClass('vindula-icon-minus')
            $icon.addClass('vindula-icon-plus-sign');
        }
        
        return false; 
    });

    $j('.clearFilter').live('click',function(){
        //Limpando todos campos do form
        $j(':input','.form-columns-tag')
          .not(':button, :submit, :reset, :hidden')
          .val('')
          .removeAttr('checked')
          .removeAttr('selected');
          
        $j('input[name="SearchableTextFilter"]')
          .val('');
          
    });
    
     $j('.datepicker').datepicker({
        showOn: "button",
        buttonImage: url+"/++resource++vindula.content/images/icon-datepicker.png",
        buttonImageOnly: true
     });

});