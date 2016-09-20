$("#slt_schools").change(function(event) {
    $('#slt_schools_community').prop("selectedIndex",$('#slt_schools').prop("selectedIndex"));
    if($('#slt_schools_community').val()=='FRENCH'){
        $('#pnl_teaching_type').css('visibility', 'visible').css('display','block');
    }else{
        $('#pnl_teaching_type').css('visibility', 'hidden').css('display','none');
    }
    if($(this).prop('selectedIndex') >= 0 ){
        $('#national_diploma_school_error').html('');
    }
});

$("#rdb_result_less_65").click(function(event) {
    $('#national_diploma_result_error').html('');
});

$("#rdb_result_between_65_75").click(function(event) {
    $('#national_diploma_result_error').html('');
});

$("#rdb_result_more_75").click(function(event) {
    $('#national_diploma_result_error').html('');
});

$("#path_repetition").click(function(event) {
    $('#national_diploma_path_repetition_error').html('');
});

$("#path_reorientation").click(function(event) {
    $('#national_diploma_path_reorientation_error').html('');
});

$("#rdb_dipl_acc_high_educ_true").click(function(event) {
    $('#national_diploma_dipl_acc_high_educ_error').html('');
});

$("#rdb_dipl_acc_high_educ_false").click(function(event) {
    $('#national_diploma_dipl_acc_high_educ_error').html('');
});

$("#rdb_belgian_community_french").click(function(event) {
    $('#national_diploma_belgian_community_error').html('');
});

$("#rdb_belgian_community_dutch").click(function(event) {
    $('#national_diploma_belgian_community_error').html('');
});

$("#rdb_belgian_community_german").click(function(event) {
    $('#national_diploma_belgian_community_error').html('');
});

$( "input[name^='rdb_education_transition_type']" ).click(function() {
    $('#national_diploma_pnl_teaching_type_error').html('');
});

$("input[name^='rdb_education_technic_type']" ).click(function() {
    $('#national_diploma_pnl_teaching_type_error').html('');
});

$("button[id^='bt_load_doc_NATIONAL_DIPLOMA_']" ).click(function() {
    $('#national_diploma_national_diploma_doc_error').html('');
});


