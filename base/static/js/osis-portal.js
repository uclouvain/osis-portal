$("#slt_offer_type").change(function() {

    init_static_questions();
    $("#pnl_grade_choices").find("label")
        .remove()
        .end()
    // Remove the offers
    $("#pnl_offers").find("table")
        .remove()
        .end()
    set_pnl_questions_empty();
    //Cancel the previous selection
    document.getElementById("txt_offer_year_id").value = "";

    if($("#slt_offer_type").val()=="BACHELOR" || $("#slt_offer_type").val()=="MASTER" || $("#slt_offer_type").val()=="TRAINING_CERTIFICATE"){
        $("#hdn_local_language_exam_needed").val('True')
         $('#pnl_local_exam').css('visibility', 'visible').css('display','block');
    }else{
        $("#hdn_local_language_exam_needed").val('False')
        $('#pnl_local_exam').css('visibility', 'hidden').css('display','none');
    }

    $('#bt_save').prop("disabled",true);
    var i=0;

    ajax_grade_choice('');

});

$("#slt_domain").change(function() {
    offer_selection_display();
});

function offer_selection_display(){
    var radio_button_value;

    if ($("input[name='grade_choice']:checked").length > 0){
       radio_button_value = $('input[name="grade_choice"]:checked').val();
    }


    //Cancel the previous selection
    document.getElementById("txt_offer_year_id").value = "";

    $('#bt_save').prop("disabled",true);
    ajax_offers(radio_button_value, '');

}

function selection(row_number, offers_length, offer_year_id){
    var elt = "offer_row_" + row_number;
    var cpt = 0;
    var already_selected =new Boolean(false);
    while (cpt < offers_length ){
        elt = "offer_row_" + cpt;
        if (document.getElementById(elt).style.color == "green" && document.getElementById("txt_offer_year_id").value == offer_year_id){
            already_selected=new Boolean(true);
        }
        document.getElementById(elt).style.color = "black";
        document.getElementById("offer_sel_" + row_number).checked = false;
        cpt++;
    }
    elt = "offer_row_" + row_number;
    document.getElementById(elt).style.color = "green";
    document.getElementById("txt_offer_year_id").value = offer_year_id;
    $('#bt_save').prop("disabled",false);


    if(already_selected == true){
        document.getElementById(elt).style.color = "black";
        document.getElementById("txt_offer_year_id").value = "";
        $('#bt_save').prop("disabled",true);
    }else{

        document.getElementById(elt).style.color = "green";
        document.getElementById("txt_offer_year_id").value = offer_year_id;
        $('#bt_save').prop("disabled",false);
        document.getElementById("offer_sel_" + row_number).checked = true;
    }
    display_dynamic_form(offer_year_id);
    ajax_static_questions(offer_year_id,'','','');


    }

function set_pnl_questions_empty(){
    $("#pnl_questions").find("label")
    .remove()
    .end()
    $("#pnl_questions").find("br")
    .remove()
    .end()
    $("#pnl_questions").find("input")
    .remove()
    .end()
    $("#pnl_questions").find("textarea")
    .remove()
    .end()
    $("#pnl_questions").find("select")
    .remove()
    .end()
    $("#pnl_questions").find("a")
    .remove()
    .end()
}

function display(id,state){
    var elt = document.getElementById(id);

    if(state){
        elt.style = "visibility:visible;display:block;";
    }else{
        elt.style = "visibility:hidden;display:none;";
    }
}

function reset_radio(elt_name){
    x=document.getElementsByName(elt_name);
    var i;
    for (i = 0; i < x.length; i++) {

        if (x[i].type == "radio") {
            x[i].checked = false;
        }
    }
}

function disabled_reset_field_txt(id, state){
    if(state){
        document.getElementById(id).disabled = true;
    }else{
        document.getElementById(id).disabled = false;
    }
    document.getElementById(id).value="";
}

$("#slt_nationality").change(function() {
   $.ajax({
       url: "/admission/country?nationality=" + $("#slt_nationality").val()
     }).then(function(data) {
        if (data.european_union) {
              $('#pnl_assimilation_criteria').css('visibility', 'hidden').css('display','none');
        }else{
              $('#pnl_assimilation_criteria').css('visibility', 'visible').css('display','block');
        }
     });
 });

//Display pnl_offer_vae only for Masters and only when rdb_offer_belgiandegree_false is clicked

$("#rdb_offer_belgiandegree_true").click(function() {
           $.ajax({
            url: "/admission/offer?offer=" + $("#txt_offer_year_id").val()
           }).then(function(data) {

            if (data.grade_type!=1){
               $('#pnl_offer_vae').css('visibility', 'hidden').css('display','none');
               $('#pnl_offer_vae').find('input[type=radio]:checked').removeAttr('checked');
               $('#pnl_offer_vae').find('input').removeAttr('required');
              }
        });

});

$("#rdb_offer_belgiandegree_false").click(function() {
           $.ajax({
            url: "/admission/offer?offer=" + $("#txt_offer_year_id").val()
           }).then(function(data) {

            if (data.grade_type!=1){
               $('#pnl_offer_vae').css('visibility', 'visible').css('display','block');
               $('#pnl_offer_vae').find('input').prop('required', true );
              }
        });

});


$("#rdb_offer_samestudies_true").click(function() {
   $('#pnl_offer_valuecredits').css('visibility', 'visible').css('display','block');
   $('#pnl_offer_valuecredits').find('input').prop('required', true );
});

$("#rdb_offer_samestudies_false").click(function() {
   $('#pnl_offer_valuecredits').css('visibility', 'hidden').css('display','none');
   $('#pnl_offer_valuecredits').find('input[type=radio]:checked').removeAttr('checked');
   $('#pnl_offer_valuecredits').find('input').removeAttr('required');
});

///OFFER SUBJECT TO QUOTA

$("#rdb_offer_sameprogram_true").click(function() {

   $('#pnl_offer_resident').css('visibility', 'hidden').css('display','none');
   $('#pnl_offer_resident').find('input[type=radio]:checked').removeAttr('checked');
   $('#pnl_offer_resident').find('input').removeAttr('required');

   $('#pnl_offer_lottery').css('visibility', 'hidden').css('display','none');
   $('#txt_offer_lottery').val('');
   $('#txt_offer_lottery').find('input').removeAttr('required');
});

$("#rdb_offer_sameprogram_false").click(function() {

   $('#pnl_offer_resident').css('visibility', 'visible').css('display','block');
   $('#pnl_offer_resident').find('input').prop('required', true );
});

$("#rdb_offer_resident_true").click(function() {
   $('#pnl_offer_lottery').css('visibility', 'hidden').css('display','none');
   $('#txt_offer_lottery').val('');
   $('#txt_offer_lottery').find('input').removeAttr('required');
});

$("#rdb_offer_resident_false").click(function() {
   $('#pnl_offer_lottery').css('visibility', 'visible').css('display','block');
   $('#pnl_offer_lottery').find('input').prop('required', true);
});


function init_static_questions (){
   $("#pnl_static_questions").children().css('visibility', 'hidden').css('display','none');
   $('#pnl_static_questions').find('input[type=radio]:checked').removeAttr('checked');
   $('#pnl_static_questions').find('input').removeAttr('required');
   $('#txt_offer_lottery').val('');

}


$("select[id^='slt_foreign_institution_country_']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    year = id.replace('slt_foreign_institution_country_','');

    $("#slt_cities_"+year).find("option")
        .remove()
       .end();

    $("#slt_foreign_university_name_"+year).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/cities?country=" + target.val()
      }).then(function(data) {
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities_"+year);
            $.each(data, function(key, value) {
                $("<option></option>").attr("value",value.city).append(value.city).appendTo("#slt_cities_"+year);
            });
          }

      });

 });

 $("select[id^='slt_cities_']" ).change(function(event) {

    var target = $(event.target);
    var id = target.attr("id");
    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    year = id.replace('slt_cities_','');
    country = document.getElementById('slt_foreign_institution_country_'+year);

    $("#slt_foreign_university_name_"+year).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/universities?city=" + target.val()
      }).then(function(data) {
          if(data.length >0){
          $("<option></option>").attr("value","-").append("-").appendTo("#slt_foreign_university_name_"+year);
            $.each(data, function(key, value) {
                $("<option></option>").attr("value",value.id).append(value.name).appendTo("#slt_foreign_university_name_"+year);
            });
          }

      });

 });

 $("select[id^='slt_linguistic_regime_']").change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    year = id.replace('slt_linguistic_regime_','');

    $.ajax({
        url: "/admission/langue_recognized?language=" + target.val()
      }).then(function(data) {
          if(data.length >0){
            $.each(data, function(key, value) {
                if(value.recognized ){
                    $("#pnl_translation_"+year).css('visibility', 'hidden').css('display','none');
                }else{
                    $("#pnl_translation_"+year).css('visibility', 'visible').css('display','block');
                }

            });
          }

      });

 });

function disabled_field(id,chb) {
    if(chb.checked){
        document.getElementById(id).disabled = false;
    }else{
        document.getElementById(id).disabled = true;
    }
}

function disabled_field_specify(id, state) {
    if(! state){
        document.getElementById(id).disabled = false;
    }else{
        document.getElementById(id).disabled = true;
    }
}

function reset_select_state(id, state){
    if(state.checked){
        document.getElementById(id).selectedIndex = -1;
    }
}

function reset_input(id){
    document.getElementById(id).value="";
}

$("select[id^='slt_national_high_non_university_institution_city_']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");

    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }

    year = id.replace('slt_national_high_non_university_institution_city_','');
    populate_institution($("#hdn_original_national_institution_id_"+year).val(),
                         target.val(),
                         'slt_national_high_non_university_institution_city_'+year,
                         'slt_national_high_non_university_institution_'+year)

});


$("select[id^='slt_foreign_high_institution_country_']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    year = id.replace('slt_foreign_high_institution_country_','');

    $("#slt_cities_high_"+year).find("option")
        .remove()
       .end();

    $("#slt_foreign_high_name_"+year).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/high_cities?country=" + target.val()
      }).then(function(data) {
          if(data.length >0){

            $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities_high_"+year);
            $.each(data, function(key, value) {
                $("<option></option>").attr("value",value.city).append(value.city).appendTo("#slt_cities_high_"+year);
            });
          }

      });
 });

 $("select[id^='slt_cities_high_']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    year = id.replace('slt_cities_high_','');

    $("#slt_foreign_high_name_"+year).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/high_institutions?city=" + target.val()
      }).then(function(data) {
          if(data.length >0){
          $("<option></option>").attr("value","-").append("-").appendTo("#slt_foreign_high_name_"+year);
            $.each(data, function(key, value) {
                $("<option></option>").attr("value",value.id).append(value.name).appendTo("#slt_foreign_high_name_"+year);
            });
          }

      });

 });

$("input[name^='path_type_']").change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    var name = target.attr("name");

    year = name.replace('path_type_','');

    var radio_value = target.val();
    // To erase the data from previous saving
    var elts = document.getElementsByTagName("input");
    for (var i = 0; i < elts.length; i++) {
        if(elts[i].id.indexOf('hdn_original_') > -1 && elts[i].id.indexOf('_'+year) > -1 ){
            elts[i].value = "";
        }
    }
    display_main_panel(radio_value,year);
});

$("input[name^='national_education_']").change(function(event) {
    var target = $(event.target);
    var name = target.attr("name");
    year = name.replace('national_education_','');
    var radio_value = target.val();
    display_belgian_universities(radio_value, year);
 });

function display_main_panel(radio_value, year){
    //By default all hiddable panels are hidden
    $('#pnl_national_education_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_national_detail_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_foreign_education_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_local_university_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_local_high_education_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_domain_no_university_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_foreign_no_university_institution_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_domain_university_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_university_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_activity_detail_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_onem_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_diploma_foreign_files_'+year).css('visibility', 'hidden').css('display','none');
    //for all
    $('#rdb_path_type_local_university_'+year).prop( "checked", false);
    $('#rdb_path_type_foreign_university_'+year).prop( "checked", false);
    $('#rdb_path_type_local_high_non_university_'+year).prop( "checked", false);
    $('#rdb_path_type_high_foreign_non_university_'+year).prop( "checked", false);
    $('#rdb_path_type_other_'+year).prop( "checked", false);
    // LOCAL_UNIVERSITY
    $('#rdb_national_education_french_'+year).prop( "checked", false);
    $('#rdb_national_education_dutch_'+year).prop( "checked", false);
    $('#pnl_universtity_'+year).css('visibility', 'hidden').css('display','none');
    $('#slt_french_universities_'+year).css('visibility', 'hidden');
    $('#slt_french_universities_'+year).css('display','none');
    $('#slt_french_universities_'+year).prop("selectedIndex",-1);
    $('#slt_dutch_universities_'+year).css('visibility', 'hidden');
    $('#slt_dutch_universities_'+year).css('display','none');
    $('#slt_dutch_universities_'+year).prop("selectedIndex",-1);
    $('#rdb_corresponds_to_domain_true_'+year).prop( "checked", false);
    $('#rdb_corresponds_to_domain_false_'+year).prop( "checked", false);
    $('#txt_diploma_title_'+year).prop( "disabled", true);
    $('#rdb_diploma_true_'+year).prop( "checked", false);
    $('#rdb_diploma_false_'+year).prop( "checked", false);
    $('#rdb_result_succeed_'+year).prop( "checked", false);
    $('#rdb_result_failed_'+year).prop( "checked", false);
    $('#rdb_no_result_'+year).prop( "checked", false);
    $('#lbl_obtained_result_'+year).css('visibility', 'hidden');
    $('#lbl_obtained_result_'+year).css('display','none');

    // LOCAL_HIGH_EDUCATION
    $('#slt_national_high_non_university_institution_city_'+year).prop("selectedIndex",-1);
    $('#slt_national_high_non_university_institution_'+year).prop("selectedIndex",-1);
    $('#chb_other_school_'+year).prop( "checked", false);
    $('#txt_other_high_non_university_name_'+year).val('');
    $('#txt_other_high_non_university_name_'+year).prop( "disabled", true);
    $('#slt_domain_non_university_'+year).prop("selectedIndex",-1);
    $('#slt_grade_type_no_university_'+year).prop("selectedIndex",-1);
    $('#rdb_study_systems_undefined_'+year).prop( "checked", false);
    $('#rdb_study_systems_social_advancement_'+year).prop( "checked", false);
    $('#rdb_study_systems_full_exercise_'+year).prop( "checked", false);
    //FOREIGN_UNIVERSITY
    $('#slt_foreign_institution_country_'+year).prop("selectedIndex",-1);
    $('#slt_cities_'+year).prop("selectedIndex",-1);
    $('#slt_foreign_university_name_'+year).prop("selectedIndex",-1);
    $('#chb_national_institution_locality_adhoc_'+year).prop( "checked", false);
    $('#chb_national_institution_name_adhoc_'+year).prop( "checked", false);
    $('#txt_city_specify_'+year).val('');
    $('#txt_name_specify_'+year).val('');
    $('#txt_city_specify_'+year).prop( "disabled", true);
    $('#txt_name_specify_'+year).prop( "disabled", true);
    $('#slt_domain_foreign_'+year).prop("selectedIndex",-1);
    $('#slt_subdomain_foreign_'+year).prop("selectedIndex",-1);
    $('#slt_subdomain_foreign_'+year).prop( "disabled", true);
    $('#slt_grade_type_foreign_'+year).prop("selectedIndex",-1);
    $('#slt_linguistic_regime_'+year).prop("selectedIndex",-1);
    $('#rdb_corresponds_to_domain_foreign_true_'+year).prop( "checked", false);
    $('#rdb_corresponds_to_domain_foreign_false_'+year).prop( "checked", false);
    $('#txt_diploma_title_foreign_'+year).prop( "disabled", true);
    $('#rdb_diploma_foreign_true_'+year).prop( "checked", false);
    $('#rdb_diploma_foreign_false_'+year).prop( "checked", false);
    $('#rdb_result_foreign_succeed_'+year).prop( "checked", false);
    $('#rdb_result_foreign_failed_'+year).prop( "checked", false);
    $('#rdb_no_result_foreign_'+year).prop( "checked", false);
    $('#lbl_obtained_result_foreign_'+year).css('visibility', 'hidden').css('display','none');
    $('#txt_credits_enrolled_foreign_'+year).val('');
    $('#txt_credits_obtained_foreign_'+year).val('');
    $('#pnl_translation_'+year).css('visibility', 'hidden').css('display','none');
    //FOREIGN_HIGH_EDUCATION
    $('#slt_foreign_high_institution_country_'+year).prop("selectedIndex",-1);
    $('#slt_cities_high_'+year).prop("selectedIndex",-1);
    $('#slt_foreign_high_name_'+year).prop("selectedIndex",-1);
    $('#chb_foreign_institution_locality_adhoc_'+year).prop( "checked", false);
    $('#chb_foreign_institution_name_adhoc_'+year).prop( "checked", false);
    $('#txt_foreing_city_specify_'+year).val('');
    $('#txt_foreign_name_specify_'+year).val('');
    $('#txt_foreing_city_specify_'+year).prop( "disabled", true);
    $('#txt_foreign_name_specify_'+year).prop( "disabled", true);
    // OTHER
    $('#pnl_other_'+year).css('visibility', 'hidden').css('display','none');
    $('#rdb_activity_type_job_'+year).prop( "checked", false);
    $('#rdb_activity_type_internship_'+year).prop( "checked", false);
    $('#rdb_activity_type_volunteering_'+year).prop( "checked", false);
    $('#rdb_activity_type_unemployment_'+year).prop( "checked", false);
    $('#rdb_activity_type_illness_'+year).prop( "checked", false);

    if (radio_value=='LOCAL_UNIVERSITY' || radio_value=='LOCAL_HIGH_EDUCATION'   ){
        $('#pnl_national_education_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_national_detail_'+year).css('visibility', 'visible').css('display','block');
    }

    if (radio_value=='LOCAL_UNIVERSITY'){
        $('#rdb_path_type_local_university_'+year).prop( "checked", true);
        $('#pnl_local_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_university_'+year).css('visibility', 'hidden').css('display','none');

    }
    if (radio_value=='FOREIGN_UNIVERSITY'){
        $('#rdb_path_type_foreign_university_'+year).prop( "checked", true);
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_foreign_education_'+year).css('visibility', 'visible').css('display','block');
        if($('#hdn_original_language_recognized_'+year).val()=='True'){
            $('#pnl_translation_'+year).css('visibility', 'visible').css('display','block');
        }
    }
    if (radio_value=='LOCAL_HIGH_EDUCATION'){
        $('#rdb_path_type_local_high_non_university_'+year).prop( "checked", true);
        $('#pnl_local_high_education_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_domain_no_university_'+year).css('visibility', 'visible').css('display','block');
    }
    if (radio_value=='FOREIGN_HIGH_EDUCATION'){
        $('#rdb_path_type_high_foreign_non_university_'+year).prop( "checked", true);
        $('#pnl_foreign_no_university_institution_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_foreign_education_'+year).css('visibility', 'visible').css('display','block');
    }

    if (radio_value=='ANOTHER_ACTIVITY'){
        $('#rdb_path_type_other_'+year).prop( "checked", true);
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_other_'+year).css('visibility', 'visible').css('display','block');
        if($('#hdn_original_activity_type_'+year).val() == 'JOB'){
            $('#rdb_activity_type_job_'+year).prop( "checked", true);
        }
        if($('#hdn_original_activity_type_'+year).val() == 'INTERNSHIP'){
            $('#rdb_activity_type_internship_'+year).prop( "checked", true);
        }
        if($('#hdn_original_activity_type_'+year).val() == 'VOLUNTEERING'){
            $('#rdb_activity_type_volunteering_'+year).prop( "checked", true);
        }
        if($('#hdn_original_activity_type_'+year).val() == 'UNEMPLOYMENT'){
            $('#rdb_activity_type_unemployment_'+year).prop( "checked", true);
        }
        if($('#hdn_original_activity_type_'+year).val() == 'ILLNESS'){
            $('#rdb_activity_type_illness_'+year).prop( "checked", true);
        }
        activity_display(year, $('#hdn_original_activity_type_'+year).val());

    }
    if (radio_value == 'LOCAL_UNIVERSITY' || radio_value == 'LOCAL_HIGH_EDUCATION'){
        if($('#hdn_original_national_education_'+year).val() == 'FRENCH'){
            $('#rdb_national_education_french_'+year).prop( "checked", true);
        }else{
            if($('#hdn_original_national_education_'+year).val() == 'DUTCH'){
                $('#rdb_national_education_dutch_'+year).prop( "checked", true);
            }
        }
        if (radio_value == 'LOCAL_UNIVERSITY' ){
            display_belgian_universities($('#hdn_original_national_education_'+year).val(),year)
            display_domain_subdomain_grade(year)
            populate_slt_subdomains('slt_domain_'+year,
                                    'slt_subdomain_'+year,
                                    $('#hdn_original_domain_id_'+year).val(),
                                    $('#hdn_original_sub_domain_id_'+year).val());

        }else{
            if (radio_value == 'LOCAL_HIGH_EDUCATION' ){
                populate_institution_city($('#hdn_original_national_institution_id_'+year).val(),
                                     $('#hdn_original_national_institution_city_'+year).val(),
                                     'slt_national_high_non_university_institution_city_'+year,
                                     'slt_national_high_non_university_institution_'+year)
                if($('#hdn_original_national_institution_adhoc_'+year).val() == 'True'){
                    $('#chb_other_school_'+year).prop( "checked", true);
                    $('#txt_other_high_non_university_name_'+year).prop( "disabled", false);
                    $('#txt_other_high_non_university_name_'+year).val($('#hdn_original_national_institution_name_'+year).val());
                    $('#slt_national_high_non_university_institution_city_'+year).prop( "disabled", true);
                    $('#slt_national_high_non_university_institution_'+year).prop( "disabled", true);
                }else{
                    $('#txt_other_high_non_university_name_'+year).prop( "disabled", true);
                    if($('#hdn_original_national_institution_id_'+year).val() != 'None'){
                        $('#slt_national_high_non_university_institution_city_'+year+' option').each(function(){
                            if($(this).attr('value')==$('#hdn_original_national_institution_city_'+year).val()){
                                $(this).prop('selected', true);
                            }
                        });
                        $('#slt_national_high_non_university_institution_'+year+' option').each(function(){
                            if($(this).attr('value')==$('#hdn_original_national_institution_id_'+year).val()){
                                $(this).prop('selected', true);
                            }
                        });

                    }

                }
                if($('#hdn_original_domain_id_'+year).val() != 'None'){
                    $('#slt_domain_non_university_'+year+' option').each(function(){
                        if($(this).attr('value')==$('#hdn_original_domain_id_'+year).val()){
                            $(this).prop('selected', true);
                        }
                    });
                }

                if($('#hdn_original_grade_type_no_university_'+year).val() != 'None'){
                    $('#slt_grade_type_no_university_'+year+' option').each(function(){
                        if($(this).attr('value')==$('#hdn_original_grade_type_no_university_'+year).val()){
                            $(this).prop('selected', true);
                        }
                    });
                }

                if($('#hdn_original_study_system_'+year).val() == 'SOCIAL_ADVANCEMENT'){
                    $('#rdb_study_systems_social_advancement_'+year).prop( "checked", true);
                }else{
                    if($('#hdn_original_study_system_'+year).val() == 'FULL_EXERCISE'){
                        $('#rdb_study_systems_social_advancement_'+year).prop( "checked", true);
                    }else{
                        $('#rdb_study_systems_undefined_'+year).prop( "checked", true);
                    }
                }

            }

        }

        if($('#hdn_original_diploma_title_'+year).val() == ''){
            $('#rdb_corresponds_to_domain_true_'+year).prop( "checked", true);
            $('#txt_diploma_title_'+year).prop( "disabled", true);
        }else{
            $('#rdb_corresponds_to_domain_false_'+year).prop( "checked", true);
            $('#txt_diploma_title_'+year).prop( "disabled", false);
        }

        if($('#hdn_original_diploma_'+year).val() == 'True'){
            $('#rdb_diploma_true_'+year).prop( "checked", true);
            $('#pnl_diploma_files_'+year).css('visibility', 'visible').css('display','block');
            if($('#hdn_original_academic_year_'+year).val()>="2014"){
                $('#lbl_obtained_result_'+year).css('visibility', 'visible').css('display','block');
            }
        }else{
            $('#rdb_diploma_false_'+year).prop( "checked", true);
             $('#pnl_diploma_files_'+year).css('visibility', 'hidden').css('display','none');
             if($('#hdn_original_academic_year_'+year).val()<"2014"){
                $('#lbl_obtained_result_'+year).css('visibility', 'visible').css('display','block');
            }
        }
        if($('#hdn_original_result_'+year).val() == 'SUCCEED'){
            $('#rdb_result_succeed_'+year).prop( "checked", true);
        }
        if($('#hdn_original_result_'+year).val() == 'FAILED'){
            $('#rdb_result_failed_'+year).prop( "checked", true);
        }
        if($('#hdn_original_result_'+year).val() == 'NO_RESULT'){
            $('#rdb_no_result_'+year).prop( "checked", true);
        }

    }

    if (radio_value=='FOREIGN_UNIVERSITY' || radio_value=='FOREIGN_HIGH_EDUCATION'){
        if($('#hdn_original_diploma_'+year).val() == 'True'){
            $('#pnl_diploma_foreign_files_'+year).css('visibility', 'visible').css('display','block');
        }
        if (radio_value=='FOREIGN_UNIVERSITY' ){
            if($('#hdn_original_national_institution_adhoc_'+year).val() == 'True'){
                $('#chb_national_institution_locality_adhoc_'+year).prop( "checked", true);
                $('#chb_national_institution_name_adhoc_'+year).prop( "checked", true);
                $('#txt_city_specify_'+year).prop( "disabled", false);
                $('#txt_name_specify_'+year).prop( "disabled", false);
                $('#slt_foreign_institution_country_'+year).prop( "disabled", true);
                $('#slt_cities_'+year).prop( "disabled", true);
                $('#slt_foreign_university_name_'+year).prop( "disabled", true);
            }else{

                if($('#hdn_original_national_institution_country_id_'+year).val() != 'None'){
                    populate_slt_foreign_university('slt_foreign_institution_country_'+year, $('#hdn_original_national_institution_country_id_'+year).val(), year, $('#hdn_original_national_institution_city_'+year).val(),$('#hdn_original_national_institution_id_'+year).val());
                }

            }
        }else{
            if(radio_value=='FOREIGN_HIGH_EDUCATION'){
                if($('#hdn_original_national_institution_adhoc_'+year).val() == 'True'){
                    $('#chb_foreign_institution_locality_adhoc_'+year).prop( "checked", true);
                    $('#chb_foreign_institution_name_adhoc_'+year).prop( "checked", true);
                    $('#txt_foreing_city_specify_'+year).prop( "disabled", false);
                    $('#txt_foreign_name_specify_'+year).prop( "disabled", false);
                    $('#slt_foreign_high_institution_country_'+year).prop( "disabled", true);
                    $('#slt_cities_high_'+year).prop( "disabled", true);
                    $('#slt_foreign_high_name_'+year).prop( "disabled", true);
                }else{

                    if($('#hdn_original_national_institution_country_id_'+year).val() != 'None'){
                        populate_slt_foreign_high_institution('slt_foreign_high_institution_country_'+year,
                                                              $('#hdn_original_national_institution_country_id_'+year).val(),
                                                              year,
                                                              $('#hdn_original_national_institution_city_'+year).val(),
                                                              $('#hdn_original_national_institution_id_'+year).val());
                    }
                }
            }
        }
        if($('#hdn_original_domain_id_'+year).val() != 'None'){
            $('#slt_domain_foreign_'+year+' option').each(function(){
                if($(this).attr('value')==$('#hdn_original_domain_id_'+year).val()){
                    $(this).prop('selected', true);
                }
            });
        }
        if($('#hdn_original_sub_domain_id_'+year).val() != 'None'){
            $('#slt_subdomain_foreign_'+year+' option').each(function(){
                if($(this).attr('value')==$('#hdn_original_sub_domain_id_'+year).val()){
                    $(this).prop('selected', true);
                    $('#slt_subdomain_foreign_'+year).prop( "disabled", false);
                }
            });
        }else{
            $('#slt_subdomain_foreign_'+year).prop( "disabled", true);
        }

        if($('#hdn_original_grade_type_id_'+year).val() != 'None'){
            $('#slt_grade_type_foreign_'+year+' option').each(function(){
                if($(this).attr('value')==$('#hdn_original_grade_type_id_'+year).val()){
                    $(this).prop('selected', true);
                }
            });
        }
        if($('#hdn_original_language_id_'+year).val() != 'None'){
            $('#slt_linguistic_regime_'+year+' option').each(function(){
                if($(this).attr('value')==$('#hdn_original_language_id_'+year).val()){
                    $(this).prop('selected', true);
                }
            });
        }

        if($('#hdn_original_diploma_title_'+year).val() == ''){
            $('#rdb_corresponds_to_domain_foreign_true_'+year).prop( "checked", true);
            $('#txt_diploma_title_'+year).prop( "disabled", true);
        }else{
            $('#rdb_corresponds_to_domain_foreign_false_'+year).prop( "checked", true);
            $('#txt_diploma_title_'+year).prop( "disabled", false);
        }

        if($('#hdn_original_diploma_'+year).val() == 'True'){
            $('#rdb_diploma_foreign_true_'+year).prop( "checked", true);
            $('#pnl_diploma_files_'+year).css('visibility', 'visible').css('display','block');
            if($('#hdn_original_academic_year_'+year).val()>="2014"){
                $('#lbl_obtained_result_foreign_'+year).css('visibility', 'visible').css('display','block');
            }
        }else{
            $('#rdb_diploma_foreign_false_'+year).prop( "checked", true);

             if($('#hdn_original_academic_year_'+year).val()<"2014"){
                $('#lbl_obtained_result_'+year).css('visibility', 'visible').css('display','block');
            }
        }
        if($('#hdn_original_result_'+year).val() == 'SUCCEED'){
            $('#rdb_result_foreign_succeed_'+year).prop( "checked", true);
        }
        if($('#hdn_original_result_'+year).val() == 'FAILED'){
            $('#rdb_result_foreign_failed_'+year).prop( "checked", true);
        }
        if($('#hdn_original_result_'+year).val() == 'NO_RESULT'){
            $('#rdb_no_result_foreign_'+year).prop( "checked", true);
        }

        if($('#hdn_original_credits_enrolled_'+year).val() != ''){
            $('#txt_credits_enrolled_foreign_'+year).val($('#hdn_original_credits_enrolled_'+year).val());
        }
        if($('#hdn_original_credits_obtained_'+year).val() != ''){
            $('#txt_credits_obtained_foreign_'+year).val($('#hdn_original_credits_obtained_'+year).val());
        }

    }
}

function display_belgian_universities(radio_value, year){
    if(radio_value == 'FRENCH'){
        $('#pnl_national_detail_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_universtity_'+year).css('visibility', 'visible').css('display','block');
        $('#slt_french_universities_'+year).css('visibility', 'visible');
        $('#slt_french_universities_'+year).css('display','block');
        $('#slt_dutch_universities_'+year).css('visibility', 'hidden');
        $('#slt_dutch_universities_'+year).css('display','none');
        if($('#hdn_original_national_institution_id_'+year).val()){
            $('#slt_french_universities_'+year + ' option[value='+$('#hdn_original_national_institution_id_'+year).val()+']').attr('selected','selected');
        }
    }else{
        if(radio_value == 'DUTCH'){
            $('#pnl_national_detail_'+year).css('visibility', 'visible').css('display','block');
            $('#pnl_universtity_'+year).css('visibility', 'visible').css('display','block');
            $('#slt_french_universities_'+year).css('visibility', 'hidden').css('display','none');
            $('#slt_dutch_universities_'+year).css('visibility', 'visible').css('display','block');
            if($('#hdn_original_national_institution_id_'+year).val()){
                $('#slt_dutch_universities_'+year + ' option[value='+$('#hdn_original_national_institution_id_'+year).val()+']').attr('selected','selected');
            }
        }
    }
}

function display_domain_subdomain_grade(year){
    if($('#hdn_original_domain_id_'+year).val()){
        $('#slt_domain_'+year + ' option[value='+$('#hdn_original_domain_id_'+year).val()+']').attr('selected','selected');
    }
    if($('#hdn_original_sub_domain_id_'+year).val()){
        $('#slt_subdomain_'+year + ' option[value=\''+$('#hdn_original_sub_domain_id_'+year).val()+'\']').attr('selected','selected');
    }
    if ($('#hdn_original_grade_type_id_'+year).val()){
        $('#slt_grade_type_'+year + ' option[value='+$('#hdn_original_grade_type_id_'+year).val()+']').attr('selected','selected');
    }

}

$('document').ready(function(){
    var year_min = 9999;
    var year_max = 0;
    //To hide previous message "data duplicated"
    var elts = document.getElementsByTagName("input");
    for (var i = 0; i < elts.length; i++) {
        if(elts[i].name.indexOf('original_academic_year_') > -1){
            year = elts[i].name.replace('original_academic_year_','');
            if (year < year_min){
                year_min = year;
            }
            if (year > year_max){
                year_max = year;
            }
        }
    }
    year = year_min;
    first_year = year;
    var cpt = 0;
    while(year <= year_max){
        var elt = document.getElementById('hdn_original_path_type_'+year);
        display_main_panel(elt.value, year);
        if ($('#hdn_pnl_other_error_'+year).val()=='True'){
            $('#pnl_other_'+year).css('visibility', 'visible').css('display','block');
            $('#pnl_detail_'+year).css('visibility', 'visible').css('display','block');
        }

        year = parseInt(year) +1;
        cpt = cpt+1;
    }
    if(cpt==1){
        $('#pnl_detail_'+first_year).css('visibility', 'visible').css('display','block');
    }

});

function populate_slt_subdomains(id_domain, id_subdomain, domain_id, subdomain_id){
    $("#"+id_subdomain).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/subdomains?domain="+domain_id
      }).then(function(data) {
          if(data.length >0){
            $("#"+id_subdomain).prop('disabled', false);
            $("<option></option>").attr("value","-").append("-").appendTo("#"+id_subdomain);
            $.each(data, function(key, value) {

                if( value.id == subdomain_id){
                    $("<option></option>").attr("value",value.id).prop('selected', true).append(value.name).appendTo("#"+id_subdomain);
                }else{
                    $("<option></option>").attr("value",value.id).append(value.name).appendTo("#"+id_subdomain);
                }
            });
          }else{
            $("#"+id_subdomain).prop('disabled', true);
          }

      });
}

function populate_slt_foreign_university(id, country_id, year,city, name){
    $("#"+id).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/countries"
      }).then(function(data) {
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#"+id);
            $.each(data, function(key, value) {
                if(value.country_id == country_id){
                    $("<option></option>").attr("value",value.country_id).prop('selected', true).append(value.country_name).appendTo("#"+id);
                }else{
                    $("<option></option>").attr("value",value.country_id).append(value.country_name).appendTo("#"+id);
                }
            });
          }

      });
    $.ajax({
        url: "/admission/cities?country="+country_id
      }).then(function(data) {
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities_"+year);
            $.each(data, function(key, value) {
                if(value.city == city){
                    $("<option></option>").attr("value",value.city).prop('selected', true).append(value.city).appendTo("#slt_cities_"+year);
                }else{
                    $("<option></option>").attr("value",value.city).append(value.city).appendTo("#slt_cities_"+year);
                }
            });
          }

      });
    $.ajax({
        url: "/admission/universities?city="+city
      }).then(function(data) {
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities_"+year);
            $.each(data, function(key, value) {
                if(value.name == name){
                    $("<option></option>").attr("value",value.id).prop('selected', true).append(value.name).appendTo("#slt_foreign_university_name_"+year);
                }else{
                    $("<option></option>").attr("value",value.id).append(value.name).appendTo("#slt_foreign_university_name_"+year);
                }
            });
          }

      });
}

function populate_slt_foreign_high_institution(id, country_id, year,city, education_institution_id){
    $("#"+id).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/high_countries"
      }).then(function(data) {
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#"+id);
            $.each(data, function(key, value) {
                if(value.country_id == country_id){
                    $("<option></option>").attr("value",value.country_id).prop('selected', true).append(value.country_name).appendTo("#"+id);
                }else{
                    $("<option></option>").attr("value",value.country_id).append(value.country_name).appendTo("#"+id);
                }
            });
          }

      });
    $.ajax({
        url: "/admission/high_cities?country="+country_id
      }).then(function(data) {
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_cities_high_"+year);
            $.each(data, function(key, value) {
                if(value.city == city){
                    $("<option></option>").attr("value",value.city).prop('selected', true).append(value.city).appendTo("#slt_cities_high_"+year);
                }else{
                    $("<option></option>").attr("value",value.city).append(value.city).appendTo("#slt_cities_high_"+year);
                }
            });
          }

      });
    $.ajax({
        url: "/admission/high_institutions?city="+city
      }).then(function(data) {
          if(data.length >0){
            $("<option></option>").attr("value","-").append("-").appendTo("#slt_foreign_high_name_"+year);
            $.each(data, function(key, value) {
                if(value.id == education_institution_id){
                    $("<option></option>").attr("value",value.id).prop('selected', true).append(value.name).appendTo("#slt_foreign_high_name_"+year);
                }else{
                    $("<option></option>").attr("value",value.id).append(value.name).appendTo("#slt_foreign_high_name_"+year);
                }
            });
          }

      });
}

$("input[name^='activity_type_']").change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    var name = target.attr("name");

    year = name.replace('activity_type_','');

    var radio_value = target.val();
    activity_display(year, radio_value);

    $.ajax({
        url: "/admission/errors_update"
      })
});

function activity_display(year,radio_value) {
    $('#pnl_activity_detail_'+year).css('visibility', 'hidden').css('display','none');
    $('#pnl_onem_'+year).css('visibility', 'hidden').css('display','none');
    if(radio_value == 'JOB' || radio_value == 'INTERNSHIP' || radio_value == 'VOLUNTEERING' ){
        $('#pnl_activity_detail_'+year).css('visibility', 'visible').css('display','block');
        $('#txt_activity_'+year).val($('#hdn_original_activity_'+year).val());
        $('#txt_activity_place_'+year).val($('#hdn_original_activity_place_'+year).val());
    }else{
        var current_year = parseInt($('#hdn_current_academic_year').val());
        if (parseInt(year) >= (current_year-5) && radio_value == 'UNEMPLOYMENT'){
            $('#pnl_onem_'+year).css('visibility', 'visible').css('display','block');
        }
    }
}

$("select[id^='slt_domain_']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    year = id.replace('slt_domain_','');

    populate_slt_subdomains(id, 'slt_subdomain_'+year, target.val(), '')
});

function populate_institution_city(national_institution_id, city_name, slt_city_id, slt_institution_id){
    $("#"+slt_city_id).find("option")
        .remove()
       .end();
    if(city_name==''){
        city_name = "-"
    }
    $.ajax({
        url: "/admission/highnonuniversity_cities"
      }).then(function(data) {
          if(data.length >0){
          $("<option></option>").attr("value","-").append("-").appendTo("#"+slt_city_id);
            $.each(data, function(key, value) {
                if(value.city == city_name){
                    $("<option></option>").attr("value",value.city).prop('selected', true).append(value.city).appendTo("#"+slt_city_id);

                }else{
                    $("<option></option>").attr("value",value.city).append(value.city).appendTo("#"+slt_city_id);
                }
            });
          }

      });
    if(national_institution_id != ''){
        populate_institution($("#hdn_original_national_institution_id_"+year).val(),
                             city_name,
                             'slt_national_high_non_university_institution_city_'+year,
                             'slt_national_high_non_university_institution_'+year)
    }

}

function populate_institution(national_institution_id, city_name, slt_city_id, slt_institution_id){

    $("#"+slt_institution_id).find("option")
        .remove()
       .end();

    if(city_name==''){
        city_name = "-"
    }
        $.ajax({
            url: "/admission/highnonuniversity?city=" + city_name
          }).then(function(data) {
              if(data.length >0){
              $("<option></option>").attr("value","-").append("-").appendTo("#"+slt_institution_id);
                $.each(data, function(key, value) {
                    if(value.id == national_institution_id){
                        $("<option></option>").attr("value",value.id).prop('selected', true).append(value.name).appendTo("#"+slt_institution_id);

                    }else{
                        $("<option></option>").attr("value",value.id).append(value.name).appendTo("#"+slt_institution_id);
                    }
                });
              }

          });


}

function reset_slt(id){
    document.getElementById(id).selectedIndex = -1;

}

function refresh_pnl_subdomain_foreign(domain, year){
    var sel = domain.options[domain.selectedIndex].text;
    var elt = document.getElementById('slt_subdomain_foreign_'+year);
    var cpt = 0;
    document.getElementById('slt_subdomain_foreign_'+year).selectedIndex = -1;
    for(var i = 0 ,l = elt.options.length; i< l;i++ ){
        if(i==0){
            elt.options[i].style="visibility:visible;display:block";
        }else{
            if (sel != "-"){
                if((elt.options[i].title).indexOf(sel) > -1){
                    elt.options[i].style="visibility:visible;display:block";
                    cpt = cpt + 1;
                }else{
                    elt.options[i].style="visibility:hidden;display:none";
                }
            }else{
                elt.options[i].style="visibility:visible;display:block";
            }
        }
    }
    if(cpt == 0){
        document.getElementById('slt_subdomain_foreign_'+year).disabled = true;
        document.getElementById('lbl_subdomain_mandatory_foreign_'+year).style="visibility:hidden;display:none";
    }else{
        document.getElementById('slt_subdomain_foreign_'+year).disabled = false;
        document.getElementById('lbl_subdomain_mandatory_foreign_'+year).style="visibility:visible;display:block";
    }
}

// to check disabled status after duplicate
var elts = document.getElementsByTagName("select");
for (var i = 0; i < elts.length; i++) {
    if(elts[i].id.indexOf('slt_subdomain_') > -1){
        if(elts[i].value == ""){
            elts[i].disabled = true;
        }else{
            elts[i].disabled = false;
        }
    }
}

$.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});

function reset_chb(elt_name){
    x=document.getElementsByName(elt_name);
    var i;
    for (i = 0; i < x.length; i++) {
        if (x[i].type == "checkbox") {
            x[i].checked = false;
        }
    }
}

function display_dynamic_form(offer_year_id){
    set_pnl_questions_empty();
    $.ajax({
        url: "/admission/options?offer=" + offer_year_id
    }).then(function(data){
          var table_size=data.length;
          if(data.length >0){
            $.each(data, function(key, value){
                if(value.question_type=='LABEL'){
                    $('#pnl_questions').append($("<label></label>")
                                       .append(value.question_label));
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append("<br>");
                }
                if(value.question_type=='SHORT_INPUT_TEXT'){
                    $('#pnl_questions').append($("<label></label>")
                                       .append(value.question_label)
                                       .attr("id","lbl_question_"+value.option_id));
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append($("<input>")
                                       .attr("class", "form-control")
                                       .attr("name","txt_answer_question_"+value.option_id)
                                       .attr("id","txt_answer_question_"+value.option_id)
                                       .attr("placeholder", value.option_label)
                                       .attr("title",value.option_description)
                                       .attr("value",value.answer)
                                       .prop("required",value.question_required));
                    if(value.question_description != ""){
                        $('#pnl_questions').append($("<label></label>")
                                           .append(value.question_description)
                                           .attr("id","lbl_question_description_"+value.option_id)
                                           .attr("class","description"));
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append("<br>");
                    }
                }
                if(value.question_type=='LONG_INPUT_TEXT'){
                    $('#pnl_questions').append($("<label></label>")
                                       .append(value.question_label)
                                       .attr("id","lbl_question_"+value.option_id));
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append($("<textarea></textarea>")
                                       .attr("class", "form-control")
                                       .attr("name","txt_answer_question_"+value.option_id)
                                       .attr("id","txt_answer_question_"+value.option_id)
                                       .attr("placeholder", value.option_label)
                                       .attr("title",value.option_description)
                                       .text(value.answer)
                                       .prop("required",value.question_required));
                    if(value.question_description != ""){
                        $('#pnl_questions').append($("<label></label>")
                                           .append(value.question_description)
                                           .attr("id","lbl_question_description_"+value.option_id)
                                           .attr("class","description"));
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append("<br>");
                    }
                }
                if(value.question_type=='RADIO_BUTTON'){
                    if(value.option_order == 1){
                        $('#pnl_questions').append($("<label></label>")
                                           .append(value.question_label)
                                           .attr("id","lbl_question_"+value.question_id));
                        $('#pnl_questions').append("<br>");
                        if(value.option_value == value.answer){
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .prop("checked", "checked")
                                               .attr("type","radio")
                                               .attr("value",value.option_id)
                                               .attr("name","txt_answer_radio_"+value.question_id)
                                               .attr("id","txt_answer_radio_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }else{
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .attr("type","radio")
                                               .attr("value",value.option_id)
                                               .attr("name","txt_answer_radio_"+value.question_id)
                                               .attr("id","txt_answer_radio_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }
                    }else{
                        if(value.option_value == value.answer){
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .prop("checked", "checked")
                                               .attr("type","radio")
                                               .attr("value",value.option_id)
                                               .attr("name","txt_answer_radio_"+value.question_id)
                                               .attr("id","txt_answer_radio_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }else{
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .attr("type","radio")
                                               .attr("value",value.option_id)
                                               .attr("name","txt_answer_radio_"+value.question_id)
                                               .attr("id","txt_answer_radio_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }
                    }
                    if(value.option_order == value.options_max_number && value.question_description != ""){
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                               .attr("id","lbl_question_description_"+value.option_id)
                                               .attr("class","description"));
                             $('#pnl_questions').append("<br>");
                             $('#pnl_questions').append("<br>");
                    }
                }
                if(value.question_type=='CHECKBOX'){
                    if(value.option_order == 1){
                        $('#pnl_questions').append($("<label></label>")
                                           .append(value.question_label)
                                           .attr("id","lbl_question_"+value.question_id));
                        $('#pnl_questions').append("<br>");
                        if(value.option_value == value.answer){
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .prop("checked", "checked")
                                               .attr("type","checkbox")
                                               .attr("name","txt_answer_checkbox_"+value.option_id)
                                               .attr("id","txt_answer_checkbox_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }else{
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .attr("type","checkbox")
                                               .attr("name","txt_answer_checkbox_"+value.option_id)
                                               .attr("id","txt_answer_checkbox_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }
                    }else{
                        if(value.option_value == value.answer){
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .prop("checked", "checked")
                                               .attr("type","checkbox")
                                               .attr("name","txt_answer_checkbox_"+value.option_id)
                                               .attr("id","txt_answer_checkbox_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }else{
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>")
                                               .append($("<input>")
                                               .attr("type","checkbox")
                                               .attr("name","txt_answer_checkbox_"+value.option_id)
                                               .attr("id","txt_answer_checkbox_"+value.option_id))
                                               .append("&nbsp;&nbsp;"+value.option_label)
                                               .prop("required",value.question_required));
                        }
                    }
                   if(value.option_order == value.options_max_number && value.question_description != ""){
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                           .attr("id","lbl_question_description_"+value.option_id)
                                           .attr("class","description"));
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append("<br>");
                   }
                }
                if(value.question_type=='DROPDOWN_LIST'){
                    if(value.option_order == 1){
                        $('#pnl_questions').append($("<label></label>")
                                           .append(value.question_label)
                                           .attr("id","lbl_question_"+value.question_id));
                        $('#pnl_questions').append("<br>");
                        if(value.option_value == value.answer){
                            $('#pnl_questions').append($("<select></select>")
                                               .attr("class", "form-control")
                                               .attr("name","slt_question_"+value.question_id)
                                               .attr("id","slt_question_"+value.question_id)
                                               .prop("required",value.question_required)
                                               .append($("<option></option")
                                               .attr('selected', 'selected')
                                               .attr("value",value.option_id)
                                               .append(value.option_value)));
                        }else{
                            $('#pnl_questions').append($("<select></select>")
                                               .attr("class", "form-control")
                                               .attr("name","slt_question_"+value.question_id)
                                               .attr("id","slt_question_"+value.question_id)
                                               .prop("required",value.question_required)
                                               .append($("<option></option")
                                               .attr("value",value.option_id)
                                               .append(value.option_value)));
                        }
                        if (value.question_description != ""){
                            $('#pnl_questions').append($("<label></label>")
                                               .append(value.question_description)
                                               .attr("id","lbl_question_description_"+value.option_id)
                                               .attr("class","description"));
                            $('#pnl_questions').append("<br>");
                        }
                    }else{
                        if(value.option_value == value.answer){
                            $('#slt_question_'+value.question_id).append($("<option></option")
                                                                 .attr('selected', 'selected')
                                                                 .attr("value",value.option_id)
                                                                 .append(value.option_value));
                        }else{
                            $('#slt_question_'+value.question_id).append($("<option></option")
                                                                 .attr("value",value.option_id)
                                                                 .append(value.option_value));
                        }
                    }
                }

            if(value.question_type=='DOWNLOAD_LINK'){
                $('#pnl_questions').append("<br>");
                $('#pnl_questions').append("<br>");
                $('#pnl_questions').append($("<label></label>").append(value.question_label)
                                                            .attr("id","lbl_question_"+value.question_id));
                $('#pnl_questions').append($("<a></a>").append("&nbsp;&nbsp;Cliquez ici pour obtenir le fichier")
                                                       .attr("id","lnk_question_"+value.option_id)
                                                       .attr("target","_blank")
                                                       .attr("href",value.option_value));
                if(value.question_description != ""){
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                                            .attr("id","lbl_question_description_"+value.option_id)
                                                            .attr("class","description"));
                }
            }
            if(value.question_type=='HTTP_LINK'){
                $('#pnl_questions').append("<br>");
                $('#pnl_questions').append("<br>");
                $('#pnl_questions').append($("<a></a>").append(value.option_value)
                                                       .attr("id","lnk_question_"+value.option_id)
                                                       .attr("target","_blank")
                                                       .attr("href",value.option_value));
                if(value.question_description != ""){
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                                            .attr("id","lbl_question_description_"+value.option_id)
                                                            .attr("class","description"));
                }
            }
        });
        }
      });
}
function ajax_grade_choice(grade_choice){

    $.ajax({
        url: "/admission/levels?type=" + $("#slt_offer_type").val()
      }).then(function(data) {

        if(data.length >0){
        $.each(data, function(key, value) {
            if(data.length == 1){
                $('#pnl_grade_choices').append($("<label></label>").attr("class", "radio-inline")
                                                                   .attr("style","visibility:hidden;display:none;")
                                                                   .append($("<input>").attr("type","radio")
                                                                      .attr("name","grade_choice")
                                                                      .attr("value",value.id )
                                                                      .attr("id","grade_choice_"+value.id)
                                                                      .attr("onchange","offer_selection_display()")
                                                                      .attr("style","visibility:hidden;display:none;")
                                                                      .attr("checked","checked"))
                                          .append(value.name));
                                          if(grade_choice==''){
                                            offer_selection_display();
                                          }

            }else{
                var chk='';

                if(grade_choice == value.id){
                  $('#pnl_grade_choices').append($("<label></label>").attr("class", "radio-inline")
                                              .append($("<input>").attr("type","radio")
                                                                          .attr("name","grade_choice")
                                                                          .attr("value",value.id )
                                                                          .attr("id","grade_choice_"+value.id)
                                                                          .attr("onchange","offer_selection_display()")
                                                                          .attr("style","visibility:visible;display:block;")
                                                                          .attr("checked","checked"))
                                              .append(value.name));

                }else{
                  $('#pnl_grade_choices').append($("<label></label>").attr("class", "radio-inline")
                                              .append($("<input>").attr("type","radio")
                                                                          .attr("name","grade_choice")
                                                                          .attr("value",value.id )
                                                                          .attr("id","grade_choice_"+value.id)
                                                                          .attr("onchange","offer_selection_display()")
                                                                          .attr("style","visibility:visible;display:block;"))
                                              .append(value.name));

                }
             }
        });
        }
      });
}

function ajax_offers(radio_button_value, offer_year_id){

    // Remove the offers
    $("#pnl_offers").find("table")
        .remove()
        .end()
    set_pnl_questions_empty();

    var i=0;
    $.ajax({
        url: "/admission/offers?level=" + $("#slt_offer_type").val() +"&domain="+$("#slt_domain").val()

      }).then(function(data) {
      var table_size=data.length;
      if(data.length >0){
        $('#pnl_grade_choices').append($("<table><tr><td></td></tr></table>"));
        var trHTML = '<table class="table table-striped table-hover">';
        trHTML += '<thead><th colspan=\'3\'><label>Cliquez sur votre choix d\'études</label></th></thead>';
        $.each(data, function(key, value) {
            id_str = "offer_row_" + i;

            onclick_str = "onclick=\'selection("+ i +", "+table_size+", " + value.id +")\'"
            var chk='';
            if (offer_year_id==''){

            }else{
                if(offer_year_id == value.id){
                    chk = ' checked=\'checked\' ';
                }
                $('#txt_offer_year_id').val(offer_year_id);
            }
            trHTML += "<tr id=\'" +  id_str + "\' "+ onclick_str +"><td><input type=\'radio\' name=\'offer_YearSel\' id=\'offer_sel_"+i+"\' "+chk+"></td><td>"+ value.acronym + "</td><td>" + value.title + "</td></tr>";
            i++;
        });
        trHTML += '</table>'
        $('#pnl_offers').append(trHTML);
        }
      });
}

function ajax_static_questions(offer_year_id, sameprogram, belgiandegree, samestudies) {
   $.ajax({
    url: "/admission/offer?offer=" + offer_year_id
   }).then(function(data) {

    init_static_questions();
//            alert(data.subject_to_quota);
//            alert(data.grade_type);
    if (data.subject_to_quota){

        $('#pnl_offer_sameprogram').css('visibility', 'visible').css('display','block');
        $('#pnl_offer_sameprogram').find('input').prop('required', true);

      }else{

        $('#pnl_offer_belgiandegree').css('visibility', 'visible').css('display','block');
        $('#pnl_offer_belgiandegree').find('input').prop('required', true);

        //// BACHELOR grade_type must have fixed values
        if (data.grade_type==1) {
            $('#pnl_offer_samestudies').css('visibility', 'visible').css('display','block');
            $('#pnl_offer_samestudies').find('input').prop('required', true);
        }
    }

    if(sameprogram=='True'){
        $('#rdb_offer_valuecredits_true').find('input').prop('checked', true);
        $('#rdb_offer_valuecredits_true').trigger('click');
    }else{
        if(sameprogram=='False'){
            $('#rdb_offer_valuecredits_false').find('input').prop('checked', false);
            $('#rdb_offer_valuecredits_false').trigger('click');
        }
    }
    if(belgiandegree=='True'){
        $('#rdb_offer_belgiandegree_true').attr('checked', 'checked');
        $('#rdb_offer_belgiandegree_true').trigger('click');

    }else{
        if(belgiandegree=='False'){
            $('#rdb_offer_belgiandegree_false').prop('checked', false);
            $('#rdb_offer_belgiandegree_false').trigger('click');
        }
    }

    if(samestudies=='True'){
        $('#rdb_offer_samestudies_true').find('input').prop('checked', true);
        $('#rdb_offer_samestudies_true').trigger('click');
    }else{
        if(sameprogram=='False'){
            $('#rdb_offer_samestudies_false').find('input').prop('checked', false);
            $('#rdb_offer_samestudies_false').trigger('click');
        }
    }

    });
}