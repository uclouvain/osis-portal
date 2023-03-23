document.addEventListener('DOMContentLoaded', function () {
    styleRow();
    addTriggerForFormsEnrollToCourse(getInscrireAuCoursUrl(), getCSRFToken());
    addTriggerForFormsUnenrollToCourse(getDesinscrireAuCoursUrl(), getCSRFToken());
    addLoaderElement();
    initPopover();

    htmx.defineExtension('class-on-confirm', {
        onEvent : function(name, evt) {
            if (name === "htmx:confirm") {
                const eltSelector = evt.detail.elt.getAttribute('hx-indicator');
                const elt = document.querySelector(eltSelector);
                elt.classList.add("htmx-request");
            }
        }
    });

}, false);


function initPopover() {
    $('[data-toggle="popover"]').popover();
}

function addLoaderElement() {
    const forms = document.querySelectorAll(".formulaire-inscription-cours")
    forms.forEach((form, key, parent) => {
        form.insertAdjacentHTML(
            'afterbegin',
            "<div class='loading pull-left'></div>"
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
    const target = `#form-inscription-${codeMiniFormation}-${ codeCours }`

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
       e.classList.add('htmx-request');
    });
}


document.addEventListener("htmx:afterSwap", styleRow)
function styleRow() {
    document.querySelectorAll('.desinscrit').forEach((el)=>el.closest('tr').style.backgroundColor='');
    document.querySelectorAll('.badge_insc_meme_context').forEach((el)=>el.closest('tr').style.backgroundColor="rgba(3,51,173, 0.07)");
    document.querySelectorAll('.badge_insc_meme_context').forEach((el)=>el.style.backgroundColor="rgba(3,51,173,0.5)");
    document.querySelectorAll('.badge_insc_different_context').forEach((el)=>el.closest('tr').style.backgroundColor="rgba(46,174,213, 0.07)");
    document.querySelectorAll('.badge_insc_different_context').forEach((el)=>el.style.backgroundColor="rgba(46,174,213,0.87)");
    document.querySelectorAll('.badge_insc_credite_meme_context, .badge_val_meme_context').forEach((el)=>el.closest('tr').style.backgroundColor="rgba(18, 119, 22, 0.07)");
    document.querySelectorAll('.badge_insc_credite_meme_context, .badge_val_meme_context').forEach((el)=>el.style.backgroundColor="rgba(18, 119, 22, 0.5)");
    document.querySelectorAll('.badge_insc_credite_different_context, .badge_val_different_context').forEach((el)=>el.closest('tr').style.backgroundColor="rgba(138, 188, 62, 0.07)");
    document.querySelectorAll('.badge_insc_credite_different_context, .badge_val_different_context').forEach((el)=>el.style.backgroundColor="rgba(138, 188, 62, 1)");
}
