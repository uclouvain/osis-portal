document.addEventListener('DOMContentLoaded', function () {
    styleRow();
    initPopover();
}, false);

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

function initPopover() {
    $('[data-toggle="popover"]').popover();
}
