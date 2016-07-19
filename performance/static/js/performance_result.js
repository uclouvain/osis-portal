/************************* FILL PERFORMANCE RESULT PAGE ***************/

function fillPage(studentJson) {
  fillStudentInfo(studentJson);
  fillSessionSummaryTable(studentJson);
  fillCoursesTable(studentJson);
  fillMentionExplanation(studentJson);
}

/***************************** STUDENT INFORMATION ********************/

/*
 * Fill the student information that consitst of the name, academic year
 * and program title.
 * studentJson: a json containing the student results.
 */
function fillStudentInfo(studentJson) {
  var firstName = studentJson.first_name;
  var lastName = studentJson.last_name;
  var academicYear = studentJson.academic_years[0].year;
  var programTitle = studentJson.academic_years[0].programs[0].title;
  $("#student_name").text(lastName + " " + firstName);
  $("#academic_year").text(academicYear);
  $("#program_title").text(programTitle);
}

/********************** STUDENT SESSIONS SUMMARY ***********************/

/*
 * Fill the table containint the summary of the sessions.
 * The summary is comprised of the total ects, mean for the sessions
 * and the mentions attributed.
 * studentJson: a json containing the student results.
 */
function fillSessionSummaryTable(studentJson) {
  var program = studentJson.academic_years[0].programs[0];

  fillRowTotalECTS(program);
  fillRowMean(program);
  fillRowMention(program);
}

function fillRowTotalECTS(programJson) {
  var totalECTS = programJson.total_ECTS;
  createJQObject("<td/>", {}, totalECTS, $("#summary_ects"));
}

function fillRowMean(programJson) {
  var meanJanv = programJson.results[0].mean;
  var meanJuin = programJson.results[1].mean;
  var meanSept = programJson.results[2].mean;

  var $rowMean = $("#summary_mean");

  var $frag = $(document.createDocumentFragment());
  createJQObject("<td/>", {}, "", $frag);
  createJQObject("<td/>", {}, meanJanv, $frag);
  createJQObject("<td/>", {}, meanJuin, $frag);
  createJQObject("<td/>", {}, meanSept, $frag);
  $frag.appendTo($rowMean);
}

function fillRowMention(programJson) {
  var mentionJanv = programJson.results[0].mention;
  var mentionJuin = programJson.results[1].mention;
  var mentionSept = programJson.results[2].mention;

  var $rowMention = $("#summary_mention");

  var $frag = $(document.createDocumentFragment());
  createJQObject("<td/>", {}, "", $frag);
  createJQObject("<td/>", {}, mentionJanv, $frag);
  createJQObject("<td/>", {}, mentionJuin, $frag);
  createJQObject("<td/>", {}, mentionSept, $frag);
  $frag.appendTo($rowMention);
}

/**************************** STUDENT COURSES RESULTS ******************/

/*
 * Fill the table containint the list of courses for the program.
 * Each course is defined by it acronym, title, weight (ects),
 * inscription, score in january, june and september and finally the credit.
 * studentJson: a json containing the student results.
 */

function fillCoursesTable(studentJson) {
  var arrayCourses = studentJson.academic_years[0].programs[0].learning_units;

  var $frag = $(document.createDocumentFragment());
  $.each(arrayCourses, function(index, course) {
    var $row = createJQObjectNoText("<tr/>", {}, $frag);
    addRowCourse(course, $row);
  });
  $frag.appendTo($("#table_courses"));
}

function addRowCourse(courseJson, $row) {
  var acronym = courseJson.acronym;
  var title = courseJson.title;
  var ects = courseJson.credits;
  var inscr = "Inscr";
  var janv = examScoreToString(courseJson.exams[0]);
  var juin = examScoreToString(courseJson.exams[1]);
  var sept = examScoreToString(courseJson.exams[2]);
  var credit = "Crédits";

  createJQObject("<td/>", {}, acronym, $row);
  createJQObject("<td/>", {}, title, $row);
  createJQObject("<td/>", {}, ects, $row);
  createJQObject("<td/>", {}, inscr, $row);
  createJQObject("<td/>", {}, janv, $row);
  createJQObject("<td/>", {}, juin, $row);
  createJQObject("<td/>", {}, sept, $row);
  createJQObject("<td/>", {}, credit, $row);
}

function examScoreToString(examJson) {
  var score = examJson.score;
  if (examJson.status_exam == "-") {
    return score;
  }
  return score + examJson.status_exam;
}

/***************************** MENTION EXPLANATION PARAGRAPH ************/

function fillMentionExplanation(studentJson) {
  var mentionExplanation = studentJson.academic_years[0].programs[0].mention_explanation;
  $("#paragraph_mention_explanation").text(mentionExplanation);
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
