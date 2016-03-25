$("#slt_offer_type").change(function() {
    $("#grade_choices").find("label")
      .remove()
      .end()

    $.ajax({
        url: "/admission/levels?type=" + $("#slt_offer_type").val()
      }).then(function(data) {

        $.each(data, function(key, value) {
          $('#grade_choices').append($("<label></label>").attr("class", "radio-inline")
                                      .append($("<input></input>").attr("type","radio")
                                                                  .attr("name","grade_choice")
                                                                  .attr("value",value.name))
                                      .append(value.name));
        });
      });

});