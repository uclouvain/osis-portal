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
