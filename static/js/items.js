/**
 * Clean up data in item form and focus on name input
 * to allow easy fast multiple items insertion.
 */
function cleanItemForm() {
    const $name = $('#name');
    $name.val('');
    $('#code').val('');
    $('#price').val('');
    $('#tags').val('');
    $name.focus();
}

/**
 * Prepare a html code of a table row for a given item object and row number.
 * @param item - item object having name, code, price and tags attributes
 * @param rowNum - number of the last row in the table. 0 if empty
 * @returns {string} - html code of <td> tag ready for inserting in table
 */
function prepareItemForTable(item, rowNum) {
    rowNum = parseInt(rowNum) + 1;
    let tableRow = `<tr id="last" class="table-row item-${item.id}">`;
    tableRow += createItemTableData(item, rowNum);
    tableRow += '</tr>';
    return tableRow;
}

/**
 * Helper function of creating html code just of content inside the table row for
 * a given item with the row number of the last entry in the table.
 * @param item - item object having name, code, price and tags attributes
 * @param rowNum - number of the last row in the table. 0 if empty
 * @returns {string} html code of <td> tags for the given item
 */
function createItemTableData(item, rowNum) {
    if (item['price'] == null) {
        item['price'] = '';
    }
    let tableRow = `<th class="num" scope="row">${rowNum}</th>`;
    tableRow += `<td>${item['name']}</td>`;
    tableRow += `<td>${item['code']}</td>`;
    tableRow += `<td class="justify-text-right">${item['price']}</td>`;
    tableRow += `<td>${item['tags']}</td>`;
    tableRow += `<td>
<span data-url="${item['url']}" class="i-btn edit-item-btn"><i class="fas fa-pen"></i></span>
<span data-url="${item['url']}" class="ml-3 i-btn delete-item-btn"><i class="fas fa-trash-alt"></i></span>
</td>`;
    return tableRow;
}

/**
 * Insert a new item into the existing table
 * @param item - item object having name, code, price and tags attributes
 */
function addItemRow(item) {
    let $emptyTable = $('#table-empty');
    if ($emptyTable.length) {
        let newRow = prepareItemForTable(item, 0);
        $emptyTable.remove();
        $('tbody').html(newRow);
    } else {
        let $last = $('#last');
        let rowNum = $('#last .num').html();
        let newRow = prepareItemForTable(item, rowNum);
        $(newRow).insertAfter($last);
        initItemEditBtn();
        $last.removeAttr('id');
    }
}

/**
 * Update an existing row in the table with new item data
 * @param item - item object having name, code, price and tags attributes
 */
function updateItemRow(item) {
    const $itemRow = $(`.item-${item.id}`);
    const rowNum = $(`.item-${item.id} .num`).html();
    const itemData = createItemTableData(item, rowNum);
    $itemRow.html(itemData);
}

/**
 * Initialize the edit item button. Create a get request to fetch the
 * data of the item from the api, adjust the add/edit item form to edit mode,
 * populate the input fields with the right data and open modal.
 */
function initItemEditBtn() {
    $('.edit-item-btn').off('click').on('click', function (e) {
            let url = $(this).data('url');
            itemModalToEdit(url);
            jsonRequest(url).then(function (item) {
                $('#name').val(item.name);
                $('#code').val(item.code);
                $('#price').val(item.price);
                $('#tags').val(item.tags);
                $('#itemModal').modal('show');
            });
        }
    )
}

/**
 * Initialize the item delete button. Make a patch request to the api for a
 * item soft delete operation. Remove item row from the item table.
 */
function initItemDeleteBtn() {
    $('.delete-item-btn').off('click').on('click', function (e) {
        const url = $(this).data('url');
        const $parent = $(this).parent().parent();
        const method = 'PATCH';
        // TODO add confirmation modal
        jsonRequest(url, null, method).then(function (response) {
            const tableId = '#items-table';
            const colspan = 6;
            const emptyTableMessage = 'No items found';
            deleteRowFromTable(tableId, $parent, colspan, emptyTableMessage);
        }).catch(createSubmissionErrorToast); // TODO: handle exception besides toast
    })
}

/**
 * Change the item form action and method to adding new items
 */
function itemModalToAddNew() {
    let $form = $('#item-form');
    let url = $form.data('new');
    $form.attr('action', url);
    $form.attr('method', 'post');
    $('.modal-title').html('New Item');
}

/**
 * Change the item from action and method to edit existing item
 * @param url - url to the api for updating items
 */
function itemModalToEdit(url) {
    let $form = $('#item-form');
    $form.attr('action', url);
    $form.attr('method', 'put');
    $('.modal-title').html('Update item');
}

/**
 * Initialize the item from submit functionality. Creates a POST or PUT
 * request to the form's action url depending on whether it's adding or
 * editing an item.
 */
function postOrPutItemData() {
    $('#item-form').submit(function (e) {
        e.preventDefault();
        const form = document.querySelector('#item-form');
        if (form.checkValidity()) {
            const $form = $('#item-form');
            const $price = $('#price');
            const data = {
                name: $('#name').val(),
                code: $('#code').val(),
                price: $price.val() ? $price.val() : null,
                tags_string: $('#tags').val()
            };
            const url = $form.attr('action');
            const method = $form.attr('method').toUpperCase();
            jsonRequest(url, data, method).then(function (response) {
                if (method === 'POST') {
                    addItemRow(response);
                } else if (method === 'PUT') {
                    updateItemRow(response);
                    $('#itemModal').modal('hide');
                }
                initItemEditBtn();
                initItemDeleteBtn();
                cleanItemForm();
            }).catch(function (response) {
                const errors = response.responseJSON;
                displayErrors(errors);
            });

        }
    });
}
