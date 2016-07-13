function display_results(data){
    display_nav_tabs(data);
    display_tab_panes(data);
}

/********************  NAVIGATION TABS *******************/

function display_nav_tabs(data){
    var $nav_tabs = $("<ul/>", {
                        id: "nav_tabs",
                        "class": "nav nav-tabs",
                        role: "tablist"
                    });
    $nav_tabs.appendTo("#div_results");

    academic_years = data.academic_years; // TO MODIFY
    $.each(academic_years, function(index, academic_year){
        var $tab = $("<li/>", {
                        role: "presentation"
                    });
        if (index == 0){
            $tab.attr("class", "active");
        }
        $tab.appendTo($nav_tabs);

        var $a = $("<a/>", {
                    href: "#year"+index.toString(),
                    "aria-controls": "year"+index.toString(),
                    role: "tab",
                    "data-toggle": "tab"
                 });
        $a.text(academic_year.programme);
        $a.appendTo($tab);
    });
}

/**************** COURSES SCORE TABLE  *************/


function display_tab_panes(data){
    academic_years = data.academic_years;

    var $div_tab_content = $("<div/>", {
                                id: "div_tab_content",
                                "class": "tab-content"
                            });
    $div_tab_content.appendTo("#div_results");

    $.each(academic_years, function(index, academic_year) {
        var $div_tab_panel = $("<div/>", {
                                id: "year"+index.toString(),
                                "class": "tab-pane",
                                role: "tabpanel"
                             });
        if(index == 0){
            $div_tab_panel.attr("class", "tab-pane active");
        }
        $div_tab_panel.appendTo($div_tab_content);

        //table of courses with results
        var $table = display_table($div_tab_panel);
        fill_table(academic_year, $table);

        //table of summary of results
        display_summary_results(academic_year, $div_tab_panel)
    });
}

function display_table(parent){
    $div_table_responsive = $("<div/>", {
                                id: "div_table_responsive_" + parent.get(0).id,
                                "class": "table-responsive"
                            });
    $div_table_responsive.appendTo(parent);

    var $table = $("<table/>", {
                    "class": "table table-striped table-bordered table-hover"
                 });
    $table.appendTo($div_table_responsive);

    var $table_row_header = $("<tr/>");
    $table_row_header.appendTo($table);

    var headers = ["Cours", "Intitulé", "ECTS", "Insc.", "Janv", "Juin", "Sept", "Crédit"];
    $.each(headers, function(index, header) {
        var $table_element = $("<th/>");
        $table_element.text(header);
        $table_element.appendTo($table_row_header);
    });
    return $table.get(0);
}

function fill_table(data, $table){
    var courses = data.learning_units
    $.each(courses, function(index, course){
        var $table_row = $("<tr/>");
        $table_row.appendTo($table);
        var table_row = $table_row.get(0);
        table_row.insertCell(0).textContent = course.acronym;
        table_row.insertCell(1).textContent = course.title;
        table_row.insertCell(2).textContent = course.credits;
        table_row.insertCell(3).textContent = "Inscr";
        table_row.insertCell(4).textContent = course.exams[0].score;
        table_row.insertCell(5).textContent = course.exams[1].score;
        table_row.insertCell(6).textContent = course.exams[2].score;
        table_row.insertCell(7).textContent = "Crédit";
    });
}

/**************** SUMMARY TABLE  *************/


function display_summary_results(data, $parent){
    var $table = display_summary_table($parent);
    fill_summary_table(data, $table.get(0));
}

function display_summary_table(parent){
    var $div_summary_results = $("<div/>", {
                                    "class": "row"
                               });
    $div_summary_results.appendTo(parent);

    var $div_positionement = $("<div/>", {
                                    "class": "col-md-4 col-md-offset-4"
                               });
    $div_positionement.appendTo($div_summary_results);

    var $div_table_responsive = $("<div/>", {
                                    "class": "table-responsive"
                               });
    $div_table_responsive.appendTo($div_positionement);

    var $table = $("<table/>", {
                    "class": "table table-striped table-condensed"
                });
    $table.appendTo($div_table_responsive);

    return $table;
}


function fill_summary_table(data, table){
    fill_row_credits(data, table);
    fill_row_date_sessions(table);
    fill_row_mean_scores(data, table);
    fill_row_mention(data, table);
}

//display the row showing total credits done this year
function fill_row_credits(data, table){
    var table_row = table.insertRow(0);
    table_row.insertCell(0).textContent = "Crédits";
    table_row.insertCell(1).textContent = "-";
    table_row.insertCell(2).textContent = "-";
    table_row.insertCell(3).textContent = "-";
}


//display the row showing the dates of session
function fill_row_date_sessions(table){
    var table_row = table.insertRow(1);
    table_row.insertCell(0).textContent = " ";
    table_row.insertCell(1).textContent = "Janv";
    table_row.insertCell(2).textContent = "Juin";
    table_row.insertCell(3).textContent = "Sept";
}

//display the row showing the mean scores
function fill_row_mean_scores(data, table){
    var table_row = table.insertRow(2);
    table_row.insertCell(0).textContent = "Moyenne";
    table_row.insertCell(1).textContent = "-";
    table_row.insertCell(2).textContent = "-";
    table_row.insertCell(3).textContent = "-";
}


//display the row showing the mention
function fill_row_mention(data, table){
    var table_row = table.insertRow(3);
    table_row.insertCell(0).textContent = "Mention";
    table_row.insertCell(1).textContent = "-";
    table_row.insertCell(2).textContent = "-";
    table_row.insertCell(3).textContent = "-";
}