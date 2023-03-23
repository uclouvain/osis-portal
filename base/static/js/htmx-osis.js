"use strict";

// Disable button or link
// Inspired by htmx disable-element extension
htmx.defineExtension('osis-disable-element', {
    onEvent: function (name, evt) {
        let elt = evt.detail.elt;
        let target = elt.getAttribute("hx-disable-element");
        let targetElement = (target == "self") ? elt : document.querySelector(target);

        if (name === "htmx:beforeRequest" && targetElement) {
            disableElement(targetElement);
        } else if (name == "htmx:afterRequest" && targetElement) {
            enableElement(targetElement);
        }
    }
});

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
