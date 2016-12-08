$('document').ready(function(){
    init_profession_fields();
});

function init_profession_fields(){
    init_profession_field('father_profession');
    init_profession_field('mother_profession');
    init_profession_field('student_profession');
    init_profession_field('conjoint_profession');
    init_profession_field('paternal_grandfather_profession');
    init_profession_field('maternal_grandfather_profession');
}

function init_profession_field(profession){
    chb_profession_other = $('#chb_'+profession+'_other');
    adhoc = chb_profession_other.prop( "checked")?'True':'False';
    display_hide_other_profession(profession, adhoc);
}

function display_hide_other_profession(profession,adhoc){
    prof_slt = $("#slt_"+profession);
    prof_other_div = $("#div_"+profession+"_other");
    if(adhoc == 'True'){
        prof_slt.prop( "disabled", true);
        prof_slt.prop("selectedIndex",-1);
        prof_other_div.css('visibility', 'visible').css('display','block');
    }else{
        prof_slt.prop( "disabled", false);
        prof_other_div.css('visibility', 'hidden').css('display','none');
    }
}

$('[id^="chb_"][id$="_other"]').change(function() {
     profession = this.id.replace('chb_','').replace('_other','');
     adhoc = this.checked?'True':'False';
     display_hide_other_profession(profession, adhoc);
});
