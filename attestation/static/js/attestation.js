
$('[id^=btn_attestation_download_]').each(function(index){
   $(this).click(function(){
       var attestation_type =  this.id.replace(/btn_attestation_download_/,'');
       var elem_id = "#attestation_printed_".concat(attestation_type);
       setTimeout(function(){$(elem_id).attr("class","fa fa-check");}, 500);
   });
});