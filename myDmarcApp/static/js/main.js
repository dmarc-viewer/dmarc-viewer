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
        });

        //XXX Add support for other form elements (textarea, radio, checkbox,...)
        return $newForm;
}
