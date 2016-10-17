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
  $("#student_name").append("<br>");
  $("#student_name").append(lastName + ", " + firstName);
  $("#academic_year").append("<br>");
  $("#academic_year").append(academicYear);
  $("#program_title").append("<br>");
  $("#program_title").append(programTitle);
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

  fillRowTotalECTSInscription(program);
  fillRowMean(program);
  fillRowMention(program);
}

function fillRowTotalECTSInscription(programJson) {
  var totalECTS = programJson.total_ECTS;
  var janvInscription = programJson.results[0].insc;
  var juinInscription = programJson.results[1].insc;
  var septInscription = programJson.results[2].insc;

  var $frag = $(document.createDocumentFragment());
  createJQObject("<td/>", {}, totalECTS, $frag);
  createJQObject("<td/>", {}, janvInscription, $frag);
  createJQObject("<td/>", {}, juinInscription, $frag);
  createJQObject("<td/>", {}, septInscription, $frag);
  $frag.appendTo($("#summary_ects"));
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
  var inscr = inscrToString(courseJson.insc);
  var janv = examScoreToString(courseJson.exams[0]);
  var juin = examScoreToString(courseJson.exams[1]);
  var sept = examScoreToString(courseJson.exams[2]);
  var credit = creditToString(courseJson.credit_report);

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
  else if(score == "-") {
    return examJson.status_exam;
  }
  return score + examJson.status_exam;
}

function inscrToString(inscr) {
  if (inscr == "I") {
    return "Inscr";
  }
  return "-";
}

function creditToString(creditReport) {
  if (creditReport == "K") {
    return "Crédit";
  }
  return "-";
}

/***************************** MENTION EXPLANATION PARAGRAPH ************/

function fillMentionExplanation(studentJson) {
  var mentionExplanation = studentJson.academic_years[0].programs[0].mention_explanation;
  $("#paragraph_mention_explanation").html(mentionExplanation);
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
