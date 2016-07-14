// Note: Suppose bootsrap is used.


/*
 * Display the results of the student.
 * data: json representing the student results
 * parent_id: container view for the student results (div for example)
 */
function display_results(data, parent_id){
    create_nav_tabs(data.academic_years, parent_id);
    create_tab_panes(data.academic_years, parent_id);
}

/********************  NAVIGATION TABS *******************/

/*
 * Create the navigation tabs used to switch between academic year results.
 * Ex: <ul>
 *        <li> <a href="year_1_results">year 1</a> </li>
 *        <li> <a href="year_2_results">year 2</a> </li>
 *     </ul>
 * academic_years: academic year of the student
 * parent_id: container view for the student results (a div for example)
 */
function create_nav_tabs(academic_years, parent_id){
    var attributes_ul = { "class": "nav nav-tabs", role: "tablist"};
    var attributes_li = { role: "presentation" };
    var attributes_a = { role: "tab", "data-toggle": "tab" }
    var $ul = createJQObjectNoText("<ul/>", attributes_ul, parent_id);

    //Fragment use for efficiency as dom manipulaiton is costy
    var $frag = $(document.createDocumentFragment());
    var array_$li = createMultipleJQObject("<li/>", attributes_li, $frag, academic_years.length );
    array_$li[0].attr("class", "active");

    $.each(array_$li, function(index, $li) {
      var $a = createJQObject("<a/>", attributes_a, academic_years[index].programme ,$li);
      $a.attr({ href: "#year"+index.toString(), "aria-controls": "year"+index.toString()});
    })
    $frag.appendTo($ul);
}

/**************** PANES OF STUDENT RESULTS  *************/

/*
 * Create the tab panes which are referred by the navigation tabs
 * and contains the student results. One program result by tab pane.
 * Ex: <div class= "tab-content">
          <div role="tabpanel" id="year1"> "table of results ""</div>
          <div role="tabpanel" id="year2"> "table of results" </div>
       </div>
 * academic_years: academic year of the student
 * parent_id: container view for the student results (a div for example)
 */
function create_tab_panes(academic_years, parent_id){
    var attributes_global_div = { "class": "tab-content" };
    var attributes_div = { "class": "tab-pane", role: "tabpanel" };

    var $global_div = createJQObjectNoText("<div/>", attributes_global_div, parent_id);

    //Fragment use for efficiency as dom manipulaiton is costy
    var $frag = $(document.createDocumentFragment());
    var array_$div = createMultipleJQObject("<div/>", attributes_div, $frag, academic_years.length);
    array_$div[0].attr("class", "tab-pane active");
    $.each(array_$div, function(index, $div) {
        $div.attr("id", "year"+index.toString());

        //table of courses with their results
        var $table = create_results_table($div);
        fill_table_results($table, academic_years[index]);

        //table of summary of the results
        display_summary_results(academic_years[index], $div);
    });
    $frag.appendTo($global_div);
}

/*
 * Create a jQuery object representing a "table" dom.
 * This object will be contained by $parent.
 */
function create_results_table($parent){
    var attributes_div_table = { "class": "table-responsive" };
    var attributes_table = { "class": "table table-striped table-bordered table-hover" };
    var $div_table= createJQObjectNoText("<div/>", attributes_div_table, $parent);

    var $table = createJQObjectNoText("<table/>", attributes_table, $div_table);
    return $table;
}

/*
 * Fill the table with the student results contained in data.
 * See the "header_table" to know the format of data.
 * $table: jQuery object that represents a dom table.
 * data: two dimension arrays of data to fill in the table.
 */
function fill_table_results($table, data) {
  var headers_table = ["Cours", "Intitulé", "ECTS", "Insc.", "Janv", "Juin", "Sept", "Crédit"];
  var data_table = [headers_table];
  data_table = $.merge(data_table, results_json_to_array(data));
  fillTable($table, data_table);
}

/*
 * Convert the student results in json into an array representation.
 * Typically it returns a two dimension table of courses results.
 */
function results_json_to_array(results) {
  var courses = results.learning_units;
  var array_results = [];
  $.each(courses, function(index, course){
      var course_result = [];
      course_result.push(course.acronym);
      course_result.push(course.title);
      course_result.push(course.credits);
      course_result.push("Inscr");
      course_result.push(course.exams[0].score);
      course_result.push(course.exams[1].score);
      course_result.push(course.exams[2].score);
      course_result.push("Crédit");

      array_results.push(course_result);
  });
  return array_results;
}

/**************** SUMMARY OF STUDENT RESULTS *************/

/*
 * Dsiplay a table that summarize the student results.
 * data: json representing the student results
 * $parent: parent jQuery object that will contain the student results.
 */
function display_summary_results(data, $parent){
    var $table = create_summary_table($parent);
    fill_summary_table(data, $table);
}

/*
 * Create a jQuery object representing a "table" dom.
 * This object will be contained by $parent.
 */
function create_summary_table($parent){
    var attributes_global_div = { "class": "row" };
    var attributes_div_positionement = { "class": "col-md-4 col-md-offset-4" };
    var attributes_div_table = { "class": "table-responsive" };
    var attributes_table = { "class": "table table-striped table-condensed" };

    var $global_div = createJQObjectNoText("<div/>", attributes_global_div, $parent);

    var $div_positionement = createJQObjectNoText("<div/>", attributes_div_positionement, $global_div);

    var $div_table= createJQObjectNoText("<div/>", attributes_div_table, $div_positionement);

    var $table = createJQObjectNoText("<table/>", attributes_table, $div_table);

    return $table;
}

/*
 * Fill the table with a summary of the student results.
 * $table: jQuery object that represents a dom table.
 * data: json object of student results.
 */
function fill_summary_table(data, $table){
  row_credits = ["Crédits", "-", "-", "-"];
  row_date_sessions = [" ", "Janv", "Juin", "Sept"];
  row_mean_scores = ["Moyenne", "-", "-", "-"];
  row_mention = ["Mention", "-", "-", "-"];

  data_table = [row_credits, row_date_sessions, row_mean_scores, row_mention];
  fillTable($table, data_table);
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
