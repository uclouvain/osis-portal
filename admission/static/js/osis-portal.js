$("#slt_domain").change(function() {
    alert('k1k');
      $.ajax({
        type: "GET",
              url: window.location.href,
      success: function(msg) {
        url = window.location.href.toString();
        url = url.replace("/" + msg, "");
        console.log(url);
        window.location.replace(url);
        }

      });


});