var numberDocForms = 0; // Global variable to keep track of the number of document forms already created.

$(document).ready(function(){
    // Adds a form when performing a click on the plus button.
    $("#button_add_form").click(function(){
        createDocumentForm();
    });
});


/*
 * Creates a document form and appends it to the div having as id
 * "div_document_forms".
 */
function createDocumentForm(){
    var divFormId = "form_".concat(numberDocForms.toString())
    var $divForm = createJQObjectNoParentNoText("<div/>", {"id": divFormId,
                                                           "class": "row"})

    // Visible inputs
    appendFileNameInput($divForm);
    appendFileInput($divForm);
    appendDescriptionInput($divForm);
    // Hidden inputs
    appendContentTypeInput($divForm);
    appendUserInput($divForm);
    appendStorageDurationInput($divForm);
    appendDocumentTypeInput($divForm);
    appendSizeInput($divForm);
    appendRemoveButton($divForm);

    $divForm.appendTo($("#div_document_forms"));
    numberDocForms++;
    $("#id_form-TOTAL_FORMS").attr("value", numberDocForms.toString());
}


/*
 * Appends an input for the "file_name" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendFileNameInput($parentForm){
    var $divInput = createJQObjectNoText("<div/>", {"class": "form_group col-md-4"}, $parentForm);

    // A label for attribute is of the form "id_form-0-file_name" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-file_name";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);
    var $label = createJQObject("<label/>", {"for": labelFor}, "Filename", $divInput);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-file_name";
    var inputName = inputNamePrefix.concat(numberDocForms.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
                                             "name": inputName,
                                             "type": "text",
                                             "class": "form-control"}, $divInput);
}

/*
 * Appends an input for the "file" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendFileInput($parentForm){
    var $divInput = createJQObjectNoText("<div/>", {"class": "form_group col-md-4"}, $parentForm);

    // A label for attribute is of the form "id_form-0-file" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-file";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);
    var $label = createJQObject("<label/>", {"for": labelFor}, "File", $divInput);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-file";
    var inputName = inputNamePrefix.concat(numberDocForms.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
                                             "name": inputName,
                                             "type": "file"}, $divInput);
}

/*
 * Appends an input for the "description" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendDescriptionInput($parentForm){
    var $divInput = createJQObjectNoText("<div/>", {"class": "form_group col-md-2"}, $parentForm);

    // A label for attribute is of the form "id_form-0-description" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-description";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);
    var $label = createJQObject("<label/>", {"for": labelFor}, "Description", $divInput);

    var selectNamePrefix = "form-";
    var selectNameSuffix = "-description";
    var selectName = selectNamePrefix.concat(numberDocForms.toString(), selectNameSuffix);
    var $select = createJQObjectNoText("<select/>", {"id": labelFor,
                                             "name": selectName}, $divInput);

    var $option1 = createJQObject("<option/>", {"value": "ID_CARD"}, "identity_card", $select);
    var $option2 = createJQObject("<option/>", {"value": "LETTER_MOTIVATION"}, "letter_motivation", $select);
    var $option2 = createJQObject("<option/>", {"value": "ID_PICTURE"}, "id_picture", $select);
}


/*
 * Appends an input for the "content_type" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendContentTypeInput($parentForm){
    // A label for attribute is of the form "id_form-0-content_type" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-content_type";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-content_type";
    var inputName = inputNamePrefix.concat(numberDocForms.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
                                             "name": inputName,
                                             "type": "hidden",
                                             "value": "application/csv"}, $parentForm);
}


/*
 * Appends an input for the "user" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendUserInput($parentForm){
    // A label for attribute is of the form "id_form-0-user" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-user";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-user";
    var inputName = inputNamePrefix.concat(numberDocForms.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
                                             "name": inputName,
                                             "type": "hidden",
                                             "value": "2"}, $parentForm);
}

/*
 * Appends an input for the "storage_duration" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendStorageDurationInput($parentForm){
    // A label for attribute is of the form "id_form-0-storage_duration" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-storage_duration";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-storage_duration";
    var inputName = inputNamePrefix.concat(numberDocForms.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
                                             "name": inputName,
                                             "type": "hidden",
                                             "value": "0"}, $parentForm);
}


/*
 * Appends an input for the "document_type" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendDocumentTypeInput($parentForm){
    // A label for attribute is of the form "id_form-0-document_type" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-document_type";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-document_type";
    var inputName = inputNamePrefix.concat(numberDocForms.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
                                             "name": inputName,
                                             "type": "hidden",
                                             "maxlength": "100",
                                             "value": "admission_attachments"}, $parentForm);
}


/*
 * Appends an input for the "size" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendSizeInput($parentForm){
    // A label for attribute is of the form "id_form-0-size" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-size";
    var labelFor = labelForPrefix.concat(numberDocForms.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-size";
    var inputName = inputNamePrefix.concat(numberDocForms.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
                                             "name": inputName,
                                             "type": "hidden"}, $parentForm);
}


function appendRemoveButton($parentForm){
    var $buttonRemove = createJQObjectNoText("<button/>", {"type": "button",
                                                            "class": "btn btn-default"}, $parentForm);
    var $span = createJQObjectNoText("<span/>", {"class": "glyphicon glyphicon-remove",
                                           "aria-hidden": "true"}, $buttonRemove);
    var divFormId = "#form_".concat(numberDocForms.toString());
    $buttonRemove.click(function(){
        $(divFormId).remove();
        numberDocForms--;
    });
}


/***************************** UTILITY FUNCTIONS ***********************/

/*
 * Creates a new jQuery object representing a DOM document.
 * tag: string of the form "<HTML_tag/>" which is the DOM type
 * attributes: object of key/value pairs that are attributes of the DOM
 * text: string which is the content of the DOM
 * $parent: jQuery object that will be the parent (container)
 */
 function createJQObject(tag, attributes, text, $parent) {
   var $jQObj = $(tag, attributes);
   $jQObj.text(text);
   $jQObj.appendTo($parent) ;
   return $jQObj;
 }

 /*
  * Creates a new jQuery object representing a DOM document.
  * tag: string of the form "<HTML_tag/>" which is the DOM type
  * attributes: object of key/value pairs that are attributes of the DOM
  * $parent: jQuery object that will be the parent (container)
  */
  function createJQObjectNoText(tag, attributes, $parent) {
    var $jQObj = $(tag, attributes);
    $jQObj.appendTo($parent) ;
    return $jQObj;
  }

 /*
  * Creates a new jQuery object representing a DOM document.
  * tag: string of the form "<HTML_tag/>" which is the DOM type
  * attributes: object of key/value pairs that are attributes of the DOM
  */
  function createJQObjectNoParentNoText(tag, attributes) {
    var $jQObj = $(tag, attributes);
    return $jQObj;
  }

  /*
   * Creates "n" same jQuery objects that are child of "parent".
   * tag: string of the form "<HTML_tag/>" which is the DOM type
   * attributes: object of key/value pairs that are attributes of the DOM
   * $parent: jQuery object that will be the parent (container)
   * n: number of objects to create
   */
   function createMultipleJQObject(tag, attributes, $parent, n){
     //Fragment use for efficiency as dom manipulaiton is costy
     var $frag = $(document.createDocumentFragment());
     var array_obj = [];

     for(var i = 0; i < n; i++){
       var obj = createJQObjectNoText(tag, attributes, $frag);
       array_obj.push(obj);
     }

     $frag.appendTo($parent);
     return array_obj;
   }

  /*
   * Fill the table with data.
   * $table: jQuery object representing a table DOM document
   * data: a two dimension array of data to put in the table
   */
   function fillTable($table, data){
     //Fragment use for efficiency as dom manipulation is costy
     var $frag = $(document.createDocumentFragment());

     $.each(data, function(row_index, row_data) {
       var $row = createJQObjectNoText("<tr>", {}, $frag);

       $.each(row_data, function(cell_index, cell_data) {
         var $cell = createJQObject("<td>", {}, cell_data, $row);
       });

     });

     $frag.appendTo($table);
   }
