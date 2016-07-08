function display_results(data){
    display_nav_tabs(data);
    display_tab_panes(data);
}

function display_nav_tabs(data){
    var nav_tabs = document.createElement("UL");
    nav_tabs.id = "nav_tabs";
    nav_tabs.setAttribute("class", "nav nav-tabs");
    nav_tabs.setAttribute("role", "tablist");
    document.getElementById("div_results").appendChild(nav_tabs);

    var t = document.createElement("LI");
    t.setAttribute("class", "active");
    t.setAttribute("role", "presentation");
    nav_tabs.appendChild(t);

    var a = document.createElement("A");
    a.setAttribute("href", "#ma1");
    a.setAttribute("aria-controls", "home");
    a.setAttribute("role", "tab");
    a.setAttribute("data-toggle", "tab");
    a.textContent = data.programme;
    t.appendChild(a);
}

function display_tab_panes(data){
    var div_tab_content = document.createElement("DIV");
    div_tab_content.id = "div_tab_content";
    div_tab_content.setAttribute("class", "tab-content");
    document.getElementById("div_results").appendChild(div_tab_content);

    var div_tab_panel = document.createElement("DIV");
    div_tab_panel.id = "ma1";
    div_tab_panel.setAttribute("role", "tabpanel");
    div_tab_panel.setAttribute("class", "tab-pane active");
    div_tab_content.appendChild(div_tab_panel);

    var table = display_table(div_tab_content);
    fill_table(data, table);
}

function display_table(parent){
    var div_table_responsive = document.createElement("DIV");
    div_table_responsive.id = "div_table_responsive_" + parent.id
    div_table_responsive.setAttribute("class", "table-responsive");
    parent.appendChild(div_table_responsive);

    var table = document.createElement("TABLE");
    table.setAttribute("class", "table table-striped table-bordered table-hover");
    div_table_responsive.appendChild(table);

    var table_row_header = table.insertRow(0);

    var headers = ["Cours", "Intitulé", "ECTS", "Insc.", "Janv", "Juin", "Sept", "Crédit"];
    for (i=0; i < headers.length; i++) {
        var table_element = document.createElement("TH");
        table_element.textContent = headers[i];
        table_row_header.appendChild(table_element);
    }
    return table;
}

function fill_table(data, table){
    var courses = data.learning_units
    for( i = 0; i < courses.length; i++){
        var table_row = table.insertRow(i+1);
        table_row.insertCell(0).textContent = courses[i].acronym;
        table_row.insertCell(1).textContent = courses[i].title;
        table_row.insertCell(2).textContent = courses[i].credits;
        table_row.insertCell(3).textContent = "Inscr";
        table_row.insertCell(4).textContent = courses[i].exams[0].score;
        table_row.insertCell(5).textContent = courses[i].exams[1].score;
        table_row.insertCell(6).textContent = courses[i].exams[2].score;
        table_row.insertCell(7).textContent = "Crédit";
    }
}

function display_summary_results(data){
    var table = display_summary_table();
    fill_summary_table(data, table);
}

function display_summary_table(){
    var div_summary_results = document.createElement("DIV");
    div_summary_results.setAttribute("class", "row");
    document.getElementById("div_results").appendChild(div_summary_results);

    var div_positionement = document.createElement("DIV");
    div_positionement.setAttribute("class", "col-md-4 col-md-offset-4");
    div_summary_results.appendChild(div_positionement);

    var div_table_responsive = document.createElement("DIV");
    div_table_responsive.setAttribute("class", "table-responsive");
    div_positionement.appendChild(div_table_responsive);

    var table = document.createElement("TABLE");
    table.setAttribute("class", "table table-striped table-condensed");
    div_table_responsive.appendChild(table);

    return table;
}

function fill_summary_table(data, table){
    fill_row_credits(data, table);
    fill_row_date_sessions(table);
    fill_row_mean_scores(data, table);
    fill_row_mention(data, table);
}

function fill_row_credits(data, table){
    var table_row = table.insertRow(0);
    table_row.insertCell(0).textContent = "Crédits";
    table_row.insertCell(1).textContent = "60";
    table_row.insertCell(2).textContent = "-";
    table_row.insertCell(3).textContent = "-";
}

function fill_row_date_sessions(table){
    var table_row = table.insertRow(1);
    table_row.insertCell(0).textContent = " ";
    table_row.insertCell(1).textContent = "Janv";
    table_row.insertCell(2).textContent = "Juin";
    table_row.insertCell(3).textContent = "Sept";
}

function fill_row_mean_scores(data, table){
    var table_row = table.insertRow(2);
    table_row.insertCell(0).textContent = "Moyenne";
    table_row.insertCell(1).textContent = "-";
    table_row.insertCell(2).textContent = "15.0";
    table_row.insertCell(3).textContent = "-";
}

function fill_row_mention(data, table){
    var table_row = table.insertRow(3);
    table_row.insertCell(0).textContent = "Mention";
    table_row.insertCell(1).textContent = "-";
    table_row.insertCell(2).textContent = "D";
    table_row.insertCell(3).textContent = "-";
}