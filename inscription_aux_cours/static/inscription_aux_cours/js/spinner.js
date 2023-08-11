document.addEventListener('DOMContentLoaded', function () {
    initSpinnerTrigger()
});

function initSpinnerTrigger() {
    document.querySelectorAll(".slow-loading").forEach(function (value, key, parent) {
        value.addEventListener("click", showSpinner)
    });
}

function showSpinner() {
    addEventListener("beforeunload", function () {
        document.querySelector("#overlay").classList.add('overlay');
        document.querySelector("#loader").classList.add('loader');
    });

}
