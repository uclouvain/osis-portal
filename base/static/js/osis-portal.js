$.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

document.addEventListener("htmx:afterSwap",function (e,) {
    $(e.target).find('[data-toggle="tooltip"]').tooltip()
});

// disable pagination page links when out of bound
document.querySelectorAll('.disabled a').forEach(
    (el) => el.removeAttribute("href")
);

$(".keep-popover-display").popover(
    {
        trigger: "manual",
        html: true,
        animation: true
    }
).on("mouseenter", function() {
    var _this = this;
    $(this).popover("show");
    $(".popover").on("mouseleave", function() {
        $(_this).popover('hide');
    });
}).on("mouseleave", function() {
    var _this = this;
    setTimeout(
        function() {
            if (!$(".popover:hover").length) {
                $(_this).popover("hide");
            }
        },
        500
    );
});
