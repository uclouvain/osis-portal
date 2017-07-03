/************************* FILL PERFORMANCE RESULT PAGE ***************/

function fillPage(studentJson) {
  fillStudentInfo(studentJson);
  fillSessionSummaryTable(studentJson);
  fillCoursesTable(studentJson);
  fillMentionExplanation(studentJson);
  fillLegendExplanation(studentJson);
}

/***************************** STUDENT INFORMATION ********************/

/*
 * Fill the student information that consitst of the name, academic year
 * and program title.
 * studentJson: a json containing the student results.
 */
function fillStudentInfo(studentJson) {
  var firstName = studentJson.etudiant.prenom;
  var lastName = studentJson.etudiant.nom;
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
  fillRowsMean(program);
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


function createMeanFrangment(meanJanv, meanJuin, meanSept, rowMean) {
  var $fragGen = $(document.createDocumentFragment());
  createJQObject("<td/>", {}, "", $fragGen);
  createJQObject("<td/>", {}, meanJanv, $fragGen);
  createJQObject("<td/>", {}, meanJuin, $fragGen);
  createJQObject("<td/>", {}, meanSept, $fragGen);
  $fragGen.appendTo(rowMean);
}

function fillRowsMean(programJson) {
  if(programJson.session[0].hasOwnProperty('moyenneGenerale')
     && programJson.session[0].moyenneGenerale != null){
    $("#summary_mean").hide();

    var meanSuccJanv = programJson.session[0].moyenne;
    var meanSuccJuin = programJson.session[1].moyenne;
    var meanSuccSept = programJson.session[2].moyenne;
    var $rowSuccessMean = $("#summary_success_mean");

    createMeanFrangment(meanSuccJanv, meanSuccJuin, meanSuccSept, $rowSuccessMean);

    var meanGenJanv = programJson.session[0].moyenneGenerale;
    var meanGenJuin = programJson.session[1].moyenneGenerale;
    var meanGenSept = programJson.session[2].moyenneGenerale;
    var $rowGenMean = $("#summary_general_mean");

    createMeanFrangment(meanGenJanv, meanGenJuin, meanGenSept, $rowGenMean);
  }
  else{
    $("#summary_success_mean").hide();
    $("#summary_general_mean").hide();

    var meanJanv = programJson.session[0].moyenne;
    var meanJuin = programJson.session[1].moyenne;
    var meanSept = programJson.session[2].moyenne;
    var $rowMean = $("#summary_mean");

    createMeanFrangment(meanJanv, meanJuin, meanSept, $rowMean);
  }

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
  if (typeof arrayCourses !== "undefined" && arrayCourses !== null && arrayCourses.length > 0){
    var $frag = $(document.createDocumentFragment());
    $.each(arrayCourses, function(index, course) {
      var $row = createJQObjectNoText("<tr/>", {}, $frag);
      addRowCourse(course, $row);
    });
    $frag.appendTo($("#table_courses"));
  }
}

function addRowCourse(courseJson, $row) {
  var acronym = courseJson.sigleComplet;
  var title = courseJson.intituleComplet;
  var ects = courseJson.poids;
  var inscr = inscrToString(courseJson.insc);
  var janv = courseJson.session[0];
  var juin = courseJson.session[1];
  var sept = courseJson.session[2];
  var credit = creditToString(courseJson.creditReport);

  createJQObject("<td/>", {}, acronym, $row);
  createJQObject("<td/>", {}, title, $row);
  createJQObject("<td/>", {}, ects, $row);
  createJQObject("<td/>", {}, inscr, $row);
  makeScoreCell(janv, $row);
  makeScoreCell(juin, $row);
  makeScoreCell(sept, $row);
  if(credit.trim() == '-'){
    createJQObject("<td/>", {"class": "text-center"}, credit, $row);
  } else {
    createJQObject("<td/>", {}, credit, $row);
  }
}

function cleanEtatExam(etatExam) {
  if (etatExam == null
      || etatExam.trim() == "-"
      || etatExam.trim() == ""
      || etatExam.trim() == "null"){
    return null;
  } else {
    return etatExam.trim();
  }
}

function makeScoreCell(examJson, row){
  var $score = examJson.note;
  var $etatExam = cleanEtatExam(examJson.etatExam);
  var $mention = mentionToString(examJson);
  if ($mention != ""){
    createJQObject("<td/>", {"colspan" : 2, "class": "text-center"}, $mention, row);
  }
  else if ($etatExam == null){
    createJQObject("<td/>", {"colspan" : 2, "class": "text-center"}, $score, row);
  }
  else{
    createJQObject("<td/>", {"style": "border-right:none;"}, $score, row);
    createJQObject("<td/>", {"class": "text-right",
                             "style": "border-left:none;"}, $etatExam, row);
  }

}

function mentionToString(examJson){
  switch (examJson.mention) {
    case "M":
      return "Excusé";
    case "S":
      if (examJson.etatExam == "R"){
        return "Absent(R)"
      }
      else {
        return "Absent";
      }
    case "A":
      if (examJson.etatExam == "R"){
        return "Absent(R)"
      }
      else {
        return "Absent";
      }
    case "T":
          return "Tricherie";
    default:
      return "";
  }
}


function inscrToString(inscr) {
  switch (inscr) {
    case "I":
      return "Inscr";
    case "R":
      return "Rep.";
    case "D":
      return "Disp.";
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
      return "Test";
    case "X":
          return "Ext.";
    default:
      return inscr;
  }
}

function creditToString(creditReport) {
  switch (creditReport) {
    case "K":
      return "Crédité";
    case "R":
      return "Reporté";
    case "S":
      return "EPM";
    case "P":
      return "Postposé";
    case "r":
      return "Reussi";
    default:
      return creditReport;

  }
}

/***************************** MENTION AND LEGEND EXPLANATION PARAGRAPH ************/

function fillMentionExplanation(studentJson) {
  var mentionExplanation = studentJson.legende.explicationMention;
  $("#paragraph_mention_explanation").html(mentionExplanation);
}


function fillLegendExplanation(studentJson) {
  var legendExplanation = studentJson.legende.explicationLettresLegende;

  if (typeof legendExplanation !== "undefined" && legendExplanation !== null && legendExplanation.length > 0) {
    var $frag = $(document.createDocumentFragment());
    var $row;
    $.each(legendExplanation, function (index, letter_explanation) {
      if (index == 0 || index % 2 == 0) {
        $row = createJQObjectNoText("<div/>", {'class': 'row'}, $frag);
        var $col = createJQObjectNoText("<div/>", {'class': 'col-md-6'}, $row);
        createJQObject("<p/>", {}, letter_explanation, $col);
      }
      else {
        var $col = createJQObjectNoText("<div/>", {'class': 'col-md-6'}, $row);
        createJQObject("<p/>", {}, letter_explanation, $col);
      }

    });
    $frag.appendTo($("#body_legend_explanation"));
  }
}

/******************************Cycle Advancement*************************/

function fillCycleAdvancement(studentJson){
  var cycleAdvancementJson = studentJson.detailsCredits;
  var afficherTableau = cycleAdvancementJson.afficherTabCreditsAcquis;
  if(typeof cycleAdvancementJson !== "undefined" && cycleAdvancementJson !== null && afficherTableau) {
    showCycleAdvancement();
    makeCycleAdvancement(cycleAdvancementJson);
  }
}

function showCycleAdvancement(){
  $("#panel_cycle_advancement").show();
}

function makeCycleAdvancement(cycleAdvancementJson){
  var arrayTotEcts = cycleAdvancementJson.totEctsAcquis;
  var ectsAcquisCycleJson = cycleAdvancementJson.ectsAcquisCycle;
  addCycleAcquiredEcts(ectsAcquisCycleJson);
  if (arrayTotEcts !== undefined || arrayTotEcts.length > 0) {
    addAcademicYearAcquiredEcts(arrayTotEcts);
  }
}

function addCycleAcquiredEcts(ectsAcquisCycleJson){
  var cycleAcronym = ectsAcquisCycleJson.sigle;
  var cycleChargeCredits = ectsAcquisCycleJson.credAcquisCharge;
  var cycleProgressionCredits = ectsAcquisCycleJson.credAcquisProgression;
  var $frag = $(document.createDocumentFragment());
  var $cell = createJQObjectNoText("<td/>", {}, $frag);
  createJQObject("<strong/>", {}, cycleAcronym, $cell);
  $cell = createJQObjectNoText("<td/>", {}, $frag);
  createJQObject("<strong/>", {}, cycleChargeCredits, $cell);
  $cell = createJQObjectNoText("<td/>", {}, $frag);
  createJQObject("<strong/>", {}, cycleProgressionCredits, $cell);
  $frag.appendTo($("#cycle_total_credits_row"));
}

function addAcademicYearAcquiredEcts(arrayTotEcts){
  var $frag = $(document.createDocumentFragment());
  $.each(arrayTotEcts, function(index, totEcts) {
    var $row = createJQObjectNoText("<tr/>", {}, $frag);
    addRowTotEcts(totEcts, $row);
  });
  $frag.appendTo($("#cycle_advancement"));
}

function addRowTotEcts(totEcts, $row){
  var academicYear = totEcts.anac;
  var acronym = totEcts.sigle;
  var acquiredChargeCredits = totEcts.credAcquisCharge;
  var acquiredProgressionCredits = totEcts.credAcquisProgression;
  createJQObject("<td/>", {}, academicYear, $row);
  createJQObject("<td/>", {}, acronym, $row);
  createJQObject("<td/>", {}, acquiredChargeCredits, $row);
  createJQObject("<td/>", {}, acquiredProgressionCredits, $row);
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
