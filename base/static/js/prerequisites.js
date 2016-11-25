

$('document').ready(function(){
    // for secondary_education and diplomas screen
    if ($('#form_secondary_education')){
        $('#pnl_secondary_education_main').css('visibility', 'hidden').css('display','none');
        $('#pnl_academic_year').css('visibility', 'hidden').css('display','none');

        $('#rdb_diploma_true').prop( "checked", false);
        $('#rdb_diploma_false').prop( "checked", false);

        $('#rdb_local').prop( "checked", false);
        $('#rdb_foreign').prop( "checked", false);

        $('#pnl_local_detail').css('visibility', 'hidden').css('display','none');
        reset_rdb_local_community(false);


        $('#pnl_dipl_acc_high_educ').css('visibility', 'hidden').css('display','none');

        $('#slt_cities').prop("selectedIndex",-1);
        $('#slt_postal_codes').prop("selectedIndex",-1);
        $('#slt_schools').prop("selectedIndex",-1);

        $('#slt_cities').prop( "disabled", false);
        $('#slt_postal_codes').prop( "disabled", false);
        $('#slt_schools').prop( "disabled", false);

        $('#pnl_other_school').css('visibility', 'hidden').css('display','none');
        $('#chb_other_school').prop( "checked", false);
        $('#txt_CESS_other_school_name').val('');
        $('#txt_CESS_other_school_name').prop( "disabled", true);
        $('#txt_CESS_other_school_city').val('');
        $('#txt_CESS_other_school_city').prop( "disabled", true);
        $('#txt_CESS_other_school_postal_code').val('');
        $('#txt_CESS_other_school_postal_code').prop( "disabled", true);

        $('#pnl_teaching_type').css('visibility', 'hidden').css('display','none');
        $('[id^="rdb_general_transition_"]').prop( "checked", false);
        $('[id^="rdb_technic_"]').prop( "checked", false);

        $('#chb_other_education').prop( "checked", false);
        $('#txt_other_education_type').val('');
        $('#txt_other_education_type').prop( "disabled", true);

        $('#rdb_dipl_acc_high_educ_true').prop( "checked", false);
        $('#rdb_dipl_acc_high_educ_false').prop( "checked", false);

        $('#rdb_repeated_grade_true').prop( "checked", false);
        $('#rdb_repeated_grade_false').prop( "checked", false);
        $('#rdb_re_orientation_true').prop( "checked", false);
        $('#rdb_re_orientation_false').prop( "checked", false);

        $('#rdb_result_less_65').prop( "checked", false);
        $('#rdb_result_between_65_75').prop( "checked", false);
        $('#rdb_result_more_75').prop( "checked", false);
        $('#rdb_no_result').prop( "checked", false);
        //for foreign diploma
        $('#pnl_foreign_detail').css('visibility', 'hidden').css('display','none');
        $('#rdb_foreign_baccalaureate_diploma_national').prop( "checked", false);
        $('#rdb_foreign_baccalaureate_diploma_european').prop( "checked", false);
        $('#rdb_foreign_baccalaureate_diploma_international').prop( "checked", false);
        $('#slt_country').prop("selectedIndex",-1);
        $('#slt_language_diploma').prop("selectedIndex",-1);
        $('#chb_other_language_regime').prop( "checked", false);
        $('#slt_other_language_diploma').prop("selectedIndex",-1);
        $('#slt_other_language_diploma').prop( "disabled", true);
        $('#rdb_international_equivalence_yes').prop( "checked", false);
        $('#rdb_international_equivalence_no').prop( "checked", false);
        $('#rdb_international_equivalence_in_progress').prop( "checked", false);
        $('#rdb_foreign_result_low').prop( "checked", false);
        $('#rdb_foreign_result_middle').prop( "checked", false);
        $('#rdb_foreign_result_high').prop( "checked", false);
        $('#rdb_foreign_no_result').prop( "checked", false);
        $('#pnl_translation').css('visibility', 'hidden').css('display','none');
        //profressional
        $('#rdb_professional_experience_true').prop( "checked", false);
        $('#rdb_professional_experience_false').prop( "checked", false);

        $('#txt_professional_exam_date').val('');
        $('#txt_professional_exam_institution').val('');
        $('#rdb_professional_exam_result_result_low').prop( "checked", false);
        $('#rdb_professional_exam_result_result_middle').prop( "checked", false);
        $('#rdb_professional_exam_result_result_high').prop( "checked", false);
        //local language exam
        $('#pnl_local_exam').css('visibility', 'hidden').css('display','none');

        $('#rdb_local_language_exam_true').prop( "checked", false);
        $('#rdb_local_language_exam_false').prop( "checked", false);

        $('#txt_local_language_exam_date').val('');
        $('#txt_local_language_exam_institution').val('');
        $('#rdb_local_exam_session_succeed').prop( "checked", false);
        $('#rdb_local_exam_session_failed').prop( "checked", false);
        $('#rdb_local_exam_enrollment_enrollment_in_progress').prop( "checked", false);
        //
        $('#pnl_admission_exam').css('visibility', 'hidden').css('display','none');

        $('#rdb_admission_exam_true').prop( "checked", false);
        $('#rdb_admission_exam_false').prop( "checked", false);

        $('#txt_admission_exam_date').val('');
        $('#txt_admission_exam_institution').val('');
        $('[id^="rdb_admission_exam_type_"]').prop( "checked", false);
        $('#txt_admission_exam_type_other').val('');
        $('#txt_admission_exam_type_other').prop( "disabled", true);
        $('#chb_admission_exam_type').prop( "checked", false);
        $('#rdb_admission_exam_result_low').prop( "checked", false);
        $('#rdb_admission_exam_result_middle').prop( "checked", false);
        $('#rdb_admission_exam_result_high').prop( "checked", false);
        $('#rdb_admission_exam_no_result').prop( "checked", false);

        if ($('#hdn_person_registration_id').val()){
        }else{
//Local diploma
            $('#pnl_secondary_education_main').css('visibility', 'visible').css('display','block');
            // on pnl_secondary_education_main
            if($('#hdn_diploma').val() == 'True'){
                $('#rdb_diploma_true').prop( "checked", true);
                $('#pnl_academic_year').css('visibility', 'visible').css('display','block');
                //on pnl_academic_year
                if ($('#hdn_secondary_education_academic_year').val() != ''){
                    $('#slt_academic_year'+' option').each(function(){
                        if($(this).attr('value')==$('#hdn_secondary_education_academic_year').val()){
                            $(this).prop('selected', true);
                        }
                    });
                }
                if($('#hdn_secondary_education_national').val() == 'True'){
                    display_local_secondary();
                }
                if($('#hdn_secondary_education_national').val() == 'False'){
                    display_foreign_secondary();
                }

            }else{
                $('#rdb_diploma_false').prop( "checked", true);
                //exam admi
                $('#pnl_admission_exam').css('visibility', 'visible').css('display','block');
                if($('#hdn_secondary_education_admission_exam').val() == 'True'){
                    $('#rdb_admission_exam_true').prop( "checked", true);
                }else{
                    $('#rdb_admission_exam_false').prop( "checked", true);
                }
                if($('#hdn_secondary_education_admission_exam_date').val() != ''){
                    $('#txt_admission_exam_date').val($('#hdn_secondary_education_admission_exam_date').val() );
                }
                if($('#hdn_secondary_education_admission_exam_institution').val() != ''){
                    $('#txt_admission_exam_institution').val($('#hdn_secondary_education_admission_exam_institution').val());
                }
                if($('#hdn_secondary_education_admission_exam_type_adhoc').val()=='True'){
                    $('#chb_admission_exam_type').prop( "checked", true);
                    $('#txt_admission_exam_type_other').val($('#hdn_secondary_education_admission_exam_type_name').val() );
                    $('#txt_admission_exam_type_other').prop( "disabled", false);

                }else{
                    if($('#hdn_secondary_education_admission_exam_type_id')){
                        $('#rdb_admission_exam_type_'+$('#hdn_secondary_education_admission_exam_type_id').val()).prop( "checked", true);
                    }
                }
                if($('#hdn_secondary_education_admission_exam_type_name').val()=="OTHER_EXAM"){
                    $('#txt_admission_exam_type_other').prop( "disabled", false);
                    $('#chb_admission_exam_type').prop( "checked", true);
                }

                if($('#hdn_secondary_education_admission_exam_type_name').val()=="LOW"){
                    $('#rdb_admission_exam_result_low').prop( "checked", true);
                }
                if($('#hdn_secondary_education_admission_exam_type_name').val()=="MIDDLE"){
                    $('#rdb_admission_exam_result_middle').prop( "checked", true);
                }
                if($('#hdn_secondary_education_admission_exam_type_name').val()=="HIGH"){
                    $('#rdb_admission_exam_result_high').prop( "checked", true);
                }
                if($('#hdn_secondary_education_admission_exam_type_name').val()=="NO_RESULT"){
                    $('#rdb_admission_exam_no_result').prop( "checked", true);
                }
            }
            //profession
            if($('#hdn_secondary_professional_exam_id').val() == ''){
                $('#rdb_professional_experience_false').prop( "checked", true);
            }else{
                $('#rdb_professional_experience_true').prop( "checked", true);
            }
            if($('#hdn_secondary_education_professional_exam_date').val() != ''){
                $('#txt_professional_exam_date').val($('#hdn_secondary_education_professional_exam_date').val() )
            }
            if($('#hdn_secondary_education_professional_exam_institution').val() != ''){
                $('#txt_professional_exam_institution').val($('#hdn_secondary_education_professional_exam_institution').val() )
            }
            if( $('#hdn_secondary_education_professional_exam_result').val() == 'LOW'){
                $('#rdb_professional_exam_result_result_low').prop( "checked", true);
            }
            if( $('#hdn_secondary_education_professional_exam_result').val() == 'MIDDLE'){
                $('#rdb_professional_exam_result_result_middle').prop( "checked", true);
            }
            if( $('#hdn_secondary_education_professional_exam_result').val() == 'HIGH'){
                $('#rdb_professional_exam_result_result_high').prop( "checked", true);
            }
            //local language exam
            if($('#hdn_local_language_exam_needed').val() == 'True'){
                $('#pnl_local_exam').css('visibility', 'visible').css('display','block');
                if($('#hdn_secondary_education_local_language_exam').val() == 'True'){
                    $('#rdb_local_language_exam_true').prop( "checked", true);

                    if($('#hdn_secondary_education_local_language_exam_date').val() != ''){
                        $('#txt_local_language_exam_date').val($('#hdn_secondary_education_local_language_exam_date').val());
                    }
                    if($('#hdn_secondary_education_local_language_exam_institution').val() != ''){
                        $('#txt_local_language_exam_institution').val($('#hdn_secondary_education_local_language_exam_institution').val());
                    }
                    if($('#hdn_secondary_education_local_language_exam_result').val() != ''){
                        if( $('#hdn_secondary_education_local_language_exam_result').val() == 'SUCCEED'){
                            $('#rdb_local_exam_session_succeed').prop( "checked", true);
                        }
                        if( $('#hdn_secondary_education_local_language_exam_result').val() == 'FAILED'){
                            $('#rdb_local_exam_session_failed').prop( "checked", true);
                        }
                        if( $('#hdn_secondary_education_local_language_exam_result').val() == 'ENROLLMENT_IN_PROGRESS'){
                            $('#rdb_local_exam_enrollment_enrollment_in_progress').prop( "checked", true);
                        }
                    }
                }else{
                    $('#rdb_local_language_exam_false').prop( "checked", true);
                }

            }
            //admission_exam
            if( $('#hdn_secondary_education_admission_exam_result').val() == 'LOW'){

                $('#rdb_admission_exam_result_low').prop( "checked", true);
            }
            if( $('#hdn_secondary_education_admission_exam_result').val() == 'MIDDLE'){
                $('#rdb_admission_exam_result_middle').prop( "checked", true);
            }

            if( $('#hdn_secondary_education_admission_exam_result').val() == 'HIGH'){
                $('#rdb_admission_exam_result_high').prop( "checked", true);
            }
            if( $('#hdn_secondary_education_admission_exam_result').val() == 'NO_RESULT'){
                $('#rdb_admission_exam_no_result').prop( "checked", true);
            }
        }
    }
});

function populate_secondary_national_institution(){
    if (! $('#hdn_secondary_education_national_institution_adhoc').val()=='True'){
        city_name = $("#hdn_secondary_education_national_institution_city").val();
        if(city_name==''){
            city_name = "-"
        }
        postal_code = $('#hdn_secondary_education_national_institution_postal_code').val()
        if(postal_code==''){
            postal_code = "-"
        }
        populate_city_default(city_name);
        postal_code = $("#hdn_secondary_education_national_institution_postal_code").val();
        if(postal_code==''){
            postal_code = "-"
        }
        if(city_name=='-'){
            $("#slt_postal_codes").find("option")
                .remove()
               .end();
            postal_code = $("#hdn_secondary_education_national_institution_postal_code").val();
            if(postal_code==''){
                postal_code = "-"
            }

            $.ajax({
                url: "/admission/institution_postal_codes?type=" + 'SECONDARY'
            }).then(function(data) {
                  if(data.length >0){
                  $("<option></option>").attr("value","-").append("-").appendTo("#slt_postal_codes");
                    $.each(data, function(key, value) {
                        if(value.city == postal_code){
                            $("<option></option>").attr("value",value.postal_code).prop('selected', true).append(value.postal_code).appendTo("#slt_postal_codes");
                        }else{
                            $("<option></option>").attr("value",value.postal_code).append(value.postal_code).appendTo("#slt_postal_codes");
                        }
                    });
                  }

            });
        }
        if (city_name!='' && city_name != '-'){
            populate_postal_code(city_name,postal_code);
            if ($('#hdn_secondary_education_national_institution_postal_code').val() != '' ){
                $('#slt_postal_codes'+' option').each(function(){
                    if($(this).attr('value')==postal_code){
                        $(this).prop('selected', true);
                    }
                });
            }
        }
        if( $("#hdn_secondary_education_national_institution_id").val() != ''){
            populate_secondary_institution(city_name,postal_code);
        }
    }
}

function populate_secondary_institution(city_name, postal_code){
    $("#slt_schools").find("option")
        .remove()
       .end();
    $("#slt_schools_community").find("option")
        .remove()
       .end();

    institution_id=$("#hdn_secondary_education_national_institution_id").val();
    if(institution_id==''){
        institution_id = "-"
    }
    $.ajax({
        url: "/admission/institutions?type=" + 'SECONDARY'+"&city=" + city_name + "&postal_code="+ postal_code
    }).then(function(data) {
          if(data.length >0){
            var option_selected="";
            if(data.length==1){
                option_selected = true;
            }
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_schools");
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_schools_community");

            $.each(data, function(key, value) {
                if(value.id == institution_id || option_selected){
                    $("<option></option>").attr("value",value.id).prop('selected', true).append(value.name).appendTo("#slt_schools");
                    $("<option></option>").attr("value",value.national_community).prop('selected', true).append(value.national_community).appendTo("#slt_schools_community");

                }else{
                    $("<option></option>").attr("value",value.id).append(value.name).appendTo("#slt_schools");
                    $("<option></option>").attr("value",value.national_community).append(value.national_community).appendTo("#slt_schools_community");
                }
            });
          }
    });

}

$("select[id^='slt_cities']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");

    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }

    $('#slt_postal_codes').prop("selectedIndex",-1);
    $('#slt_schools').prop("selectedIndex",-1);

    if(target.val() != '-'){
        populate_postal_code(target.val(),'-');
    }else{
        populate_city_default('-');
        populate_postal_code_default();
    }

    populate_secondary_institution(target.val(),'-')

});

$("select[id^='slt_postal_codes']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");

    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    $('#slt_cities').prop("selectedIndex",-1);
    $('#slt_schools').prop("selectedIndex",-1);

    $("#slt_cities").find("option")
        .remove()
        .end();
    if(target.val() != '-'){
        populate_city('-',target.val());
    }else{
        $.ajax({
            url: "/admission/institution_cities?type=" + 'SECONDARY'
        }).then(function(data) {
              if(data.length >0){
              $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities");
                $.each(data, function(key, value) {
                    var city_name_value= first_letter_each_word_uppercase(value.city) ;
                    $("<option></option>").attr("value",value.city).append(city_name_value).appendTo("#slt_cities");

                });
              }
        });
        $("#slt_postal_codes").find("option")
            .remove()
           .end();
        $.ajax({
            url: "/admission/institution_postal_codes?type=" + 'SECONDARY'
        }).then(function(data) {
              if(data.length >0){
              $("<option></option>").attr("value","-").append("-").appendTo("#slt_postal_codes");
                $.each(data, function(key, value) {
                    $("<option></option>").attr("value",value.postal_code).append(value.postal_code).appendTo("#slt_postal_codes");

                });
              }
        });
    }
    populate_secondary_institution('-',target.val())

});


$("select[id^='slt_academic_year']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");

    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    $('#hdn_secondary_education_academic_year').val(target.val());


});

$("select[id^='slt_country']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");

    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    $('#hdn_secondary_education_international_diploma_country_id').val(target.val());


});

$("select[id^='slt_language_diploma']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");

    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    $('#hdn_secondary_education_international_diploma_language_id').val(target.val());
    $('#slt_language_diploma_recognized').prop("selectedIndex",target.prop("selectedIndex"));
    $('#slt_language_diploma_recognized').val(target.val());

    if($('#slt_language_diploma_recognized option:selected').text() == 'True'){
        disabled_other_language();
    }else{
        enabled_other_language();
    }
});

function display_local_secondary(){
    $('#rdb_local').prop( "checked", true);
    //on pnl_local_detail
    $('#pnl_local_detail').css('visibility', 'visible').css('display','block');
    if($('#hdn_secondary_education_national_community').val() == 'FRENCH'){
        $('#rdb_local_community_french').prop( "checked", true);
        $('#pnl_teaching_type').css('visibility', 'visible').css('display','block');
    }
    if($('#hdn_secondary_education_national_community').val() == 'DUTCH'){
        $('#rdb_local_community_dutch').prop( "checked", true);
        $('#pnl_teaching_type').css('visibility', 'visible').css('display','block');
    }
    if($('#hdn_secondary_education_national_community').val() == 'GERMAN'){
        $('#rdb_local_community_german').prop( "checked", true);
        $('#pnl_teaching_type').css('visibility', 'visible').css('display','block');
    }
    populate_school_dropdown($('#hdn_secondary_education_national_institution_city').val(),
                             $('#hdn_secondary_education_national_institution_postal_code').val(),
                             $('#hdn_secondary_education_national_institution_adhoc').val(),
                             $('#hdn_secondary_education_national_institution_id').val(),
                             $('#hdn_secondary_education_national_institution_name').val()) ;

    national_community_display();
    if(($('#rdb_local_community_french').prop("checked") && $('#hdn_secondary_education_academic_year').val() < 1994)
        || (($('#rdb_local_community_dutch').prop("checked") && $('#hdn_secondary_education_academic_year').val() < 1992))){
        $('#rdb_dipl_acc_high_educ_true').prop( "checked", true);
        $('#pnl_dipl_acc_high_educ').css('visibility', 'visible').css('display','block');
    }else{
        $('#rdb_dipl_acc_high_educ_false').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_path_repetition').val() == 'True'){
        $('#rdb_repeated_grade_true').prop( "checked", true);
    }else{
        $('#rdb_repeated_grade_false').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_path_reorientation').val() == 'True'){
        $('#rdb_re_orientation_true').prop( "checked", true);
    }else{
        $('#rdb_re_orientation_false').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val() == 'LOW'){
        $('#rdb_result_less_65').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val() == 'MIDDLE'){
        $('#rdb_result_between_65_75').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val() == 'HIGH'){
        $('#rdb_result_more_75').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val() == 'NO_RESULT'){
        $('#rdb_no_result').prop( "checked", true);
    }

}

function display_foreign_secondary(){
   $('#rdb_foreign').prop( "checked", true);
    $('#pnl_foreign_detail').css('visibility', 'visible').css('display','block');
//foreign diploma
    if( $('#hdn_secondary_education_international_diploma').val() == 'NATIONAL'){
        $('#rdb_foreign_baccalaureate_diploma_national').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_international_diploma').val() == 'EUROPEAN'){
        $('#rdb_foreign_baccalaureate_diploma_european').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_international_diploma').val() == 'INTERNATIONAL'){
        $('#rdb_foreign_baccalaureate_diploma_international').prop( "checked", true);
    }

    $('#slt_country').prop("selectedIndex",0);
    $('#slt_country'+' option').each(function(){
        if($(this).attr('value')==$('#hdn_secondary_education_international_diploma_country_id').val()){
            $(this).prop('selected', true);
        }
    });

    $('#slt_language_diploma').prop("selectedIndex",0);
    $('#slt_language_diploma'+' option').each(function(){
        if($(this).attr('value')==$('#hdn_secondary_education_international_diploma_language_id').val()){
            $(this).prop('selected', true);
        }
    });
    $('#slt_language_diploma_recognized'+' option').each(function(){
        if($(this).attr('value')==$('#hdn_secondary_education_international_diploma_language_id').val()){
            $(this).prop('selected', true);
        }
    });
    if($('#slt_language_diploma_recognized option:selected').text() == 'True'){
        disabled_other_language();
    }else{
        enabled_other_language();
    }


    if( $('#hdn_secondary_education_international_diploma_language_recognized').val() == 'False'){
        $('#pnl_translation').css('visibility', 'visible').css('display','block');
    }else{
        $('#pnl_translation').css('visibility', 'hidden').css('display','none');
    }

    $('#slt_other_language_diploma').prop("selectedIndex",0);
    $('#slt_other_language_diploma'+' option').each(function(){
        if($(this).attr('value')==$('#hdn_secondary_education_international_diploma_language_id').val()){
            $(this).prop('selected', true);
        }
    });
    if( $('#hdn_secondary_education_international_equivalence').val()=="YES"){
        $('#rdb_international_equivalence_yes').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_international_equivalence').val()=="NO"){
        $('#rdb_international_equivalence_no').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_international_equivalence').val()=="DEMANDED"){
        $('#rdb_international_equivalence_in_progress').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val()=="LOW"){
        $('#rdb_foreign_result_low').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val()=="MIDDLE"){
        $('#rdb_foreign_result_middle').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val()=="HIGH"){
        $('#rdb_foreign_result_high').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_result').val()=="NO_RESULT"){
        $('#rdb_foreign_no_result').prop( "checked", true);
    }
}

function national_community_display(){

    if($('#hdn_secondary_education_national_community').val() == 'FRENCH' ||
       $('#hdn_secondary_education_national_community').val() == 'GERMAN' ||
       $('#hdn_secondary_education_national_community').val() == 'DUTCH'){

        $('#pnl_teaching_type').css('visibility', 'visible').css('display','block');
        if($('#hdn_secondary_education_education_type_id')){
            if($('#rdb_general_transition_'+$('#hdn_secondary_education_education_type_id').val())){
                $('#rdb_general_transition_'+$('#hdn_secondary_education_education_type_id').val()).prop( "checked", true);
            }
            if( $('#rdb_technic_'+$('#hdn_secondary_education_education_type_id').val())){
                $('#rdb_technic_'+$('#hdn_secondary_education_education_type_id').val()).prop( "checked", true);
            }
            if($('#hdn_secondary_education_education_type_adhoc').val() == 'True'){
                $('#chb_other_education').prop( "checked", true);
                $('#txt_other_education_type').prop( "disabled", false);
                $('#txt_other_education_type').val($('#hdn_secondary_education_education_type_name').val());
                $('[name^="rdb_education_transition_type"]').each(function(){
                    $(this).prop( "disabled", true);
                });
                $('[name^="rdb_education_technic_type"]').each(function(){
                    $(this).prop( "disabled", true);
                });
            }
        }
    }

}

function populate_exam_admin(){
    if($('#hdn_secondary_education_admission_exam').val() == 'True'){
        $('#rdb_admission_exam_true').prop( "checked", true);
        $('#pnl_admission_exam').css('visibility', 'visible').css('display','block');
    }else{
        $('#rdb_admission_exam_false').prop( "checked", true);
        $('#pnl_admission_exam').css('visibility', 'hidden').css('display','none');
    }
    if($('#hdn_diploma').val()=="False"){
        $('#pnl_admission_exam').css('visibility', 'visible').css('display','block');
    }
    if($('#hdn_secondary_education_admission_exam_date').val() != ''){
        $('#txt_admission_exam_date').val($('#hdn_secondary_education_admission_exam_date').val() );
    }
    if($('#hdn_secondary_education_admission_exam_institution').val() != ''){
        $('#txt_admission_exam_institution').val($('#hdn_secondary_education_admission_exam_institution').val());
    }
    if($('#hdn_secondary_education_admission_exam_type_adhoc').val()=='True'){
        $('#chb_admission_exam_type').prop( "checked", true);
        $('#txt_admission_exam_type_other').val($('#hdn_secondary_education_admission_exam_type_name').val() );
        $('#txt_admission_exam_type_other').prop( "disabled", false);

    }else{
        if($('#hdn_secondary_education_admission_exam_type_id')){
            $('#rdb_admission_exam_type_'+$('#hdn_secondary_education_admission_exam_type_id').val()).prop( "checked", true);
        }
    }
    if($('#hdn_secondary_education_admission_exam_type_name').val()=="OTHER_EXAM"){
        $('#txt_admission_exam_type_other').prop( "disabled", false);
        $('#chb_admission_exam_type').prop( "checked", true);
    }

    if($('#hdn_secondary_education_admission_exam_type_name').val()=="LOW"){
        $('#rdb_admission_exam_result_low').prop( "checked", true);
    }
    if($('#hdn_secondary_education_admission_exam_type_name').val()=="MIDDLE"){
        $('#rdb_admission_exam_result_middle').prop( "checked", true);
    }
    if($('#hdn_secondary_education_admission_exam_type_name').val()=="HIGH"){
        $('#rdb_admission_exam_result_high').prop( "checked", true);
    }
    if($('#hdn_secondary_education_admission_exam_type_name').val()=="NO_RESULT"){
        $('#rdb_admission_exam_no_result').prop( "checked", true);
    }
}

$("#rdb_professional_experience_false").click(function() {
    $('#txt_professional_exam_date').val('');
    $('#txt_professional_exam_institution').val('');
    $('#rdb_professional_exam_result_result_low').prop( "disabled", false);
    $('#rdb_professional_exam_result_middle').prop( "disabled", false);
    $('#rdb_professional_exam_result_high').prop( "disabled", false);
    $('#rdb_professional_exam_no_result').prop( "disabled", false);
    delete_document('PROFESSIONAL_EXAM_CERTIFICATE');
});

$("#chb_other_education").change(function() {
    if ($('#chb_other_education').prop( "checked")){
            $('[name^="rdb_education_transition_type"]').each(function(){
                $(this).prop( "disabled", true);
                $(this).prop( "checked", false);
            });
            $('[name^="rdb_education_technic_type"]').each(function(){
                $(this).prop( "disabled", true);
                $(this).prop( "checked", false);
            });
            $('#txt_other_education_type').prop( "disabled",false);

    }else{
            $('[name^="rdb_education_transition_type"]').each(function(){
                $(this).prop( "disabled", false);
            });
            $('[name^="rdb_education_technic_type"]').each(function(){
                $(this).prop( "disabled", false);
            });
            $('#txt_other_education_type').prop( "disabled",true);
            $('#txt_other_education_type').val('');
    }
});



$("#rdb_diploma_false").click(function() {
    $('#pnl_academic_year').css('visibility', 'hidden').css('display','none');
    if($('#hdn_local_language_exam_needed').val()=="True"){
        $('#pnl_admission_exam').css('visibility', 'visible').css('display','block');
    }else{
        $('#pnl_admission_exam').css('visibility', 'hidden').css('display','none');
    }
});

$("#rdb_diploma_true").click(function() {
    $('#pnl_academic_year').css('visibility', 'visible').css('display','block');
    $('#pnl_admission_exam').css('visibility', 'hidden').css('display','none');
});

function first_letter_each_word_uppercase(str){
  str=str.toLowerCase();
  return str.replace(/(\b)([a-zA-Z])/g,
           function(firstLetter){
              return   firstLetter.toUpperCase();
           });
}

function populate_postal_code(city_name,postal_code){
    if ($('#hdn_secondary_education_national_institution_adhoc').val()!='True'){
        $.ajax({
            url: "/admission/postalcodes?city=" + city_name
        }).then(function(data) {
            $("#slt_postal_codes").find("option")
                .remove()
                .end();
            if(data.length >0){
                $("<option></option>").attr("value","-").append("-").appendTo("#slt_postal_codes");

                var option_selected = false;
                postal_code= '-'
                if(data.length==1){
                    option_selected = true;
                }else{
                    postal_code= $('#hdn_secondary_education_national_institution_postal_code').val();
                }
                $.each(data, function(key, value) {
                    if(option_selected || postal_code==value.postal_code){
                        $("<option></option>").attr("value",value.postal_code).prop('selected', true).append(value.postal_code).appendTo("#slt_postal_codes");
                    }else{
                        $("<option></option>").attr("value",value.postal_code).append(value.postal_code).appendTo("#slt_postal_codes");
                    }
                });

            }

        });
    }
}

function populate_city(city_name,postal_code){
    if ($('#hdn_secondary_education_national_institution_adhoc').val()!='True'){
        $.ajax({
            url: "/admission/educationinstitution/cities?postal_code=" + postal_code
        }).then(function(data) {
            $("#slt_cities").find("option")
                .remove()
                .end();
                $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities");
            if(data.length >0){
                var option_selected = false;
                if(data.length==1){
                    option_selected = true;
                }
                $.each(data, function(key, value) {
                    var city_name_value = first_letter_each_word_uppercase(value.city);
                    if(option_selected){
                        $("<option></option>").attr("value",value.city).prop('selected', true).append(city_name_value).appendTo("#slt_cities");
                    }else{
                        $("<option></option>").attr("value",value.city).append(city_name_value).appendTo("#slt_cities");
                    }
                });

            }
        });
    }
}

function populate_city_default(city_name){
    //Populate the dropdown list of city for education institution.
    //The cities for schools are all the distinct cities existing in the table EducationInstitution
    $("#slt_cities").find("option")
        .remove()
        .end();
    $.ajax({
        url: "/admission/institution_cities?type=" + 'SECONDARY'
    }).then(function(data) {
          if(data.length >0){
          $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities");
            $.each(data, function(key, value) {
                var city_name_value= first_letter_each_word_uppercase(value.city) ;
                if(value.city == city_name){
                    $("<option></option>").attr("value",value.city).prop('selected', true).append(city_name_value).appendTo("#slt_cities");
                }else{
                    $("<option></option>").attr("value",value.city).append(city_name_value).appendTo("#slt_cities");
                }
            });
          }
    });
}

$("#chb_other_school").change(function(event) {
    var target = $(event.target);
    if(target.prop("checked")){
        $('#pnl_other_school').css('visibility', 'visible').css('display','block');
        $('#slt_cities').prop( "disabled", true);
        $('#slt_postal_codes').prop( "disabled", true);
        $('#slt_schools').prop( "disabled", true);
        $('#slt_cities').prop( "selectedIndex", -1);
        $('#slt_postal_codes').prop( "selectedIndex", -1);
        $('#slt_schools').prop("selectedIndex",-1);
        $('#hdn_secondary_education_national_institution_adhoc').val('True') ;
    }else{
        $('#pnl_other_school').css('visibility', 'hidden').css('display','none');
        $('#slt_cities').prop( "disabled", false);
        $('#slt_postal_codes').prop( "disabled", false);
        $('#slt_schools').prop( "disabled", false);
        $('#hdn_secondary_education_national_institution_adhoc').val('False') ;
        populate_city_default('-');
        populate_postal_code_default();
    }

});

function populate_postal_code_default(){
    //Populate the dropdown list of postal codes for education institution.
    //The postal codes for schools are all the distinct postal code existing in the table EducationInstitution
    $("#slt_postal_codes").find("option")
        .remove()
       .end();
    $.ajax({
        url: "/admission/institution_postal_codes?type=" + 'SECONDARY'
    }).then(function(data) {
          $("#slt_postal_codes").prop("selectedIndex",-1);
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_postal_codes");
            $.each(data, function(key, value) {
                $("<option></option>").attr("value",value.postal_code).append(value.postal_code).appendTo("#slt_postal_codes");
            });
          }
    });
}

function populate_school_dropdown(city_name, postal_code, adhoc, institution_id, institution_name){
    if(institution_id!=''){
        if(adhoc == 'False'){
            enabled_known_national_school();
            if (city_name!='' && postal_code!=''){
                populate_city(city_name,postal_code);
                populate_postal_code(city_name,postal_code);
                populate_secondary_institution(city_name,postal_code);
                if ($('#hdn_secondary_education_national_institution_postal_code').val() != '' ){
                    $('#slt_postal_codes'+' option').each(function(){
                        if($(this).attr('value')==postal_code){
                            $(this).prop('selected', true);
                        }
                    });
                }
            }
        }else{
            if(adhoc == 'True'){
                empty_disabled_known_national_school(city_name, postal_code,institution_name);
            }
        }

    }else{
        populate_city_default('-');
        populate_postal_code_default()
    }
}

function empty_disabled_known_national_school(city_name, postal_code,institution_name){
    $('#slt_cities').prop( "disabled", true);
    $("#slt_cities").find("option")
        .remove()
        .end();

    $('#slt_postal_codes').prop( "disabled", true);
    $("#slt_postal_codes").find("option")
        .remove()
        .end();

    $('#slt_schools').prop( "disabled", true);
    $("#slt_schools").find("option")
        .remove()
        .end();

    $('#pnl_other_school').css('visibility', 'visible').css('display','block');
    $('#chb_other_school').prop( "checked", true);
    $('#txt_CESS_other_school_name').val(institution_name);
    $('#txt_CESS_other_school_name').prop( "disabled", false);
    $('#txt_CESS_other_school_city').val(city_name);
    $('#txt_CESS_other_school_city').prop( "disabled", false);
    $('#txt_CESS_other_school_postal_code').val(postal_code);
    $('#txt_CESS_other_school_postal_code').prop( "disabled", false);
}

function enabled_known_national_school(){
    $('#slt_cities').prop( "disabled", false);
    $('#slt_postal_codes').prop( "disabled", false);
    $('#slt_schools').prop( "disabled", false);
    $('#pnl_other_school').css('visibility', 'hidden').css('display','none');
    $('#chb_other_school').prop( "checked", false);
    $('#txt_CESS_other_school_name').val('');
    $('#txt_CESS_other_school_name').prop( "disabled", true);
    $('#txt_CESS_other_school_city').val('');
    $('#txt_CESS_other_school_city').prop( "disabled", true);
    $('#txt_CESS_other_school_postal_code').val('');
    $('#txt_CESS_other_school_postal_code').prop( "disabled", true);
}

$("#rdb_local").click(function(event) {
    $('#hdn_secondary_education_national_institution_city').val('')
    $('#hdn_secondary_education_national_institution_postal_code').val('');
    $('#hdn_secondary_education_national_institution_adhoc').val('');
    $('#hdn_secondary_education_national_institution_id').val('');
    $('#hdn_secondary_education_national_institution_name').val('');
    reset_rdb_local_community(false);
    $('#rdb_repeated_grade_true').prop("checked", false);
    $('#rdb_repeated_grade_false').prop("checked", false);
    $('#rdb_re_orientation_true').prop("checked", false);
    $('#rdb_re_orientation_false').prop("checked", false);
    $('#rdb_dipl_acc_high_educ_true').prop("checked", false);
    $('#rdb_dipl_acc_high_educ_false').prop("checked", false);
    populate_school_dropdown('', '', '', '', '');
});

function display_date_msg_error(value, id_msg_field){
    $(id_msg_field).find("label").remove();
    if (isDate(value)){
        $(id_msg_field).find("label").remove();
    }else{
        $(id_msg_field).append("<label>"+gettext('invalid_date')+"</label>");
    }
}

$("#txt_professional_exam_date").blur(function() {
    display_date_msg_error($("#txt_professional_exam_date").val(), "#msg_error_txt_professional_exam_date");
});

$("#txt_admission_exam_date").blur(function() {
    display_date_msg_error($("#txt_admission_exam_date").val(), "#msg_error_txt_admission_exam_date");
});

$("#txt_local_language_exam_date").blur(function() {
    display_date_msg_error($("#txt_local_language_exam_date").val(), "#msg_error_local_language_exam_date");
});

function reset_rdb_local_community(status){
    $('#rdb_local_community_french').prop( "checked", status);
    $('#rdb_local_community_dutch').prop( "checked", status);
    $('#rdb_local_community_german').prop( "checked", status);
}

$("select[id^='slt_language_diploma_recognized']" ).change(function(event) {
    var target = $(event.target);

    if (typeof id == 'undefined') {
        target = target.parent();

    }
    if(target.val()=="True"){
        enabled_other_language();
    }else{
        if(target.val()=="False"){
            disabled_other_language();
        }else{
            disabled_other_language();
        }
    }

});

function disabled_other_language(){
    document.getElementById('pnl_translation').style="visibility:hidden;display:none;";
}

function enabled_other_language(){
    document.getElementById('slt_country').selectedIndex = 0;
    document.getElementById('pnl_translation').style="visibility:visible;display:block;";

}

$("#slt_schools").change(function(event) {
    $('#slt_schools_community').prop("selectedIndex",$('#slt_schools').prop("selectedIndex"));
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

$("#rdb_no_result").click(function(event) {
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

$("#rdb_local_community_french").click(function(event) {
    $('#national_diploma_local_community_error').html('');
});

$("#rdb_local_community_dutch").click(function(event) {
    $('#national_diploma_local_community_error').html('');
});

$("#rdb_local_community_german").click(function(event) {
    $('#national_diploma_local_community_error').html('');
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

$( "#txt_professional_exam_institution").blur(function() {
    $('#professional_exam_institution_error').html('');
});

$( "input[name^='professional_exam_result']" ).click(function() {
    $('#professional_exam_result_error').html('');
});
$("#bt_load_doc_PROFESSIONAL_EXAM_CERTIFICATE" ).click(function() {
    $('#professional_exam_doc_error').html('');
});

$("button[id^='bt_load_doc_HIGH_SCHOOL_SCORES_TRANSCRIPT_']" ).click(function() {
    $('#high_school_diploma_doc_error').html('');
});