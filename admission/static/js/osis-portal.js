$("#slt_offer_type").change(function() {

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

    document.getElementById("bt_save").disabled = true;
    var i=0;
    $.ajax({
        url: "/admission/levels?type=" + $("#slt_offer_type").val()
      }).then(function(data) {

        if(data.length >0){
        $.each(data, function(key, value) {

          $('#pnl_grade_choices').append($("<label></label>").attr("class", "radio-inline")
                                      .append($("<input>").attr("type","radio")
                                                                  .attr("name","grade_choice")
                                                                  .attr("value",value.id )
                                                                  .attr("id","grade_choice_"+value.id)
                                                                  .attr("onchange","offer_selection_display()"))
                                      .append(value.name));

        });
        }
      });

});


$("#slt_domain").change(function() {
    offer_selection_display();
});


function offer_selection_display(){
    var radio_button_value;

    if ($("input[name='grade_choice']:checked").length > 0){
       radio_button_value = $('input[name="grade_choice"]:checked').val();
    }
    else{
       return False
    }

    $("#pnl_offers").find("table")
      .remove()
      .end()
    set_pnl_questions_empty();
    //Cancel the previous selection
    document.getElementById("txt_offer_year_id").value = "";

    document.getElementById("bt_save").disabled = true;

    var i=0;
    $.ajax({
        url: "/admission/offers?level=" + radio_button_value +"&domain="+$("#slt_domain").val()

      }).then(function(data) {
      var table_size=data.length;
      if(data.length >0){
        $('#pnl_grade_choices').append($("<table><tr><td></td></tr></table>"));
        var trHTML = '<table class="table table-striped table-hover">';
        trHTML += '<thead><th colspan=\'3\'><label>Cliquez sur votre choix d\'études</label></th></thead>';
        $.each(data, function(key, value) {
            id_str = "offer_row_" + i;

            onclick_str = "onclick=\'selection("+ i +", "+table_size+", " + value.id +")\'"
            trHTML += "<tr id=\'" +  id_str + "\' "+ onclick_str +"><td><input type=\'radio\' name=\'offer_YearSel\' id=\'offer_sel_"+i+"\'></td><td>"+ value.acronym + "</td><td>" + value.title + "</td></tr>";
            i++;
        });
        trHTML += '</table>'
        $('#pnl_offers').append(trHTML);
        }
      });
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
        document.getElementById("bt_save").disabled = false;


        if(already_selected == true){
            document.getElementById(elt).style.color = "black";
            document.getElementById("txt_offer_year_id").value = "";
            document.getElementById("bt_save").disabled = true;
        }else{

            document.getElementById(elt).style.color = "green";
            document.getElementById("txt_offer_year_id").value = offer_year_id;
            document.getElementById("bt_save").disabled = false;
            document.getElementById("offer_sel_" + row_number).checked = true;
        }
        set_pnl_questions_empty();

        $.ajax({
            url: "/admission/options?offer=" + offer_year_id

        }).then(function(data) {
          var table_size=data.length;

          if(data.length >0){

            $.each(data, function(key, value) {
                if(value.question_type=='LABEL'){
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append($("<label></label>").attr("style", "color:red")
                    .append(value.option_label));
                }

                if(value.question_type=='SHORT_INPUT_TEXT'){
                    $('#pnl_questions').append($("<label></label>").append(value.question_label)
                                                                   .attr("id","lbl_question_"+value.option_id));
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append($("<input>").attr("class", "form-control")
                                            .attr("name","txt_answer_question_"+value.option_id)
                                            .attr("id","txt_answer_question_"+value.option_id)
                                            .attr("placeholder", value.option_label)
                                            .attr("title",value.option_description)
                                            .prop("required",value.question_required));
                    if(value.question_description != ""){
                        $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                                                .attr("id","lbl_question_description_"+value.option_id)
                                                                .attr("class","description"));
                    }
                }

                if(value.question_type=='LONG_INPUT_TEXT') {
                    $('#pnl_questions').append($("<label></label>").append(value.question_label)
                                                                   .attr("id","lbl_question_"+value.option_id));
                    $('#pnl_questions').append("<br>");
                    $('#pnl_questions').append($("<textarea></textarea>").attr("class", "form-control")
                                            .attr("name","txt_answer_question_"+value.option_id)
                                            .attr("id","txt_answer_question_"+value.option_id)
                                            .attr("placeholder", value.option_label)
                                            .attr("title",value.option_description)
                                            .prop("required",value.question_required));
                    if(value.question_description != ""){
                        $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                                                .attr("id","lbl_question_description_"+value.option_id)
                                                                .attr("class","description"));
                    }
                }

                if(value.question_type=='RADIO_BUTTON'){
                    var radio_checked = new Boolean(false)
                    if(value.option_order == 1){
                        radio_checked = new Boolean(true)
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append($("<label></label>").append(value.question_label)
                                                                .attr("id","lbl_question_"+value.question_id));

                        $('#pnl_questions').append("<br>");
                        if (value.question_required ){
                            $('#pnl_questions').append($("<label></label>")
                                  .append($("<input>").attr("type","radio")
                                                              .attr("name","txt_answer_radio_chck_optid_"+value.option_id)
                                                              .attr("id","txt_answer_radio_"+value.option_id)
                                                              .prop("required",value.question_required)
                                                              .prop("checked",radio_checked))
                                  .append("&nbsp;&nbsp;"+value.option_label));
                          }else{
                            $('#pnl_questions').append($("<label></label>")
                              .append($("<input>").attr("type","radio")
                                                          .attr("name","txt_answer_radio_chck_optid_"+value.option_id)
                                                          .attr("id","txt_answer_radio_"+value.option_id)
                                                          .prop("required",value.question_required))
                              .append("&nbsp;&nbsp;"+value.option_label));
                          }
                    }else{
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append($("<label></label>")
                              .append($("<input>").attr("type","radio")
                                                          .attr("name","txt_answer_radio_chck_optid_"+value.option_id)
                                                          .attr("id","txt_answer_radio_"+value.option_id)
                                                          .prop("required",value.question_required))
                              .append("&nbsp;&nbsp;"+value.option_label));
                    }
                    if(value.option_order == value.options_max_number && value.question_description != ""){
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                               .attr("id","lbl_question_description_"+value.option_id)
                                               .attr("class","description"));

                    }
                }

                if(value.question_type=='CHECKBOX'){

                    if(value.option_order == 1){
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append($("<label></label>").append(value.question_label)
                                                                .attr("id","lbl_question_"+value.question_id));

                        $('#pnl_questions').append("<br>");
                    }else{
                        $('#pnl_questions').append("<br>");
                    }

                    if(value.question_required){
                        $('#pnl_questions').append($("<label></label>")
                       .append($("<input>").attr("type","checkbox")
                                                  .attr("name","txt_answer_radio_chck_optid_"+value.option_id)
                                                  .attr("id","txt_answer_radio_chck_optid_req_"+value.option_id + "_q_"+ value.question_id))
                       .append("&nbsp;&nbsp;"+value.option_label));
                   }else{
                        $('#pnl_questions').append($("<label></label>")
                       .append($("<input>").attr("type","checkbox")
                                                  .attr("name","txt_answer_radio_chck_optid_"+value.option_id)
                                                  .attr("id","txt_answer_radio_chck_optid_"+value.option_id))
                       .append("&nbsp;&nbsp;"+value.option_label));
                    }
                    if(value.option_order == value.options_max_number && value.question_description != ""){
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>").append(value.question_description)
                                               .attr("id","lbl_question_description_"+value.option_id)
                                               .attr("class","description"));

                    }

                }
                if(value.question_type=='DROPDOWN_LIST'){
                    if(value.option_order == 1){
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append("<br>");
                        $('#pnl_questions').append($("<label></label>").append(value.question_label)
                                                                .attr("id","lbl_question_"+value.question_id));

                        $('#pnl_questions').append("<br>");
                        if(value.question_required){
                            $('#pnl_questions').append($("<select></select>")
                                .attr("name","slt_question_"+value.question_id)
                                .attr("id","slt_question_"+value.question_id)
                                .prop("required",value.question_required)
                                .append($("<option></option").attr("value",value.option_id).append(value.option_label)));
                        }else{
                            $('#pnl_questions').append($("<select></select>")
                                .attr("name","slt_question_"+value.question_id)
                                .attr("id","slt_question_"+value.question_id)
                                .append($("<option></option").attr("value",value.option_id).append(value.option_label)));
                        }
                        if (value.question_description != ""){
                            $('#pnl_questions').append("<br>");
                            $('#pnl_questions').append($("<label></label>").append(value.question_description)
                               .attr("id","lbl_question_description_"+value.option_id)
                               .attr("class","description"));
                        }

                    }else{
                        $('#slt_question_'+value.question_id).append($("<option></option").attr("value",value.option_id).append(value.option_label));
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

// AA : 25/04/16

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

$("input[name^='path_type__']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    year = id.replace('slt_national_institution_','');

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
    country = document.getElementById('slt_national_institution_'+year);

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

 $("select[id^='slt_linguistic_regime_']" ).change(function(event) {
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


    $("#slt_national_high_non_university_institution_"+year).find("option")
        .remove()
       .end();

    $.ajax({
        url: "/admission/highnonuniversity?city=" + target.val()
      }).then(function(data) {
          if(data.length >0){
          $("<option></option>").attr("value","-").append("-").appendTo("#slt_national_high_non_university_institution_"+year);
            $.each(data, function(key, value) {
                $("<option></option>").attr("value",value.id).append(value.name).appendTo("#slt_national_high_non_university_institution_"+year);
            });
          }

      });

 });


$("select[id^='slt_foreign_high_institution_']" ).change(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    if (typeof id == 'undefined') {
        target = target.parent();
        id = target.attr("id");
    }
    year = id.replace('slt_foreign_high_institution_','');

    $("#slt_cities_high_"+year).find("option")
        .remove()
       .end();

    $("#slt_foreign_university_name_"+year).find("option")
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
    display_main_panel(radio_value,year);
 });

$("input[name^='national_education_']").change(function(event) {
    alert('kkkk');
    var target = $(event.target);
    var name = target.attr("name");

    year = name.replace('national_education_','');

    var radio_value = target.val();
    display_belgian_universities(radio_value, year);
 });



function display_main_panel(radio_value, year){
    //alert('display_main_panel');
    //alert(radio_value);
    $('#rdb_national_education_french_'+year).prop( "checked", false );
    $('#rdb_national_education_dutch_'+year).prop( "checked", false );
    $('#slt_french_universities_'+year).css('visibility', 'hidden');
    $('#slt_french_universities_'+year).css('display','none');
    $('#slt_dutch_universities_'+year).css('visibility', 'hidden');
    $('#slt_dutch_universities_'+year).css('display','none');
    $('#rdb_corresponds_to_domain_true_'+year).prop( "checked", false );
    $('#rdb_corresponds_to_domain_false_'+year).prop( "checked", false );
    $('#txt_diploma_title_'+year).prop( "disabled", true );
    $('#rdb_diploma_true_'+year).prop( "checked", false );
    $('#rdb_diploma_false_'+year).prop( "checked", false );
    $('#rdb_result_succeed_'+year).prop( "checked", false );
    $('#rdb_result_failed_'+year).prop( "checked", false );
    $('#rdb_no_result_'+year).prop( "checked", false );

    if (radio_value=='LOCAL_UNIVERSITY' || radio_value=='LOCAL_HIGH_EDUCATION'   ){
        $('#pnl_national_education_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_national_detail_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_foreign_education_'+year).css('visibility', 'hidden').css('display','none');


    }else{
        $('#pnl_national_education_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_national_detail_'+year).css('visibility', 'hidden').css('display','hidden');
        $('#pnl_foreign_education_'+year).css('visibility', 'visible').css('display','block');
    }

    if (radio_value=='LOCAL_UNIVERSITY'){
        $('#pnl_local_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_local_high_education_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_domain_no_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_foreign_no_university_institution_'+year).css('visibility', 'hidden').css('display','none');


    }
    if (radio_value=='FOREIGN_UNIVERSITY'){
        $('#pnl_local_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_local_high_education_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_domain_no_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_university_'+year).css('visibility', 'visible').css('display','bloc');
        $('#pnl_foreign_no_university_institution_'+year).css('visibility', 'hidden').css('display','none');
    }
    if (radio_value=='LOCAL_HIGH_EDUCATION'){
        $('#pnl_local_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_local_high_education_'+year).css('visibility', 'visible').css('display','display');
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_domain_no_university_'+year).css('visibility', 'visible').css('display','display');
        $('#pnl_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_foreign_no_university_institution_'+year).css('visibility', 'hidden').css('display','none');
    }
    if (radio_value=='FOREIGN_HIGH_EDUCATION'){
        $('#pnl_local_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_local_high_education_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_domain_no_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_foreign_no_university_institution_'+year).css('visibility', 'visible').css('display','display');
    }

    if (radio_value=='ANOTHER_ACTIVITY'){
        $('#pnl_local_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_local_high_education_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_domain_university_'+year).css('visibility', 'visible').css('display','block');
        $('#pnl_domain_no_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_university_'+year).css('visibility', 'hidden').css('display','none');
        $('#pnl_foreign_no_university_institution_'+year).css('visibility', 'hidden').css('display','none');
    }
    if (radio_value == 'LOCAL_UNIVERSITY'){
        alert($('#hdn_original_national_education_'+year).val());
        if($('#hdn_original_national_education_'+year).val() == 'FRENCH'){
            $('#rdb_national_education_french_'+year).prop( "checked", true );
        }else{
            if($('#hdn_original_national_education_'+year).val() == 'DUTCH'){
                $('#rdb_national_education_dutch_'+year).prop( "checked", true );
            }
        }
        display_belgian_universities($('#hdn_original_national_education_'+year).val(),year)

        if($('#hdn_original_diploma_title_'+year).val() == ''){
            $('#rdb_corresponds_to_domain_true_'+year).prop( "checked", true );
            $('#txt_diploma_title_'+year).prop( "disabled", true );
        }else{
            $('#rdb_corresponds_to_domain_false_'+year).prop( "checked", true );
            $('#txt_diploma_title_'+year).prop( "disabled", false );
        }

        if($('#hdn_original_diploma_'+year).val() == 'True'){
            $('#rdb_diploma_true_'+year).prop( "checked", true );

        }else{
            $('#rdb_diploma_false_'+year).prop( "checked", true );
        }
        if($('#hdn_original_result_'+year).val() == 'SUCCEED'){
            $('#rdb_result_succeed_'+year).prop( "checked", true );
        }
        if($('#hdn_original_result_'+year).val() == 'FAILED'){
            $('#rdb_result_failed_'+year).prop( "checked", true );
        }
        if($('#hdn_original_result_'+year).val() == 'NO_RESULT'){
            $('#rdb_no_result_'+year).prop( "checked", true );
        }

    }
}

function display_belgian_universities(radio_value, year){
    //alert('display_belgian_universities');
    //alert(radio_value);
    //alert(year);
    if(radio_value == 'FRENCH'){
        $('#pnl_national_detail_'+year).css('visibility', 'visible').css('display','display');
        $('#slt_french_universities_'+year).css('visibility', 'visible');
        $('#slt_french_universities_'+year).css('display','');
        $('#slt_dutch_universities_'+year).css('visibility', 'hidden');
        $('#slt_dutch_universities_'+year).css('display','none');

        reset_slt('slt_dutch_universities_'+year);
    }else{
        if(radio_value == 'DUTCH'){
            $('#pnl_national_detail_'+year).css('visibility', 'visible').css('display','');
            $('#slt_french_universities_'+year).css('visibility', 'hidden').css('display','none');
            $('#slt_dutch_universities_'+year).css('visibility', 'visible').css('display','');
            reset_slt('slt_french_universities_'+year);
        }
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
    while(year <= year_max){

        var elt = document.getElementById('hdn_original_path_type_'+year);
        display_main_panel(elt.value, year);

        year = parseInt(year) +1;
    }


});
