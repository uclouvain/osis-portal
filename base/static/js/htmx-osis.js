"use strict";

// Disable button or link
// Inspired by htmx disable-element extension
htmx.defineExtension('osis-disable-element', {
    onEvent: function (name, evt) {
        let elt = evt.detail.elt;
        let target = elt.getAttribute("hx-disable-element");
        let targetElements = (target == "self") ? [elt] : document.querySelectorAll(target);

        if (name === "htmx:beforeRequest") {
            targetElements.forEach(element => disableElement(element))
        } else if (name == "htmx:afterRequest") {
            targetElements.forEach(element => enableElement(element))
        }
    }
});


htmx.defineExtension('class-on-confirm', {
    onEvent : function(name, evt) {
        if (name === "htmx:confirm") {
            const eltSelector = evt.detail.elt.getAttribute('hx-indicator');
            const elt = document.querySelector(eltSelector);
            if (elt !== null) {
                elt.classList.add("htmx-request");
            }

        }
    }
})

function disableElement(ele) {
    if (ele.tagName === 'A') {
        ele.classList.add('disabled');
    } else {
        ele.disabled = true;
    }
}


function enableElement(ele) {
    if (ele.tagName === 'A') {
        ele.classList.remove('disabled');
    } else {
        ele.disabled = false;
    }
}

function initializeSelect2(ev) {
    const el = ev.detail.elt;
    el.querySelectorAll('[data-autocomplete-light-function=select2]').forEach(window.__dal__initialize)
}
document.addEventListener("htmx:afterSwap", initializeSelect2);