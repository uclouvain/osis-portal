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
  var firstName = studentJson.etudiant.nom;
  var lastName = studentJson.etudiant.prenom;
  var academicYear = studentJson.monAnnee.anneeAcademique;
  var programTitle = studentJson.monAnnee.monOffre.offre.intituleComplet;
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
  var program = studentJson.monAnnee.monOffre.resultats;

  fillRowTotalECTSInscription(studentJson);
  fillRowMean(program);
  fillRowMention(program);
}

function fillRowTotalECTSInscription(studentJson) {
  var totalECTS = studentJson.monAnnee.monOffre.totalECTS;
  var programJson = studentJson.monAnnee.monOffre.resultats;
  var janvInscription = programJson.session[0].inscription;
  var juinInscription = programJson.session[1].inscription;
  var septInscription = programJson.session[2].inscription;

  var $frag = $(document.createDocumentFragment());
  createJQObject("<td/>", {}, totalECTS, $frag);
  createJQObject("<td/>", {}, janvInscription, $frag);
  createJQObject("<td/>", {}, juinInscription, $frag);
  createJQObject("<td/>", {}, septInscription, $frag);
  $frag.appendTo($("#summary_ects"));
}

function fillRowMean(programJson) {
  var meanJanv = programJson.session[0].moyenne;
  var meanJuin = programJson.session[1].moyenne;
  var meanSept = programJson.session[2].moyenne;

  var $rowMean = $("#summary_mean");

  var $frag = $(document.createDocumentFragment());
  createJQObject("<td/>", {}, "", $frag);
  createJQObject("<td/>", {}, meanJanv, $frag);
  createJQObject("<td/>", {}, meanJuin, $frag);
  createJQObject("<td/>", {}, meanSept, $frag);
  $frag.appendTo($rowMean);
}

function fillRowMention(programJson) {
  var mentionJanv = programJson.session[0].mention;
  var mentionJuin = programJson.session[1].mention;
  var mentionSept = programJson.session[2].mention;

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
  var arrayCourses = studentJson.monAnnee.monOffre.cours;

  var $frag = $(document.createDocumentFragment());
  $.each(arrayCourses, function(index, course) {
    var $row = createJQObjectNoText("<tr/>", {}, $frag);
    addRowCourse(course, $row);
  });
  $frag.appendTo($("#table_courses"));
}

function addRowCourse(courseJson, $row) {
  var acronym = courseJson.sigleComplet;
  var title = courseJson.intituleComplet;
  var ects = courseJson.poids;
  var inscr = inscrToString(courseJson.insc);
  var janv = examScoreToString(courseJson.session[0]);
  var juin = examScoreToString(courseJson.session[1]);
  var sept = examScoreToString(courseJson.session[2]);
  var credit = creditToString(courseJson.creditReport);

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

  var etatExam = etatExamToString(examJson);
  if (etatExam != ""){
    return etatExam;
  }

  var mention = mentionToString(examJson);
  if (mention != ""){
    return mention;
  }

  return scoreToString(examJson);
}

function etatExamToString(examJson){
  if(examJson.etatExam == "D") {
    return "Disp.";
  }
  return "";
}

function mentionToString(examJson){
  switch (examJson.mention) {
    case "M":
      return "Exc.";
    case "S":
      if (examJson.etatExam == "R"){
        return "Abs.(R)"
      }
      else {
        return "Abs.";
      }
    case "A":
      if (examJson.etatExam == "R"){
        return "Abs.(R)"
      }
      else {
        return "Abs.";
      }
    default:
      return "";
  }
}

function scoreToString(examJson){
  var score = examJson.note;
  if (examJson.etatExam == "-") {
    return score;
  }
  else if(score == "-") {
    return examJson.etatExam;
  }
  return score + examJson.etatExam;
}

function inscrToString(inscr) {
  switch (inscr) {
    case "I":
      return "Inscr";
    case "R":
      return "Rep.";
    case "D":
      return "Dsip.";
    case "B":
      return "Créd.";
    case "K":
      return "K94";
    case "C":
      return "C94";
    case "N":
      return "RIP";
    case "Q":
      return "Q94";
    case "S":
      return "EPM";
    case "T":
      return "T94";
    default:
      return inscr;
  }
}

function creditToString(creditReport) {
  switch (creditReport) {
    case "K":
      return "Crédit";
    case "R":
      return "Report";
    case "S":
      return "EPM";
    case "P":
      return "Postposé";
    default:
      return creditReport;

  }
}

/***************************** MENTION EXPLANATION PARAGRAPH ************/

function fillMentionExplanation(studentJson) {
  var mentionExplanation = studentJson.legende.explicationMention;
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
