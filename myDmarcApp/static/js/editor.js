/*
 * Copy a formset by 
 */
var editor = {
    copyFilterSet: function(el) {
        //get the new form and form to copy
        var $formsetPlugin = $("#filterSetContainer").data("formset"),
            $oldForm = $(el).closest("[data-formset-form]"),
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

        //XXX Add support for other form elements (textarea, radio, ...)
        return $newForm;
    },
    /*
     * Toggle Date Range Type
     */
    toggleDateRange: function(){
        //Fixed
        var dr_type = $("[name='dr_type']:checked").val();
        $("[name='dr_type']").closest(".radio").removeClass("active")
        if (dr_type == 1){
            $("[name='dr_type']:checked").closest(".radio").addClass("active")
            $("#id_quantity, #id_unit").prop('disabled', true).val(null)
            $("#id_begin, #id_end").prop('disabled', false);
        } else if (dr_type == 2) {
            $("[name='dr_type']:checked").closest(".radio").addClass("active")
            $("#id_begin, #id_end").prop('disabled', true).val(null)
            $("#id_quantity, #id_unit").prop('disabled', false);
        }
    },
    /*
     * Show only selectize options that are relevant for report type
     * XXX LP: it would be nicer to load and change them via ajax (+chache)
     *         especially if the list is very very long
     */
    toggleReportTypeOptGroups: function(evt){
        $("#viewFilterForm").attr("data-hide-incoming", false)
                            .attr("data-hide-outgoing", false);

        if ($("[name='report_type']").val() == "1")
            $("#viewFilterForm").attr("data-hide-outgoing", true);
        if ($("[name='report_type']").val() == "2")
            $("#viewFilterForm").attr("data-hide-incoming", true);
    }
}
