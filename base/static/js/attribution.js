$('document').ready(function(){
    var recompute_submit_renew_btn_and_select_all_state = function(){
       // Submit button
       var submit_renew_btn = $("#bt_submit_attribution_renew");
       var checkboxes_checked = $('input:checkbox[id^="chb_attribution_renew_"]:checked');
       submit_renew_btn.prop('disabled', checkboxes_checked.length == 0);

       // Select all checkbox
       var select_all_chb =  $("#chb_renew_all");
       var checkboxes_enabled = $('input:checkbox[id^="chb_attribution_renew_"]:enabled');
       if (checkboxes_checked.length == checkboxes_enabled.length && checkboxes_enabled.length > 0){
            select_all_chb.prop('checked', true);
       }else {
            select_all_chb.prop('checked', false);
       }
    };

    var select_all_chb =  $("#chb_renew_all");
    var checkboxes_enabled = $('input:checkbox[id^="chb_attribution_renew_"]:enabled');
    if (checkboxes_enabled.length > 0) {
        select_all_chb.attr('disabled', false);
        select_all_chb.click(function() {
            is_checked = $(this).prop('checked');
            checkboxes_enabled.prop('checked', is_checked);
            recompute_submit_renew_btn_and_select_all_state();
        });
        checkboxes_enabled.each(function(){
            $(this).click(recompute_submit_renew_btn_and_select_all_state);
        });
    }
    recompute_submit_renew_btn_and_select_all_state();

    //Show confirm popup before delete application
    $("button[id^='lnk_application_delete_']").click(function() {
        return confirm(gettext('Are you sure you want to delete the application?'));
    });
});

function changeOrientation(button) {
    if (button.className.includes("glyphicon-collapse-down")) {
        button.className = button.className.replace("glyphicon-collapse-down", "glyphicon-expand");
    }
    else if (button.className.includes("glyphicon-expand")) {
        button.className = button.className.replace("glyphicon-expand", "glyphicon-collapse-down");
    }
}