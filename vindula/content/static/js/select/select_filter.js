 $j = jQuery.noConflict();


$j(document).ready(function(){
    $j(".select-filter").multiselect({
        selectedList:10,
        minWidth:150,
        height:100,

        // checkAll: function(){
        //     ajaxBusca();
        // },
        // uncheckAll: function(){
        //     ajaxBusca();
        // }
    }).multiselectfilter({
        width:120
    },'refresh');


 });