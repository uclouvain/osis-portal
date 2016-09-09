
$("#rd_same_contact_legal_addr_true").click(function() {
    alert('rd_same_contact_legal_addr_true');
    $('#txt_contact_adr_street').val('');
    $('#txt_contact_adr_number').val('');
    $('#txt_contact_adr_complement').val('');
    $('#txt_contact_adr_postal_code').val('');
    $('#txt_contact_adr_city').val('');
    $('#txt_contact_adr_city').val('');
    $('#slt_contact_adr_country'+year).prop("selectedIndex",-1);
});