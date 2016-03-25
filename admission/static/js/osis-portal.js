$("#slt_offer_type").change(function() {
    $("#pnl_grade_choices").find("label")
      .remove()
      .end()

    $.ajax({
        url: "/admission/levels?type=" + $("#slt_offer_type").val()
      }).then(function(data) {
        if(data.length >0){
        $.each(data, function(key, value) {

          $('#pnl_grade_choices').append($("<label></label>").attr("class", "radio-inline")
                                      .append($("<input>").attr("type","radio")
                                                                  .attr("name","grade_choice")
                                                                  .attr("value",value.id)
                                                                  .attr("id","grade_choice_"+value.id)
                                                                  .attr("onchange","grade_choice_selection(this)"))
                                      .append(value.name));
        });
        }else{
        alert('k');
        }
      });

});


$("#slt_domain").change(function() {

         var radio_button_value;

           if ($("input[name='grade_choice']:checked").length > 0){
               radio_button_value = $('input[name="grade_choice"]:checked').val();
           }
           else{
               //radio_button_value=$("#slt_offer_type").val();
               return False
           }
           alert(radio_button_value);
    $("#pnl_offers").find("table")
      .remove()
      .end()

    $.ajax({
        url: "/admission/offers?level=" + radio_button_value +"&domain="+$("#slt_domain").val()

      }).then(function(data) {
        $('#pnl_grade_choices').append($("<table><tr><td></td></tr></table>"));
        var trHTML = '<table>';

        $.each(data, function(key, value) {
            trHTML += '<tr><td>' + value.title + '</td></tr>';
        });
        trHTML += '</table>'
        $('#pnl_offers').append(trHTML);
      });

});

function grade_choice_selection(rb){
    alert('kk1'+rb.value);
}