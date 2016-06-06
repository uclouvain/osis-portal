$('document').ready(function(){
    // for secondary_education and diplomas screen
    if ($('#form_accounting')){
        $('#pnl_study_grant_detail').css('visibility', 'hidden').css('display','none');
        $('#pnl_scholarship_organization').css('visibility', 'hidden').css('display','none');
        
        if ($("input[name='study_grant']:checked").val()){
            $('#pnl_study_grant_detail').css('visibility', 'visible').css('display','block');
        }
        if ($("input[name='rdb_no_UCL_scholarship_true']:checked").val()){
            $('#pnl_scholarship_organization').css('visibility', 'visible').css('display','block');
        }

    }
});

