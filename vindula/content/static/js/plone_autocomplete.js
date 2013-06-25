$j(document).ready(function() {
    var url = $j('base').attr('href')+'/autocomplete-view'
    
    createInputToken(url,$j(".document-type"),'Digite o tipo');
    createInputToken(url,$j(".structure-owner"),'Digite a letra inicial');
    createInputToken(url,$j(".structure-client"),'Digite a letra inicial');
    createInputToken(url,$j(".document-format"),'Digite o tipo');
});

function createInputToken(url, $element)
{
    $element.tokenInput(url+'?action='+$element.attr('class'),
                        {queryParam: 'term', theme: "facebook", i18n:'pt_BR'});
}
