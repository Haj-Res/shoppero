function form_add_row(target_element, after_element) {
    $(target_element).clone(true).insertAfter(after_element);
    return false;
}

function initClickableTableRow() {
    $(".table-row").click(function () {
        window.document.location = $(this).data("href");
    });
}