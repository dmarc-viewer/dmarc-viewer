/*
 * Copy a formset by
 */
var editor = {
    /*
     * Copy a dmarc viewer filterset using djangoformsetjs' addForm function,
     * copying the form field values from the formset enclosing the
     * copy button to the newly added form
     *
     */
    copyFilterSet: function(clickedElement) {
        //Query the formset container (old and new)
        var container = "#filterSetContainer";

        // Add one-time listener for the formAdded Event, triggered
        // at the end of this function
        // Copying on formAdded Event guarantees that the elements of the new
        // form have been initialized in the DOM and can be fully used, which
        // is crucial when copying selectize elements
        $(document).one("formAdded", container, function(event) {
            var $newForm = $(event.target);
            var $oldForm = $(clickedElement)
                    .closest("[data-formset-form]");

            // Copy plain input fields
            ["filter_label", "filter_color", "filter_source_ip"].forEach(
                function(filter_class) {
                    var selector = "." + filter_class + " input";
                    $newForm.find(selector).val(
                        $oldForm.find(selector).val()
                    );
                }
            );

            // Copy select elements
            ["filter_report_receiver_domain", "filter_report_sender",
                    "filter_raw_spf_domain", "filter_raw_spf_result",
                    "filter_raw_dkim_domain", "filter_raw_dkim_result",
                    "filter_aligned_spf_result", "filter_aligned_dkim_result",
                    "filter_disposition"].forEach(function(filter_class) {

                var selector = "." + filter_class + " select";
                var $newSelect = $newForm.find(selector);
                var $newSelectize = $newSelect[0].selectize;

                var $oldSelect = $oldForm.find(selector);
                var $oldSelectize = $oldSelect[0].selectize;

                // Copy each option of the select from the source filter set
                // to the new copied filter set (addOption), and toggle
                // selection accordingly (addItem), using the selectize API
                for (var key in $oldSelectize.options) {
                    var value = $oldSelectize.options[key]["value"];
                    var text = $oldSelectize.options[key]["text"];

                    // Add dynamically retrieved selectize options
                    // No-op if the option already exists, e.g. was available
                    // via <option> element
                    $newSelectize.addOption({
                        value: value,
                        text: text
                    });

                    // Select previously selected items
                    if ($oldSelectize.items.indexOf(value) != -1) {
                        $newSelectize.addItem(value, true);
                    }
                    $newSelectize.refreshItems();
                }

                // Copy vanilla checkbox
                var selector = "." + "filter_multiple_dkim input";
                $newForm.find(selector).prop("checked",
                        $oldForm.find(selector).is(":checked"));
            });
        });

        // Add new empty formset to DOM, which triggers above listener to copy
        // the fields from the old formset, whose copy button was clicked
        $(container).data("formset").addForm();
    },
    /*
     * Toggle Date Range Type
     * Disable input fields of deselected date range type
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
        if (!str.length || str.length < 3) return;
        editor._xhr && editor._xhr.abort();
        this.load(function(callback) {
            editor._xhr = $.ajax({
                url: this.settings.load_action,
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
