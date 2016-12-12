$("input[id^='chb_attribution_renew_'").click(function() {
    $('#bt_submit_attribution_renew').prop("disabled", true);

    $('input:checkbox[id^="chb_attribution_renew_"]:checked').each(function(){
        $('#bt_submit_attribution_renew').prop("disabled", false);
    });
});

$('document').ready(function(){
    $('#bt_submit_attribution_renew').css('visibility', 'hidden').css('display','none');
    $('#spn_renew_title').css('visibility', 'hidden').css('display','none');
    $('input:checkbox[id^="chb_attribution_renew_"]').each(function(){
        $('#bt_submit_attribution_renew').css('visibility', 'visible').css('display','block');
        $('#spn_renew_title').css('visibility', 'visible').css('display','block');
    });

});
