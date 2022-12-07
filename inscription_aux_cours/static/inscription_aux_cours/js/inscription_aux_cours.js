document.addEventListener('DOMContentLoaded', function () {
    addTriggerForFormsEnrollToCourse(getInscrireAuCoursUrl(), getCSRFToken());
    addTriggerForFormsUnenrollToCourse(getDesinscrireAuCoursUrl(), getCSRFToken());
    addLoaderElement();
    alignCoursAJoutesTables();
}, false);


function alignCoursAJoutesTables() {
    const tableCoursAjoutes = document.querySelectorAll("table.cours-ajoutes");
    tableCoursAjoutes.forEach((table, key, parent) => {
        const headerTableFormulaire = table.closest("div").previousElementSibling.querySelector("thead");
        const headerTable = table.querySelector("thead");
        alignCoursAjoutesTable(headerTable, headerTableFormulaire)
    });
}

function alignCoursAjoutesTable(headerTableCoursAjoutes, headerTableFormulaire) {
    headerTableCoursAjoutes.querySelector("th:nth-child(1)").style.width = getComputedStyle(headerTableFormulaire.querySelector("th:nth-child(1)")).width;
    headerTableCoursAjoutes.querySelector("th:nth-child(2)").style.width = getComputedStyle(headerTableFormulaire.querySelector("th:nth-child(2)")).width;
    headerTableCoursAjoutes.querySelector("th:last-child").style.width = getComputedStyle(headerTableFormulaire.querySelector("th:last-child")).width;

}

function addLoaderElement() {
    const forms = document.querySelectorAll(".formulaire-inscription-cours")
    forms.forEach((form, key, parent) => {
        form.insertAdjacentHTML(
            'beforeend',
            "<div class='loading'></div>"
        )
    });
}


function getInscrireAuCoursUrl() {
    if (document.querySelector(".panel-formulaires-inscription-cours") !== null) {
        return document.querySelector(".panel-formulaires-inscription-cours").dataset.urlInscrireCours;
    }
    return ""
}

function getDesinscrireAuCoursUrl() {
    if (document.querySelector(".panel-formulaires-inscription-cours") !== null) {
        return document.querySelector(".panel-formulaires-inscription-cours").dataset.urlDesinscrireCours;
    }
    return ""
}

function getCSRFToken() {
    if (document.querySelector(".panel-formulaires-inscription-cours") !== null) {
        return document.querySelector(".panel-formulaires-inscription-cours").dataset.csrfToken;
    }
    return ""
}

function addTriggerForFormsEnrollToCourse(postUrl, csrfToken) {
    const forms = document.querySelectorAll(".formulaire-inscription-cours[data-est-inscrit='False']")
    forms.forEach((value, key, parent) => {
        addTriggerOnForm(value, postUrl, csrfToken)
    });
}

function addTriggerForFormsUnenrollToCourse(postUrl, csrfToken) {
    const forms = document.querySelectorAll(".formulaire-inscription-cours[data-est-inscrit='True']")
    forms.forEach((value, key, parent) => {
        addTriggerOnForm(value, postUrl, csrfToken)
    });
}

function addTriggerOnForm(formElement, postUrl, csrfToken) {
    const codeCours = formElement.dataset.codeCours;
    const codeMiniFormation = formElement.dataset.codeMiniFormation;
    const target = `#div-inscription-${codeMiniFormation}-${ codeCours }`

    triggerHtmxPostOnClick(
        formElement,
        postUrl,
        target,
        {'code_mini_formation': codeMiniFormation, 'code_cours': codeCours},
        {"X-CSRFToken": csrfToken}
    )
}

function triggerHtmxPostOnClick(e, postUrl, target, values, headers) {
    e.addEventListener('click', (event) => {
       htmx.ajax('POST', postUrl, {'source': e, 'target': target, 'swap': 'outerHTML', 'values': values, 'headers': headers})
    });
}

