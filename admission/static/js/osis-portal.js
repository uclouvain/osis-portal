$("#slt_domain").change(function() {
    var offer_type = $("#slt_offer_type").val();
    alert(offer_type);
    console.log('testtt');
    $.ajax({
            type: "POST",
            url: "/admission/admission/test/",
            data: { "offer_type": $("#slt_offer_type").val() },
            success: function(data) {
                alert(data.message);
            }

        });
    /*$.get("/test/"+this.id+"/", function(data) {
         console.log('testtt 1');
        if (data.fact_type=="T") {

        guess_result="This fact is true! " + data.fact_note;

        } else {

        guess_result="This fact is false! " + data.fact_note;

        }

        $('#result')[0].innerHTML=guess_result;

        });*/
      /*$.ajax({
        type: "GET",
              url: window.location.href ,

      success: function(msg) {
        url = window.location.href.toString();
        url = url.replace("/" + msg, "");
        url = url + "?offer_type=" + $("#slt_offer_type").val();
        console.log(url);
        console.log('test')
        window.location.replace(url);
        }

      });*/

   // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});