document.addEventListener('DOMContentLoaded', function () {
    styleRow();
    initPopover();
}, false);

document.addEventListener("htmx:afterSwap", styleRow)

const COLOR_BADGE_INSC = "rgba(3,51,173,0.07)";

function styleRow() {
    document.querySelectorAll('.non-inscrit').forEach((el)=>el.closest('tr').style.backgroundColor="");
    document.querySelectorAll('.badge_insc_meme_context').forEach((el)=>el.closest('tr').style.backgroundColor=COLOR_BADGE_INSC);
    document.querySelectorAll('.badge_insc_meme_context').forEach((el)=>el.style.backgroundColor="rgba(3,51,173,0.5)");
    document.querySelectorAll('.badge_insc_different_context').forEach((el)=>el.closest('tr').style.backgroundColor="rgba(46,174,213, 0.07)");
    document.querySelectorAll('.badge_insc_different_context').forEach((el)=>el.style.backgroundColor="rgba(46,174,213,0.87)");
    document.querySelectorAll('.insc_credite_meme_context, .val_meme_context').forEach((el)=>el.closest('tr').style.backgroundColor="rgba(0, 102, 68, 0.07)");
    document.querySelectorAll('.badge_insc_credite_meme_context, .badge_val_meme_context').forEach((el)=>el.style.backgroundColor="rgba(0, 102, 68, 1)");
    document.querySelectorAll('.insc_credite_different_context, .val_different_context').forEach((el)=>el.closest('tr').style.backgroundColor="rgba(171, 245, 209, 0.2)");
    document.querySelectorAll('.badge_insc_credite_different_context, .badge_val_different_context').forEach((el)=>{el.style.backgroundColor="rgba(171, 245, 209, 1)";el.style.color="black";});
}

function initPopover() {
    $('[data-toggle="popover"]').popover();
}
