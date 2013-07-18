$j(document).ready(function(){
    $('a.button-action').click(function(event){
        event.preventDefault();
        event.stopPropagation();
        var url = '/vindula-api/social/combo/action_tabular/';
        url = url.concat(window.token+'/'+$(this).attr('type_object')+'/'+this.id);
        
        $j(window.parent.document).vindula('add_combo_action_tabular', {'id': this.id, 'src': url, 'iframe_class': 'new_combo_action_tabular', 'left': '-17px'});
    });
});