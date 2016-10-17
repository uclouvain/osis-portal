$('document').ready(function(){
    var adhoc = $('#hdn_father_profession_adhoc').val();
    display_hide_other_profession('#slt_father_profession',
                                  '#chb_father_profession_other',
                                  '#div_father_profession_other',
                                  '#txt_father_profession_other',
                                  adhoc,
                                  '');

    if($('#hdn_father_profession_adhoc').val() == 'True'){
        display_hide_other_profession('#slt_father_profession',
                                      '#chb_father_profession_other',
                                      '#div_father_profession_other',
                                      '#txt_father_profession_other',
                                      adhoc,
                                      $('#hdn_father_profession_name').val());
    }
    //
    adhoc = $('#hdn_mother_profession_adhoc').val();
    display_hide_other_profession('#slt_mother_profession',
                                  '#chb_mother_profession_other',
                                  '#div_mother_profession_other',
                                  '#txt_mother_profession_other',
                                  adhoc,
                                  '');

    if($('#hdn_mother_profession_adhoc').val() == 'True'){
        display_hide_other_profession('#slt_mother_profession',
                                      '#chb_mother_profession_other',
                                      '#div_mother_profession_other',
                                      '#txt_mother_profession_other',
                                      adhoc,
                                      $('#hdn_mother_profession_name').val());
    }
    //
    adhoc = $('#hdn_student_profession_adhoc').val();
    display_hide_other_profession('#slt_student_profession',
                                  '#chb_student_profession_other',
                                  '#div_student_profession_other',
                                  '#txt_student_profession_other',
                                  adhoc,
                                  '');

    if($('#hdn_student_profession_adhoc').val() == 'True'){
        display_hide_other_profession('#slt_student_profession',
                                      '#chb_student_profession_other',
                                      '#div_student_profession_other',
                                      '#txt_student_profession_other',
                                      adhoc,
                                      $('#hdn_student_profession_name').val());

    }
    //
    adhoc = $('#hdn_conjoint_profession_adhoc').val();
    display_hide_other_profession('#slt_conjoint_profession',
                                  '#chb_conjoint_profession_other',
                                  '#div_conjoint_profession_other',
                                  '#txt_conjoint_profession_other',
                                  adhoc,
                                  '');

    if($('#hdn_conjoint_profession_adhoc').val() == 'True'){
        display_hide_other_profession('#slt_conjoint_profession',
                                      '#chb_conjoint_profession_other',
                                      '#div_conjoint_profession_other',
                                      '#txt_conjoint_profession_other',
                                      adhoc,
                                      $('#hdn_conjoint_profession_name').val());

    }
    //
    adhoc = $('#hdn_paternal_grandfather_profession_adhoc').val();
    display_hide_other_profession('#slt_paternal_grandfather_profession',
                                  '#chb_paternal_grandfather_profession_other',
                                  '#div_paternal_grandfather_profession_other',
                                  '#txt_paternal_grandfather_profession_other',
                                  adhoc,
                                  '');

    if($('#hdn_paternal_grandfather_profession_adhoc').val() == 'True'){
        display_hide_other_profession('#slt_paternal_grandfather_profession',
                                      '#chb_paternal_grandfather_profession_other',
                                      '#div_paternal_grandfather_profession_other',
                                      '#txt_paternal_grandfather_profession_other',
                                      adhoc,
                                      $('#hdn_paternal_grandfather_profession_name').val());

    }
    //
    adhoc = $('#hdn_maternal_grandfather_profession_adhoc').val();
    display_hide_other_profession('#slt_maternal_grandfather_profession',
                                  '#chb_maternal_grandfather_profession_other',
                                  '#div_maternal_grandfather_profession_other',
                                  '#txt_maternal_grandfather_profession_other',
                                  adhoc,
                                  '');

    if($('#hdn_maternal_grandfather_profession_adhoc').val() == 'True'){
        alert('ii');
        display_hide_other_profession('#slt_maternal_grandfather_profession',
                                      '#chb_maternal_grandfather_profession_other',
                                      '#div_maternal_grandfather_profession_other',
                                      '#txt_maternal_grandfather_profession_other',
                                      adhoc,
                                      $('#hdn_maternal_grandfather_profession_name').val());

    }

});

function display_hide_other_profession(slt, chb, div, txt, adhoc, name){
    if(adhoc == 'True'){
        $(slt).prop( "disabled", true);
        $(slt).prop("selectedIndex",-1);
        $(chb).prop('checked', true);
        $(div).css('visibility', 'visible').css('display','block');
    }else{
        $(slt).prop( "disabled", false);
        $(chb).prop('checked', false);
        $(div).css('visibility', 'hidden').css('display','none');
    }
    $(txt).val(name);

}

$("#chb_father_profession_other").change(function() {
    $('#hdn_father_profession_adhoc').val('');
    var adhoc = 'False';
    if ($('#chb_father_profession_other').prop( "checked")){
        adhoc = 'True';
    }
    display_hide_other_profession('#slt_father_profession',
                                  '#chb_father_profession_other',
                                  '#div_father_profession_other',
                                  '#txt_father_profession_other',
                                  adhoc);
});

$("#chb_mother_profession_other").change(function() {
    $('#hdn_mother_profession_adhoc').val('');
    var adhoc = 'False';
    if ($('#chb_mother_profession_other').prop( "checked")){
        adhoc = 'True';
    }
    display_hide_other_profession('#slt_mother_profession',
                                  '#chb_mother_profession_other',
                                  '#div_mother_profession_other',
                                  '#txt_mother_profession_other',
                                  adhoc);
});

$("#chb_student_profession_other").change(function() {
    $('#hdn_student_profession_adhoc').val('');
    var adhoc = 'False';
    if ($('#chb_student_profession_other').prop( "checked")){
        adhoc = 'True';
    }
    display_hide_other_profession('#slt_student_profession',
                                  '#chb_student_profession_other',
                                  '#div_student_profession_other',
                                  '#txt_student_profession_other',
                                  adhoc);
});

$("#chb_conjoint_profession_other").change(function() {
    $('#hdn_conjoint_profession_adhoc').val('');
    var adhoc = 'False';
    if ($('#chb_conjoint_profession_other').prop( "checked")){
        adhoc = 'True';
    }
    display_hide_other_profession('#slt_conjoint_profession',
                                  '#chb_conjoint_profession_other',
                                  '#div_conjoint_profession_other',
                                  '#txt_conjoint_profession_other',
                                  adhoc);
});

$("#chb_maternal_grandfather_profession_other").change(function() {
    $('#hdn_maternal_grandfather_profession_adhoc').val('');
    var adhoc = 'False';
    if ($('#chb_maternal_grandfather_profession_other').prop( "checked")){
        adhoc = 'True';
    }
    display_hide_other_profession('#slt_maternal_grandfather_profession',
                                  '#chb_maternal_grandfather_profession_other',
                                  '#div_maternal_grandfather_profession_other',
                                  '#txt_maternal_grandfather_profession_other',
                                  adhoc);
});

$("#chb_paternal_grandfather_profession_other").change(function() {
    $('#hdn_paternal_grandfather_profession_adhoc').val('');
    var adhoc = 'False';
    if ($('#chb_paternal_grandfather_profession_other').prop( "checked")){
        adhoc = 'True';
    }
    display_hide_other_profession('#slt_paternal_grandfather_profession',
                                  '#chb_paternal_grandfather_profession_other',
                                  '#div_paternal_grandfather_profession_other',
                                  '#txt_paternal_grandfather_profession_other',
                                  adhoc);
});