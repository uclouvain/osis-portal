
    $(document).ready(function() {
        if($('#hdn_tab_active').val()=='2'){
            $('#form_secondary_education').append( $('#pnl_files>div') );
        }

       $.ajax({
           url: "/admission/country?nationality=" + $("#slt_nationality").val()
         }).then(function(data) {

            if (data.european_union) {
                  $('#pnl_assimilation_criteria').css('visibility', 'hidden').css('display','none');
            }else{
                  $('#pnl_assimilation_criteria').css('visibility', 'visible').css('display','block');
            }
         });

        $('#txt_admission_exam_date').val('');
        $('#txt_admission_exam_institution').val('');
        $('[id^="rdb_admission_exam_type_"]').prop( "checked", false);
        $('#txt_admission_exam_type_other').val('');
        $('#txt_admission_exam_type_other').prop( "disabled", true);
        $('#chb_admission_exam_type').prop( "checked", false);
        $('#rdb_admission_exam_result_low').prop( "checked", false);
        $('#rdb_admission_exam_result_middle').prop( "checked", false);
        $('#rdb_admission_exam_result_high').prop( "checked", false);
        populate_exam_admin();
        if($("#hdn_application_offer_year_id").val()){
            display_dynamic_form($("#hdn_application_offer_year_id").val());
        }
        if($('#hdn_current_application_id').val()==''){

        }else{
            $('#txt_offer_year_id').val($('#hdn_application_offer_year_id').val())
            $('#slt_offer_type').val($('#hdn_application_grade').val())
            display_known_offer($('#hdn_application_offer_year_id').val());

        }
    });

    function save(form_to_submit){
        id = 'form#' + form_to_submit;
        $(id).submit();
    }

    $("#lnk_profil_next_step").click(function() {
        $('#txt_message_error_profile').css('visibility', 'hidden').css('display','none');
        if (! valid()){
            return false;
        }
        $('#hdn_tab_applications_status').val('True');


        save('form_profile');
        return true;
    });
    $("#lnk_profil_next_step_up").click(function() {
        $('#txt_message_error_profile_up').css('visibility', 'hidden').css('display','none');
        if (! valid()){
            return false;
        }
        $('#hdn_tab_applications_status').val('True');
        save('form_profile');
        return true;
    });
    $("#lnk_application_tab").click(function() {
        if(! valid()){
            return false;
        }
        if ($('#hdn_application_id').val()){
            $('#slt_offer_type option').each(function(){
                if($(this).attr('value')==$('#hdn_application_grade').val()){
                    $(this).prop('selected', true);
                }
            });
            $('#slt_domain option').each(function(){
                if($(this).attr('value')==$('#hdn_application_domain_id').val()){
                    $(this).prop('selected', true);
                }
            });
           //TODO : les donnnées s'affichent puis elles disparaissent.... LV
        }
    });

    $("#btn_modify_picture").click(function(event) {
        update_description('ID_PICTURE', $(event.target));
        display_existing_files('ID_PICTURE');
    });

    $("#btn_modify_id_document").click(function(event) {
        update_description('ID_CARD',$(event.target));
        display_existing_files('ID_CARD');
    });

    $("#txt_birth_date").blur(function() {
        var value = $("#txt_birth_date").val();
        $("#msg_error_birth_date").find("label").remove();
        if (isDate(value)){
            $("#msg_error_birth_date").find("label").remove();
        }else{
            $("#msg_error_birth_date").append("<label>Invalid</label>");
        }

    });

    function isDate(txtDate){
        var currVal = txtDate;
        if(currVal == '')
            return false;

        var rxDatePattern = /^(\d{1,2})(\/|-)(\d{1,2})(\/|-)(\d{4})$/; //Declare Regex
        var dtArray = currVal.match(rxDatePattern); // is format OK?

        if (dtArray == null)
            return false;

        //Checks for mm/dd/yyyy format.
        dtDay = dtArray[1];
        dtMonth= dtArray[3];
        dtYear = dtArray[5];

        if (dtMonth < 1 || dtMonth > 12)
            return false;
        else if (dtDay < 1 || dtDay> 31)
            return false;
        else if ((dtMonth==4 || dtMonth==6 || dtMonth==9 || dtMonth==11) && dtDay ==31)
            return false;
        else if (dtMonth == 2)
        {
            var isleap = (dtYear % 4 == 0 && (dtYear % 100 != 0 || dtYear % 400 == 0));
            if (dtDay> 29 || (dtDay ==29 && !isleap))
                    return false;
        }
        return true;
    }

    // national diploma recto and verso
    $("#bt_load_doc_NATIONAL_DIPLOMA_VERSO").click(function(event) {
        update_description('NATIONAL_DIPLOMA_VERSO',$(event.target));
    });

    $("#bt_load_doc_NATIONAL_DIPLOMA_RECTO").click(function(event) {
        update_description('NATIONAL_DIPLOMA_RECTO',$(event.target));
    });
    // international diploma
    $("#bt_load_doc_INTERNATIONAL_DIPLOMA_VERSO").click(function(event) {
        update_description('INTERNATIONAL_DIPLOMA_VERSO',$(event.target));
    });

    $("#bt_load_doc_INTERNATIONAL_DIPLOMA_RECTO").click(function(event) {
        update_description('INTERNATIONAL_DIPLOMA_RECTO',$(event.target));
    });

    $("#bt_load_doc_TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO").click(function(event) {
        update_description('TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO',$(event.target));
    });

    $("#bt_load_doc_TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO").click(function(event) {
        update_description('TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO',$(event.target));
    });

    // Scores transcript
    $("#bt_load_doc_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO").click(function(event) {
        update_description('HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO',$(event.target));
    });
    $("#bt_load_doc_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO").click(function(event) {
        update_description('HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO',$(event.target));
    });

    $("#bt_load_doc_TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO").click(function(event) {
        update_description('TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO',$(event.target));
    });
    $("#bt_load_doc_TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO").click(function(event) {
        update_description('TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO',$(event.target));
    });
    $("#bt_load_doc_EQUIVALENCE").click(function(event) {
        update_description('EQUIVALENCE',$(event.target));
    });
    $("#bt_load_doc_ADMISSION_EXAM_CERTIFICATE").click(function(event) {
        update_description('ADMISSION_EXAM_CERTIFICATE',$(event.target));
    });
    $("#bt_load_doc_professional_exam_file").click(function(event) {
        update_description('PROFESSIONAL_EXAM_CERTIFICATE',$(event.target));
    });
    function valid(){
        if($("#hdn_tab_active").val()=="0"){
            if (! valid_profile()){
                return false;
            }
        }
        if($("#hdn_tab_active").val()=="1"){
            if (! valid_offer()){
                return false;
            }
        }
        return true;
    }
    function valid_profile(){
        if (($("#slt_nationality").prop('selectedIndex') < 0
            || $("#slt_legal_adr_country").prop('selectedIndex') < 0) || ($("#slt_nationality").val()=='-1' || $("#slt_legal_adr_country").val()=='-1')){
            $("#txt_message_error_profile_up").text(gettext('msg_next_profil'));
            $('#txt_message_error_profile_up').css('visibility', 'visible').css('display','block');
            return false;
        }
        return true;
    }
    $("#lnk_diploma_tab").click(function() {
        $('#form_secondary_education').append( $('#pnl_files>div') );
        if (! valid()){
            return false;
        }
    });
    $("#lnk_curriculum_tab").click(function() {
        if (! valid()){
            return false;
        }
    });
    $("#lnk_accounting_tab").click(function() {
        if (! valid()){
            return false;
        }
    });
    $("#lnk_sociological_tab").click(function() {
        if (! valid()){
            return false;
        }
    });
    $("#lnk_attachments_tab").click(function() {
        if (! valid()){
            return false;
        }
    });
    $("#lnk_submission_tab").click(function() {
        if (! valid()){
            return false;
        }
    });
    $("#lnk_profile_tab").click(function() {
        if($("#hdn_tab_active").val()=="1"){
        }else{
            if (! valid()){
                return false;
            }
        }
    });
    function valid_offer(){
        if ($("#txt_offer_year_id").val()==''
            || ($('#rdb_offer_belgiandegree_true').prop("checked") == "false" && $('#rdb_offer_belgiandegree_false').prop("checked") == "false") ){
            $("#txt_message_error_offer_up").text(gettext('msg_next_offer'));
            $('#txt_message_error_offer_up').css('visibility', 'visible').css('display','block');
            $("#txt_message_error_offer_down").text(gettext('msg_next_offer'));
            $('#txt_message_error_offer_down').css('visibility', 'visible').css('display','block');
            return false;
        }
        return true;
    }

    $("#lnk_next_offer_step_up").click(function() {
       return offer_steps();
    });
    $("#lnk_next_offer_step").click(function() {
        return offer_steps();
    });
    $("#lnk_previous_offer_step_up").click(function() {
       $('#form_secondary_education').append( $('#pnl_files>div') );
       return offer_steps();
    });
    $("#lnk_previous_offer_step").click(function() {
        $('#form_secondary_education').append( $('#pnl_files>div') );
        return offer_steps();
    });
    function offer_steps(){
        $('#txt_message_error_offer_up').css('visibility', 'hidden').css('display','none');
        $('#txt_message_error_offer_down').css('visibility', 'hidden').css('display','none');
        if (! valid()){
            return false;
        }
        $('#hdn_tab_applications_status').val('True');
        save('form_questions');
        return true;
    }

    function display_known_offer(offer_year_id){
        ajax_grade_choice($('#hdn_application_grade_type_id').val());
        $('#slt_domain').val($('#hdn_application_domain_id').val());
        ajax_offers($('#hdn_application_grade_type_id').val(),$('#hdn_application_offer_year_id').val());
        display_dynamic_form(offer_year_id);
        ajax_static_questions(offer_year_id,$('#hdn_applied_to_sameprogram').val(),$('#hdn_belgian_degree').val(),$('#hdn_started_samestudies').val());

    }
    //***************************
    //Assimilation criteria
    //***************************
    $( "input[name^='assimilation_criteria_']" ).click(function(event) {
        //One of the criteria has been checked as true or false
        var target = $(event.target);
        var id = target.attr("id");

        if(id.endsWith("_false")){
            var criteria = id.replace('assimilation_criteria_','');
            criteria = criteria.replace('_false','');
            $("#pnl_criteria_"+criteria).css('visibility', 'hidden').css('display','none');

        }
        if(id.endsWith("_true")){
            //Hide all pnl_criteria to let only one visible
            $('[id^="pnl_criteria_"]').each(function(){
                var target_pnl = $(this);
                var id_pnl = target_pnl.attr("id");

                var pos = id_pnl.indexOf('pnl_criteria_')
                var criteria_id = id_pnl.substring(pos+13)

                if ($('input[type=radio][name=assimilation_criteria_'+criteria_id+']:checked').attr('value') == 'true'){
                   if(id != 'assimilation_criteria_'+criteria_id+'_true'){
                        $('#assimilation_criteria_'+criteria_id+'_false').prop( "checked", true);
                   }
                }
                $(this).css('visibility', 'hidden').css('display','none');
            });
            var criteria = id.replace('assimilation_criteria_','');
            criteria = criteria.replace('_true','');
            $("#pnl_criteria_"+criteria).css('visibility', 'visible').css('display','block');
            $("#slt_criteria_5").val("");


        }
    });

    $(document).bind('click', function (e) {
       var target = $(e.target);
       var id = target.attr("id");
       if (target.is('.class_upload_assimilation')) {
          e.preventDefault(); // if you want to cancel the event flow

          if(id.startsWith('btn_load_assimilation_doc_')){
            //upload for assimilation
            var pos = id.indexOf('_id_')
            var description = id.substring(pos+4)
            update_description(description, target);
            display_existing_files(description)

          }

        }
      if(id=='bt_delete_document_file'){
        e.preventDefault(); // if you want to cancel the event flow
        click_bt_delete_document_file();
      }
    });

    $("#slt_criteria_5").change(function(event) {
        $('[id^="pnl_criteria_bis_"]').each(function(){
            $(this).remove();

        });
        var target = $(event.target);
        var id = target.attr("id");
        var selected_criteria = $("#slt_criteria_5").val();
        div_cloned =$("#pnl_criteria_"+selected_criteria).clone();
        var id_cloned_div = "pnl_criteria_bis_"+selected_criteria;
        div_cloned.attr("id",id_cloned_div);
        div_cloned.css('visibility', 'visible').css('display','block');
        div_cloned.appendTo("#pnl_other_criteria");
        var span = "<div>"+ gettext('concerned_person')+"</div>";
        $('#'+id_cloned_div+' .panel-heading').append(span);

    });
    //***************************
    //Assimilation criteria - end
    //***************************
    //***************************
    //File upload
    //***************************
    function update_description(description, elt){
        $('#hdn_description').val(description);
        $('#lbl_description_label').text(gettext(description.toLowerCase()));
        $('#txt_file').val('');
        $('#hdn_pushed').val(elt.attr("id"));
    }

    $("#txt_file").on("change", function(){
       var file = this.files[0],
       fileName = file.name,
       fileSize = file.size;
       $("#hdn_filename").val(fileName)

    });

    $('[id^="bt_load_doc_"]').click(function(event) {
        var target = $(event.target);
        var id = target.attr("id");
        var pos = id.indexOf('bt_load_doc_');
        var description = id.substring(pos+12);
        update_description(description, target);
    });

    $("#bt_upload_document").click(function(event) {
        var target = $(event.target);
        var id = target.attr("id");
        var form = target.form;

        var description = $("#hdn_description").val();
        //Clear existing fields
        $('#hdn_file_'+$("#txt_file").val()).remove();
        $('#hdn_file_name_'+description).remove();
        $('#hdn_file_description_'+description).remove();

        var data = new FormData();
        data.append('description', description);
        data.append('storage_duration', 0);

        data.append('filename', $("#txt_file").val());
        var fileSelect = document.getElementById('txt_file');
        var files = fileSelect.files;
        var file=''
        for (var i = 0; i < files.length; i++) {
          var file = files[i];
          data.append('file', file);
          break;
        }
        $.ajax({
            url: "{% url 'save_uploaded_file' %}",
            enctype: 'multipart/form-data',
            type: 'POST',
            data : data,
            processData: false,
            contentType: false,

          });
          update_upload_btn_class(file,description);

          return true;
    });

    //***************************
    //File upload - end
    //***************************
    function display_existing_files(description){
        // To clear the div
        $("#pnl_existing_files").html('')
        $("#pnl_existing_files").find("a")
            .remove()
            .end()
        //
        $.ajax({
            url: "/admission/document?description=" + description

          }).then(function(data) {

            if(data.length > 0 ){
                $('#pnl_existing_files').append("<br>");
                $('#pnl_existing_files').append('<span style="text-decoration:underline;">Existing file :</span>');
                $.each(data, function(key, value) {
                    var url = build_url('upload/download/', value.id);
                    $('#pnl_existing_files').append("<br>");
                    $('#pnl_existing_files').append($("<a></a>").attr("href", url)
                                                                .attr("target","_blank")
                                                                .append(value.file_name));
                    var url = build_url('upload/delete/', value.id);
                    var bt = jQuery('<input  id="hdn_delete_document_file" type="hidden" value="'+value.id+'">');
                    $('#pnl_existing_files').append(bt);
                    $('#pnl_existing_files').append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
                    bt = jQuery('<button type="submit" id="bt_delete_document_file" class="btn btn-default" data-dismiss="modal"><span class="glyphicon glyphicon-trash"></span></button>');
                    $('#pnl_existing_files').append(bt);

                });
            }
          });
    }

    function build_url(url_begin, value){
        /*Todo try to use django url directly in href - Leila*/
        var loc = location.href;

        var count = 0;
        var pos = loc.indexOf('/admission/');

        pos = pos + 12;
        while ( pos != -1 ) {
           count++;
           pos = loc.indexOf( "/",pos + 1 );
        }
        count=count-1;
        var url = url_begin + value;
        var cpt = 0;
        while (cpt< count){
            url = "../" + url
            cpt=cpt+1;

        }
        return url;
    }

    $('#bt_upload_document3').bind('bt_upload_document3done', function (e, data) {
        alert('Done');
    });
    $('#txt_file').bind('txt_filedone', function (e, data) {
        alert('Done');
    });


    function click_bt_delete_document_file(){

        var document_file_id = $('#hdn_delete_document_file').val();
        var description = $("#hdn_description").val();
        var data = new FormData();
        data.append('document_file_id', document_file_id);
        $.ajax({
            url: "{% url 'delete_document_file' %}",
            type: 'POST',
            data : data,
            processData: false,
            contentType: false

          });
          update_upload_btn_class('',description);

          return true;
    }
    function update_upload_btn_class(file, description){
          if(file != ''){
              if(description == 'ID_PICTURE'){
                $('#btn_modify_picture').attr('title', gettext('change_document'));
                $('#spn_modify_picture').attr('class', 'glyphicon glyphicon-ok-circle');
              }
              if(description == 'ID_CARD'){
                $('#btn_modify_id_document').attr('title', gettext('change_document'));
                $('#spn_modify_id_document').attr('class', 'glyphicon glyphicon-ok-circle');
              }

            $('[id$="'+description+'"]').each(function(){
                if($(this).attr("id").startsWith('btn_load_assimilation_doc_')){
                    $(this).attr('title', gettext('change_document'));
                    var spn_id = '#spn_' +$(this).attr("id");
                    $(spn_id).attr('class', 'glyphicon glyphicon-ok-circle');
                }
            });
          }else{
              if(description == 'ID_PICTURE'){
                $('#btn_modify_picture').attr('title', gettext('add_document'));
                $('#spn_modify_picture').attr('class', 'glyphicon glyphicon-upload');
              }
              if(description == 'ID_CARD'){
                $('#btn_modify_id_document').attr('title', gettext('add_document'));
                $('#spn_modify_id_document').attr('class', 'glyphicon glyphicon-upload');
              }

            $('[id$="'+description+'"]').each(function(){
                if($(this).attr("id").startsWith('btn_load_assimilation_doc_')){
                    $(this).attr('title', gettext('add_document'));
                    var spn_id = '#spn_' +$(this).attr("id");
                    $(spn_id).attr('class', 'glyphicon glyphicon-upload');
                }
            });

          }

    }
