 $j = jQuery.noConflict();


$j(document).ready(function(){
    $j(".select-filter").multiselect({
        selectedList:10,
        minWidth:200,
        height:150,

    }).multiselectfilter({
        width:180
    },'refresh');


 });