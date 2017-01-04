$("input[id^='chb_attribution_renew_'").click(function() {
    bt_submit_attribution_renew_activation();
});

$('document').ready(function(){
    $('#bt_submit_attribution_renew').css('visibility', 'hidden').css('display','none');
    $('#spn_renew_title').css('visibility', 'hidden').css('display','none');
    $('input:checkbox[id^="chb_attribution_renew_"]').each(function(){
        $('#bt_submit_attribution_renew').css('visibility', 'visible').css('display','block');
        $('#spn_renew_title').css('visibility', 'visible').css('display','block');
    });

});

$("#chb_renew_all").click(function() {
    $('input:checkbox[id^="chb_attribution_renew_"]').each(function(){
        $(this).prop('checked',$('#chb_renew_all').prop('checked'));

    });
    bt_submit_attribution_renew_activation();
});

function bt_submit_attribution_renew_activation() {
    $('#bt_submit_attribution_renew').prop("disabled", true);

    $('input:checkbox[id^="chb_attribution_renew_"]:checked').each(function(){
        $('#bt_submit_attribution_renew').prop("disabled", false);
    });
}