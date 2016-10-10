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

        $('#rdb_loal_community_french').prop( "checked", false);
        $('#rdb_local_community_dutch').prop( "checked", false);
        $('#rdb_local_community_german').prop( "checked", false);

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

        $('#rdb_school_local_community_french').prop( "checked", false);
        $('#rdb_school_local_community_dutch').prop( "checked", false);
        $('#rdb_school_local_community_german').prop( "checked", false);

        $('#rdb_school_local_community_french').prop( "disabled", true);
        $('#rdb_school_local_community_dutch').prop( "disabled", true);
        $('#rdb_school_local_community_german').prop( "disabled", true);

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

        if ($('#hdn_person_registration_id').val()){
        }else{
//Local diploma
            $('#pnl_secondary_education_main').css('visibility', 'visible').css('display','block');
            // on pnl_secondary_education_main
            if($('#hdn_diploma').val() == 'True'){
                $('#rdb_diploma_true').prop( "checked", true);
                $('#pnl_academic_year').css('visibility', 'visible').css('display','block');
                //on pnl_academic_year
                if ($('#hdn_secondary_education_academic_year_id').val() != ''){
                    $('#slt_academic_year'+' option').each(function(){
                        if($(this).attr('value')==$('#hdn_secondary_education_academic_year_id').val()){
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
            $('#pnl_teaching_type').css('visibility', 'hidden').css('display','none');

            $.each(data, function(key, value) {
                if(value.id == institution_id || option_selected){
                    $("<option></option>").attr("value",value.id).prop('selected', true).append(value.name).appendTo("#slt_schools");
                    $("<option></option>").attr("value",value.national_community).prop('selected', true).append(value.national_community).appendTo("#slt_schools_community");
                    if(value.national_community=='FRENCH'){
                        $('#pnl_teaching_type').css('visibility', 'visible').css('display','block');
                    }
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
                    var city_name_value= ucwords(value.city,true) ;
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
    $('#hdn_secondary_education_academic_year_id').val(target.val());


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


});

function display_local_secondary(){
    $('#rdb_local').prop( "checked", true);
    //on pnl_local_detail
    $('#pnl_local_detail').css('visibility', 'visible').css('display','block');
    if($('#hdn_secondary_education_national_community').val() == 'FRENCH'){
        $('#rdb_local_community_french').prop( "checked", true);
    }
    if($('#hdn_secondary_education_national_community').val() == 'DUTCH'){
        $('#rdb_local_community_dutch').prop( "checked", true);
    }
    if($('#hdn_secondary_education_national_community').val() == 'GERMAN'){
        $('#rdb_local_community_german').prop( "checked", true);
    }

    if($('#hdn_secondary_education_national_institution_adhoc').val() == 'True'){
        $('#pnl_other_school').css('visibility', 'visible').css('display','block');
        $('#chb_other_school').prop( "checked", true);
        $('#txt_CESS_other_school_name').prop( "disabled", false);
        $('#txt_CESS_other_school_name').val($('#hdn_secondary_education_national_institution_name').val());
        $('#txt_CESS_other_school_city').prop("disabled", false);
        $('#txt_CESS_other_school_city').val($('#hdn_secondary_education_national_institution_city').val());
        $('#txt_CESS_other_school_postal_code').prop( "disabled", false);
        $('#txt_CESS_other_school_postal_code').val($('#hdn_secondary_education_national_institution_postal_code').val());
        $('#slt_schools').prop( "disabled", true);
        $('#slt_cities').prop( "disabled", true);
        $('#slt_postal_codes').prop( "disabled", true);
    }else{
        if($('#hdn_original_national_institution_id_').val() != ''){
            $('#slt_cities'+' option').each(function(){
                if($(this).attr('value')==$('#hdn_secondary_education_national_institution_city').val()){
                    $(this).prop('selected', true);
                }
            });
            $('#slt_postal_codes'+' option').each(function(){
                if($(this).attr('value')==$('#hdn_secondary_education_national_institution_postal_code').val()){
                    $(this).prop('selected', true);
                }
            });
            $('#slt_schools'+' option').each(function(){
                if($(this).attr('value')==$('#slt_schools').val()){
                    $(this).prop('selected', true);
                }
            });

        }

    }
    if($('#hdn_secondary_education_national_institution_id').val()!='' && $('#hdn_secondary_education_national_institution_adhoc').val()=='False'){
        populate_city('-',$('#hdn_secondary_education_national_institution_postal_code').val());
        populate_postal_code($('#hdn_secondary_education_national_institution_city').val(),$('#hdn_secondary_education_national_institution_postal_code').val());
    }else{
        if($('#hdn_secondary_education_national_institution_adhoc').val()!='True'){
            populate_city_default('-');
            populate_postal_code_default;
        }
    }

    populate_secondary_institution($('#hdn_secondary_education_national_institution_city').val(),$('#hdn_secondary_education_national_institution_postal_code').val());
    national_community_display();
    if(($('#rdb_local_community_french').checked && $('#hdn_secondary_education_academic_year').val()<1994)
        || (($('#rdb_local_community_dutch').checked && $('#hdn_secondary_education_academic_year').val()<1992))){
        $('#rdb_dipl_acc_high_educ_true').prop( "checked", true);
        $('#pnl_dipl_acc_high_educ').css('visibility', 'visible').css('display','block');
    }else{
        $('#rdb_dipl_acc_high_educ_false').prop( "checked", true);
    }
    if( $('#hdn_secondary_education_academic_year').val() < 1994){
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

    if( $('#hdn_secondary_education_international_diploma_language_recognized').val() == 'False'){
        $('#chb_other_language_regime').prop( "checked", true);
        $('#slt_other_language_diploma').prop( "disabled", false);
        $('#slt_language_diploma').prop( "disabled", true);
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
}

function national_community_display(){

    if($('#hdn_secondary_education_national_institution_national_community').val() == 'FRENCH'){
        $('#rdb_school_local_community_french').prop( "checked", true);
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
    if($('#hdn_secondary_education_national_institution_national_community').val() == 'DUTCH'){
        $('#rdb_school_local_community_dutch').prop( "checked", true);
    }
    if($('#hdn_secondary_education_national_institution_national_community').val() == 'GERMAN'){
        $('#rdb_school_local_community_german').prop( "checked", true);
    }
    if($('#hdn_secondary_education_national_institution_adhoc').val()=='False' || $('#hdn_secondary_education_national_institution_adhoc').val()==''){
        $('#rdb_school_local_community_french').prop( "checked", false);
        $('#rdb_school_local_community_dutch').prop( "checked", false);
        $('#rdb_school_local_community_german').prop( "checked", false);
        $('#rdb_school_local_community_french').prop( "disabled", true);
        $('#rdb_school_local_community_dutch').prop( "disabled", true);
        $('#rdb_school_local_community_german').prop( "disabled", true);
    }else{
        $('#rdb_school_local_community_french').prop( "disabled", false);
        $('#rdb_school_local_community_dutch').prop( "disabled", false);
        $('#rdb_school_local_community_german').prop( "disabled", false);
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
}

$("#rdb_professional_experience_false").click(function() {
    $('#txt_professional_exam_date').val('');
    $('#txt_professional_exam_institution').val('');
    $('#rdb_professional_exam_result_result_low').prop( "disabled", false);
    $('#rdb_professional_exam_result_middle').prop( "disabled", false);
    $('#rdb_professional_exam_result_high').prop( "disabled", false);
    delete_document('PROFESSIONAL_EXAM_CERTIFICATE');
});

$("#chb_other_school").change(function() {
    if ($('#chb_other_school').prop( "checked")){
        $('#rdb_school_local_community_french').prop( "disabled", false);
        $('#rdb_school_local_community_dutch').prop( "disabled", false);
        $('#rdb_school_local_community_german').prop( "disabled", false);
    }else{
        $('#rdb_school_local_community_french').prop( "checked", false);
        $('#rdb_school_local_community_dutch').prop( "checked", false);
        $('#rdb_school_local_community_german').prop( "checked", false);
        $('#rdb_school_local_community_french').prop( "disabled", true);
        $('#rdb_school_local_community_dutch').prop( "disabled", true);
        $('#rdb_school_local_community_german').prop( "disabled", true);
    }
});

$("#chb_other_education").change(function() {
    if ($('#chb_other_education').prop( "checked")){
            $('[name^="rdb_education_transition_type"]').each(function(){
                $(this).prop( "disabled", true);
            });
            $('[name^="rdb_education_technic_type"]').each(function(){
                $(this).prop( "disabled", true);
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

function ucwords(str,force){
  str=force ? str.toLowerCase() : str;
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
                    if(option_selected){
                        $("<option></option>").attr("value",value.city).prop('selected', true).append(value.city).appendTo("#slt_cities");
                    }else{
                        $("<option></option>").attr("value",value.city).append(value.city).appendTo("#slt_cities");
                    }
                });

            }
        });
    }
}

function populate_city_default(city_name){
    //Populate the dropdown list of city for education institution.
    //The citiess for schools are all the distinct cities existing in the table EducationInstitution
    $("#slt_cities").find("option")
        .remove()
        .end();
    $.ajax({
        url: "/admission/institution_cities?type=" + 'SECONDARY'
    }).then(function(data) {
          if(data.length >0){
          $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities");
            $.each(data, function(key, value) {
                var city_name_value= ucwords(value.city,true) ;
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