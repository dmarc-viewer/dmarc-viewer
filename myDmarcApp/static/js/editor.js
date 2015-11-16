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

            //HTML select
            var optionsHTML = $selectsOld[idx].innerHTML;
            if (optionsHTML)
                $(this).html(optionsHTML);

            //Selectize
            //XXX LP: It would be nice if selectize did this on its own
            $selectizeNew = $(this)[0].selectize;
            if ($selectizeNew != 'undefined') {
                //options - Available options in dropdown - {text: <>, value: <> }
                oldOptions = $selectsOld[idx].selectize.options;
                for (optionName in oldOptions) {
                    $selectizeNew.addOption({
                        text: oldOptions[optionName].text, 
                        value: oldOptions[optionName].value
                    });
                }

                //items - selected options in input -  <value>
                oldItems   = $selectsOld[idx].selectize.items;
                oldItems.forEach(function(item){
                    $selectizeNew.addItem(item);
                });
            }
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
     * Disable input fields of deslected date range type 
     * 1: variable
     * 2: fixed
     * Add/Remove some classes for css
     * 
     */
    toggleDateRange: function(){
        //Fixed
        var dr_type = $("[name='dr_type']:checked").val();
        $("[name='dr_type']").closest(".radio").removeClass("active")

        if (dr_type == 1){
            $("[name='dr_type']:checked").closest(".radio").addClass("active");
            $("#id_quantity, #id_unit").prop('disabled', true).val(null);
            $("#id_quantity_container, #id_unit_container").addClass("disabled");

            $("#id_begin, #id_end").prop('disabled', false);
            $("#id_begin_container, #id_end_container").removeClass("disabled");

        } else if (dr_type == 2) {
            $("[name='dr_type']:checked").closest(".radio").addClass("active");
            $("#id_begin, #id_end").prop('disabled', true).val(null);
            $("#id_begin_container, #id_end_container").addClass("disabled");

            $("#id_quantity, #id_unit").prop('disabled', false);
            $("#id_quantity_container, #id_unit_container").removeClass("disabled");

        }
    },
    /*
     * Load choices from server
     */
    _xhr: null,
    loadChoices: function(str){
        if (!str.length) return;
        editor._xhr && editor._xhr.abort();
        this.load(function(callback) {
            editor._xhr = $.ajax({
                url: '/choices-async/',
                data: {
                    report_type : $("[name='report_type']").val(),
                    choice_type : this.settings.load_choice_type,
                    query_str  : str
                },
                success: function(results) {
                    var choices = results.choices.map(function(obj){
                        return {value: obj, text: obj};
                    });
                    callback(choices);
                },
                error: function() {
                    callback();
                }
            });
        });
    }
}
