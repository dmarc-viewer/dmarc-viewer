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

/*
 * Copy a formset by 
 */
var copy = function(el) {
        //get the new form and form to copy
        var $formsetPlugin = $("#filterSetContainer").data("formset"),
            $oldForm = $(el).parent("[data-formset-form]"),
            $newForm = $formsetPlugin.addForm();

        //copy all selects' options
        var $selectsOld = $oldForm.find("select");
        $newForm.find("select").each(function(idx){ 
            var optionsHTML = $selectsOld[idx].innerHTML;
            if (optionsHTML)
                $(this).html(optionsHTML);

            //Handle selectize plugin
            //XXX It would be nice if selectize did this on its own
            $selectize = $(this)[0].selectize;
            $(this).find("option[selected='selected']").each(function(idx){
                $selectize.addItem($(this).val(), true);
            });
        });

        //copy all inputs' values
        var $inputsOld = $oldForm.find("input");
        $newForm.find("input").each(function(idx){ 
            var value = $inputsOld[idx].value;
            if (value)
                $(this).val(value);

            //Checkboxes
            if ($(this).attr("type") == "checkbox")
                $(this).attr('checked', $inputsOld[idx].checked)

        });

        //XXX Add support for other form elements (textarea, radio, checkbox,...)
        return $newForm;
}

/*
 * Toggle Date Range Type
 */
var toggleDateRange = function(){
    //Fixed
    var dr_type = $("[name='dr_type']:checked").val();
    if (dr_type == 1){
        $("#id_quantity, #id_unit").prop('disabled', true).val(null)
        $("#id_begin, #id_end").prop('disabled', false);
    } else if (dr_type == 2) {
        $("#id_begin, #id_end").prop('disabled', true).val(null)
        $("#id_quantity, #id_unit").prop('disabled', false);
    }
}

$(document).ready(toggleDateRange)
$(document).on("click", "[name='dr_type']", toggleDateRange)


