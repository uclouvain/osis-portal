$("#slt_schools").change(function(event) {
    $('#slt_schools_community').prop("selectedIndex",$('#slt_schools').prop("selectedIndex"));
    if($('#slt_schools_community').val()=='FRENCH'){
        $('#pnl_teaching_type').css('visibility', 'visible').css('display','block');
    }else{
        $('#pnl_teaching_type').css('visibility', 'hidden').css('display','none');
    }

});