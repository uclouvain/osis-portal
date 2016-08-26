var nextIdDocForm = 0; // Global variable to keep track of the number of document forms already created.
var maxNumberForms = 5; // Default value


$(document).ready(function(){
    maxNumberForms = $("#id_form-MAX_NUM_FORMS").attr("value").toString();
    disablePlusButton();  // In case if the user has already uploaded the maximum number of attachments.
    // Adds a form when performing a click on the plus button.
    $("#button_add_form").click(function(){
        createDocumentForm();
        incrementNextIdDocForm();
    });
});


// Functions used to activate and deactivate the plus button.
function incrementNextIdDocForm(){
    nextIdDocForm++;
    disablePlusButton();
}

function decrementNextIdDocForm(){
    nextIdDocForm--;
    activatePlusButton();
    var totalForms = nextIdDocForm;
    $("#id_form-TOTAL_FORMS").attr("value", totalForms.toString());
}


function disablePlusButton(){
    if(nextIdDocForm >= maxNumberForms){
        $("#button_add_form").prop("disabled", true);
    }
}

function activatePlusButton(){
    if(nextIdDocForm < maxNumberForms){
        $("#button_add_form").prop("disabled", false);
    }
}


/*
 * Creates a document form and appends it to the div having as id
 * "div_document_forms".
 */
function createDocumentForm(){
    var divFormId = "form_".concat(nextIdDocForm.toString());
    var $divForm = createJQObjectNoParentNoText("<div/>", {"id": divFormId,
        "class": "row"});

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
    appendRemoveButton($divForm)

    createJQObjectNoText("<br/>", {}, $($divForm));

    $divForm.appendTo($("#div_document_forms"));
    var totalForms = nextIdDocForm+1;
    $("#id_form-TOTAL_FORMS").attr("value", totalForms.toString());
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
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);
    //var $label = createJQObject("<label/>", {"for": labelFor}, "Filename", $divInput);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-file_name";
    var inputName = inputNamePrefix.concat(nextIdDocForm.toString(), inputNameSuffix);
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
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);
    //var $label = createJQObject("<label/>", {"for": labelFor}, "File", $divInput);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-file";
    var inputName = inputNamePrefix.concat(nextIdDocForm.toString(), inputNameSuffix);
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
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);
    //var $label = createJQObject("<label/>", {"for": labelFor}, "Description", $divInput);

    var selectNamePrefix = "form-";
    var selectNameSuffix = "-description";
    var selectName = selectNamePrefix.concat(nextIdDocForm.toString(), selectNameSuffix);
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
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-content_type";
    var inputName = inputNamePrefix.concat(nextIdDocForm.toString(), inputNameSuffix);
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
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-user";
    var inputName = inputNamePrefix.concat(nextIdDocForm.toString(), inputNameSuffix);
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
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-storage_duration";
    var inputName = inputNamePrefix.concat(nextIdDocForm.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
        "name": inputName,
        "type": "hidden",
        "value": "0"}, $parentForm);
}


/*
 * Appends an input for the "application_name" to a form.
 * $parentForm: a JQuery object representing a form.
 */
function appendDocumentTypeInput($parentForm){
    // A label for attribute is of the form "id_form-0-application_name" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-application_name";
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-application_name";
    var inputName = inputNamePrefix.concat(nextIdDocForm.toString(), inputNameSuffix);
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
    var labelFor = labelForPrefix.concat(nextIdDocForm.toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-size";
    var inputName = inputNamePrefix.concat(nextIdDocForm.toString(), inputNameSuffix);
    var $input = createJQObjectNoText("<input/>", {"id": labelFor,
        "name": inputName,
        "type": "hidden"}, $parentForm);
}


/*
 * Appends the remove button when wanting to remove an attachment uplooad form.
 * $parentForm: a JQuery object representing a form.
 */
function appendRemoveButton($parentForm){
    var $buttonRemove = createJQObjectNoText("<button/>", {"type": "button",
        "class": "btn btn-default"}, $parentForm);
    var $span = createJQObjectNoText("<span/>", {"class": "glyphicon glyphicon-remove",
        "aria-hidden": "true"}, $buttonRemove);
    var divFormId = "#form_".concat(nextIdDocForm.toString());
    $buttonRemove.click(function(){
        var $divFormId = $(divFormId);
        var idNumber = getIdNumber($divFormId.attr("id"));
        $divFormId.remove();
        decrementNextIdDocForm();
        reorderFormsId(idNumber);
    });
}


/*
 * Reorder the forms id so that they are in increasing order
 * of step 1 starting at 0.
 * Ex: 0 - 1 - 2 - 3  good
 *     0 - 1 - 3 - 4  bad (1 - 3)
 * $idDivRemoved: id number of the div removed
 */
function reorderFormsId(idDivRemoved){
    var idToBeginOrder = idDivRemoved;
    // Apply function on all div containing a document form.
    $("#div_document_forms > [id^=form_]").each(function(index, element){
        var elementIdNumber = getIdNumber($(this).attr("id"));
        if( elementIdNumber > idToBeginOrder){
            // Then we decrement the value of the id by one.
            decrementIdOfDocForm($(this), elementIdNumber);
        }
    });
}


/*
 * Decrement the id of the doc form.
 */
function decrementIdOfDocForm($divDocForm, currentIdNumber){
    $divDocForm.attr({"id":"form_".concat((currentIdNumber-1).toString())});

    decrementFileName($divDocForm, currentIdNumber);
    decrementFile($divDocForm, currentIdNumber);
    decrementDescriptionId($divDocForm, currentIdNumber);

    decrementUserId($divDocForm, currentIdNumber)
    decrementContentTypeId($divDocForm, currentIdNumber);
    decrementStorageDurationId($divDocForm, currentIdNumber);
    decrementDocumentTypeId($divDocForm, currentIdNumber);
    decrementSizeId($divDocForm, currentIdNumber);
    modifyButtonRemoveBehaviour($divDocForm, currentIdNumber);
}

// decrement file name id
function decrementFileName($divDocForm, currentIdNumber){
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-file_name";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-file_name";
    var newInputName = inputNamePrefix.concat((currentIdNumber-1).toString(), inputNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newInputName});
}

// decrement file id
function decrementFile($divDocForm, currentIdNumber) {
    // A label for attribute is of the form "id_form-0-file" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-file";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-file";
    var newInputName = inputNamePrefix.concat((currentIdNumber-1).toString(), inputNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newInputName});
}

// decrement user id
function decrementUserId($divDocForm, currentIdNumber){
    // A label for attribute is of the form "id_form-0-user" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-user";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-user";
    var newInputName = inputNamePrefix.concat((currentIdNumber-1).toString(), inputNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newInputName});
}

// decrement description id
function decrementDescriptionId($divDocForm, currentIdNumber){
    // A label for attribute is of the form "id_form-0-description" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-description";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var selectNamePrefix = "form-";
    var selectNameSuffix = "-description";
    var newSelectName = selectNamePrefix.concat((currentIdNumber-1).toString(), selectNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newSelectName});
}

// decrement content type id
function decrementContentTypeId($divDocForm, currentIdNumber){
    // A label for attribute is of the form "id_form-0-content_type" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-content_type";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-content_type";
    var newInputName = inputNamePrefix.concat((currentIdNumber-1).toString(), inputNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newInputName});
}

// decrement storage duration id
function decrementStorageDurationId($divDocForm, currentIdNumber){
    // A label for attribute is of the form "id_form-0-storage_duration" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-storage_duration";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-storage_duration";
    var newInputName = inputNamePrefix.concat((currentIdNumber-1).toString(), inputNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newInputName});
}

// decrement application name id
function decrementDocumentTypeId($divDocForm, currentIdNumber){
    // A label for attribute is of the form "id_form-0-application_name" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-application_name";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-application_name";
    var newInputName = inputNamePrefix.concat((currentIdNumber-1).toString(), inputNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newInputName});
}

// decrement application name id
function decrementSizeId($divDocForm, currentIdNumber){
    // A label for attribute is of the form "id_form-0-size" for example.
    var labelForPrefix = "id_form-";
    var labelForSuffix = "-size";
    var labelFor = labelForPrefix.concat(currentIdNumber.toString(), labelForSuffix);
    var newLabelFor = labelForPrefix.concat((currentIdNumber-1).toString(), labelForSuffix);

    var inputNamePrefix = "form-";
    var inputNameSuffix = "-size";
    var newInputName = inputNamePrefix.concat((currentIdNumber-1).toString(), inputNameSuffix);

    $divDocForm.find("#".concat(labelFor)).attr({"id" : newLabelFor,
        "name": newInputName});
}

// Modify the remove button so that it removed the correct upload form
function modifyButtonRemoveBehaviour($divDocForm, currentIdNumber){
    var $buttonRemove = $divDocForm.find("button");
    var divFormId = $divDocForm;
    $buttonRemove.off();
    $buttonRemove.click(function(){
        var $divFormId = $(divFormId);
        var idNumber = getIdNumber($divFormId.attr("id"));
        $divFormId.remove();
        decrementNextIdDocForm();
        reorderFormsId(idNumber);
    });
}

/*
 * Extract the id number from the id string of a div
 * containing a document form.
 */
function getIdNumber(idString){
    var idNumberOnly = idString.substring(5);
    return parseInt(idNumberOnly);
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



