/*
 ***********************************************
 * Managing shopping lists form helper functions
 ***********************************************
 */

/**
 * Initialize button for archive the corresponding shopping list
 */
function initListArchiveBtn() {
    $('.archive-list').on('click', function (e) {
        const url = $(this).data('url');
        deleteOrArchiveList(url, 'PATCH', 'List archived');
    })
}


/**
 * Initialize button for showing delete confirmation modal
 */
function initListDeleteBtn() {
    $('.delete-list').off('click').on('click', function (e) {
        $('.btn-ok').data('url', $(this).data('url'));
        $('#confirm-delete').modal('show');
    })
}

/**
 * Permanently delete a shopping list
 */
function initListDeleteConfirmBtn() {
    $('.btn-ok').on('click', function (e) {
        const url = $(this).data('url');
        deleteOrArchiveList(url, 'DELETE', 'List deleted');
    })
}

/**
 * Helper function for deleting or archiving a list
 * @param url - string value of the api endpoint
 * @param method - string name of the method (patch or delete)
 * @param toastMessage - string message to be shown to the user
 */
function deleteOrArchiveList(url, method, toastMessage) {
    jsonRequest(url, null, method).then(function (response) {
        const table = generateShoppingListTable(response.content);
        $('#shopping-list-table tbody').html(table);
        initListArchiveBtn();
        initListDeleteBtn();
        initClickableShoppingListCell();
        $('.modal').modal('hide');
        createToastMessage(toastMessage, 'info');
    });
}

/**
 * Generate the html code for the table containing all items in
 * in the curent list
 * @param items - array of item objects
 * @returns {string} html code ready to be inserted in the table body tag
 */
function generateShoppingListTable(items) {
    let table = '';
    if (items.length > 0) {
        items.forEach(item => {
            let row = '<tr class="table-row">';
            row += `<td>${item.shopping_list__name}</td>`;
            row += `<td>${item.complete_item_count}/${item.item_count}</td>`;
            row += `<td>${item.total_price}</td>`;
            row += `<td>
                <a class="i-btn" href="${item.url}"><i class="fas fa-pen"></i></a>
                <span class="i-btn archive-list" data-url="${item.url}"><i class="fas fa-archive"></i></span>
                <span class="i-btn delete-list" data-url="${item.url}"><i class="fas fa-trash-alt"></i></span>
                </td>`;
            row += '</tr>';
            table += row;
        });
    } else {
        const link = $('#new-list').attr('href');
        table = `<tr id="table-empty"><td class="table-data" colspan="4">
            Click <a href="${link}">here</a> to add a new 
            list and start using the site.
            </td></tr>`
    }

    return table;
}

/**
 * Allow user to click whole row of a table and redirect the
 * user to the clicked list view
 */
function initClickableShoppingListCell() {
    $('.clickable').on('click', function (e) {
        window.location.href = $(this).data('url');
    })
}

/*
 ******************************************
 Autocomplete items search helper functions
 ******************************************
 */

/**
 * Initialize item search for the shopping list form.
 * Creates a get request to the api after user enters anything in the
 * item name input as long as the input is longer or equal to 3 character.
 */
function initItemAutocompleteSearch() {
    const $elem = $('#item-name');
    $elem.on('input', function (e) {
        const val = $elem.val();
        if (val.length >= 3) {
            let url = $elem.data('url') + `?name=${val}`;
            const method = 'GET';
            jsonRequest(url, null, method).then(function (response) {
                const dataList = itemListToDataList(response);
                $('#item-datalist').html(dataList);
            });
        }
    })
}

/**
 * Helper function to convert the returned item search list
 * to a list of html options tags
 * @param items
 * @returns {string}
 */
function itemListToDataList(items) {
    let dataList = '';
    items.forEach(item => {
        dataList += `<option data-id="${item.id}" data-code="${item.code}" 
data-price="${item.price}">${item.name}</option>`;
    });
    return dataList;
}

/*
 *************************************
 Adding items to list helper functions
 *************************************
 */

/**
 * Function for adding items to the shopping list table.
 * @param rowMap - map necessary for editing rows in the
 * shopping list items table
 */
function initAddItemToListForm(rowMap) {
    const formSelector = '#shopping-list-item-form';
    $(formSelector).submit(function (e) {
        e.preventDefault();
        const form = document.querySelector(formSelector);
        if (form.checkValidity()) {
            const $itemName = $('#item-name');
            const $code = $('#code');
            const $quantity = $('#quantity');
            const $price = $('#price');
            const item = {
                id: $itemName.attr('data-id') ? $itemName.attr('data-id') : '',
                name: $itemName.val().trim(),
                code: $code.val(),
                quantity: $quantity.val() ? parseFloat($quantity.val()) : 1,
                price: $price.val(),
                is_done: $('#is-done').prop('checked')
            };
            const row = createShoppingListItemRow(item);
            addRowToTable('items', row);
            initDeleteItemRow();
            clearShoppingListItemForm();
            initToggleItemDone();
            initEditListEditItemRow(rowMap);
        }
    });
}

/**
 * Delete an item row form the shopping list table
 */
function initDeleteItemRow() {
    $('.delete-item-btn-row').off('click').on('click', function (e) {
        const $parent = $(this).parent().parent();
        const tableId = 'items';
        const colspan = 6;
        const emptyTableMessage = 'No items';
        deleteRowFromTable(tableId, $parent, colspan, emptyTableMessage);
    })
}

/**
 * Clear the shopping list add item form and focus on name for
 * easy and fast item addition.
 */
function clearShoppingListItemForm() {
    const $name = $('#item-name');
    $name.val('');
    $('#code').val('');
    $('#quantity').val('');
    $('#price').val('');
    $('#is-done').prop('checked', false);
    $name.focus()
}

/**
 * Method that generates a list of items based on item data rows in the
 * shopping list table
 * @returns {[]}
 */
function collectShoppingListItemValues() {
    const $editRow = $('.cancel-btn').not('#tmpl-action .cancel-btn');
    if ($editRow.length) {
        $editRow.trigger('click');
    }
    const $dataRows = $('.data');
    const items = [];
    $.each($dataRows, function (_, row) {
        const item = {
            link_id: $(row).attr('data-link') ? $(row).attr('data-link') : null,
            item_id: $(row).attr('data-item-id') ? $(row).attr('data-item-id') : null,
            name: $(row).children('.item-name').attr('data-value'),
            code: $(row).children('.item-code').attr('data-value'),
            quantity: $(row).children('.item-quantity').attr('data-value'),
            is_done: $(row).children('.item-done').attr('data-value') === 'True'
        };
        const price = $(row).children('.item-price').attr('data-value');
        if (!isNaN(price)) {
            item['price'] = parseFloat(price);
        }
        items.push(item);
    });
    return items;
}

/**
 * Helper function that generates the HTML code of td tags for
 * a single item row
 * @param item
 * @returns {string}
 */
function createShoppingListItemRow(item) {
    let is_done = '';
    if (item.is_done) {
        is_done = '<i class="fa-15x text-success fas fa-check-circle"></i>'
    } else {
        is_done = '<i class="fa-15x text-danger far fa-times-circle"></i>'
    }
    let tableRow = `<tr class="data" id="last" data-item-id="${item.id}" data-link>`;
    tableRow += `<td class="item-name" data-value="${item.name}">${item.name}</td>`;
    tableRow += `<td class="item-code" data-value="${item.code}">${item.code}</td>`;
    tableRow += `<td class="item-quantity" data-value="${item.quantity}">${item.quantity}</td>`;
    tableRow += `<td class="item-price" data-value="${item.price}">${item.price}</td>`;
    tableRow += `<td class="i-btn item-done toggle-done justify-text-center" data-value="${item.is_done ? "True" : "False"}">${is_done}</td>`;
    tableRow += '<td><span class="i-btn mr-3 edit-item-row"><i class="fas fa-pen"></i></span>' +
        '<span class="i-btn delete-item-btn-row"><i class="fas fa-trash-alt"></i></span></td>';
    tableRow += '</tr>';
    return tableRow;
}

/**
 * Helper function that populates the item addition form
 * in the shopping list view when an item from the search list
 * is selected.
 */
function itemInputOnChange() {
    const $elem = $('#item-name');
    $elem.change(function () {
        const options = $('#item-datalist option');
        if (options.length === 0) {
            $('#item-name').removeAttr('data-id');
        } else {
            options.each(function (index) {
                const text = ($(this).text());
                if (text.toLowerCase() === $elem.val().toLowerCase()) {
                    $('#item-name').attr('data-id', $(this).data('id'));
                    $('#price').val($(this).data('price'));
                    $('#code').val($(this).data('code'));
                }
            })
        }
    })
}

/*
 **************************************
 Share list with email helper functions
 **************************************
 */

/**
 * Initialize the share list to email form. Generates a new row
 * for the shared table.
 */
function initShareEmailForm() {
    $('#share-list-form').submit(function (e) {
        e.preventDefault();
        const form = document.querySelector('#share-list-form');
        if (form.checkValidity()) {
            const $mail = $('#email');
            const mail = $mail.val();
            const row = createShareEmailRow(mail);
            addRowToTable('email', row);
            initShareEmailDeleteButton();
            cleanShareEmailForm($mail);
        }
    })
}

/**
 * Helper function for generating a html row code for
 * shared emails table
 * @param mail
 * @returns {string}
 */
function createShareEmailRow(mail) {
    return `<tr id="last">
    <td class="email" data-email="${mail}">${mail}</td>
    <td class="w-3-rem i-btn delete-mail">
    <i class="fas fa-trash-alt"></i>
    </td></tr>`;
}

/**
 * Helper function that clears the share list form
 * @param $mail
 */
function cleanShareEmailForm($mail) {
    $mail.val('');
    $mail.focus();
}

/**
 * Initialize the delete button for removing emails from
 * the share list table
 */
function initShareEmailDeleteButton() {
    $('.delete-mail').off('click').on('click', function (e) {
        const tableId = 'email';
        const colspan = 2;
        const emptyTableMessage = "No emails";
        const $parent = $(this).parent();
        deleteRowFromTable(tableId, $parent, colspan, emptyTableMessage);
    })
}

/**
 * Helper function that creates a list of email objects from the
 * share list table
 * @returns {[]}
 */
function collectShareEmailValues() {
    const $emailRows = $('.email');
    const emails = [];
    $.each($emailRows, function (_, row) {
        emails.push($(row).data('email'))
    });
    return emails
}

/*
 *******************************************
 * Submit ShoppingList form helper functions
 *******************************************
 */

/**
 * Function for submitting a shopping list to the right api endpoints
 * @param method - string value of the http method used for submitting.
 */
function initSubmitShoppingList(method) {
    $('#submit-shopping-list').off('click').on('click', function (e) {
        const items = collectShoppingListItemValues();
        const emails = collectShareEmailValues();
        const data = {
            name: $('#name').val().trim(),
            items: items,
            emails: emails
        };
        const url = $(this).data('url');
        jsonRequest(url, data, method).then(function (response) {
            window.location.replace(response.url);
        }).catch(function (response) {
            if ('responseJSON' in response) {
                response = response.responseJSON;
                console.log(response);
                if ('message' in response) {
                    createToastMessage(response.message, 'error',
                        5000, 'Submission Error');
                }
                if ('errors' in response) {
                    displayErrors(response.errors)
                }
            } else {
                createSubmissionErrorToast();
            }
        });
    })
}

/*
 **********************************************
 * Editing shopping lists form helper functions
 **********************************************
 */

/**
 * Function for editing item rows in a shopping list. Replace item
 * row with a prepopulated from for editing row. Initializes all
 * buttons in the item rows while viewing and editing.
 * @param rowMap - helper map for editing rows
 * @returns {jQuery}
 */
function initEditListEditItemRow(rowMap) {
    return $('.edit-item-row').off('click').on('click', function (e) {
        let activeRow = rowMap.get('activeRow');
        if (activeRow) {
            const $container = activeRow['container'];
            const row = activeRow['row'];
            $container.html(row.children());
        }
        const $container = $(this).closest('tr');
        const row = $container.clone();
        activeRow = {
            container: $container,
            row: row
        };
        rowMap.set('activeRow', activeRow);
        const editRow = createEditItemRowForm($container);
        $container.html(editRow);
        $container.find('#edit-code').focus();
        initEditListEditItemRow(rowMap);
        initCancelEditBtn(rowMap);
        initListDeleteBtn();
        initToggleItemDone();
    });
}

/**
 * Init cancel button for item editing. Replaces edit form with a td
 * tags.
 * @param rowMap - map containing the original row that was edited
 * and container where the row was
 */
function initCancelEditBtn(rowMap) {
    let activeRow = rowMap.get('activeRow');
    $('.cancel-btn').off('click').on('click', function (e) {
        const $container = activeRow['container'];
        const row = activeRow['row'];
        $container.html(row.children());
        activeRow = null;
        rowMap.set('activeRow', activeRow);
        initEditListEditItemRow(rowMap);
        initToggleItemDone();
    });
}

/**
 * Generate html code for item row edit form
 * @param $container - jquery selector of the container where to
 * insert the genrerated form
 * @returns {jQuery}
 */
function createEditItemRowForm($container) {
    let $form = $('#template-row').clone();
    const $itemName = $form.find('.item-name');
    let value = $container.find('.item-name').data('value');
    $itemName.removeAttr('id');
    $itemName.html(value);

    const $itemCode = $form.find('.item-code');
    value = $container.find('.item-code').data('value');
    $itemCode.removeAttr('id');
    let input = `<input id="edit-code" type="text" placeholder="Item Code" maxlength="20"
        class="form-control" value="${value}" form="edit-row-form">`;
    $itemCode.removeAttr('id');
    $itemCode.html(input);

    const $itemQuantity = $form.find('.item-quantity');
    value = $container.find('.item-quantity').data('value');
    try {
        value = parseFloat(value);
    } catch (e) {
        value = 0
    }
    input = `<input id="edit-quantity" type="number" step="0.01" min="0" placeholder="Quantity" max="99.99"
       class="form-control" value="${value}" form="edit-row-form">`;
    $itemQuantity.removeAttr('id');
    $itemQuantity.html(input);

    const $itemPrice = $form.find('.item-price');
    value = $container.find('.item-price').data('value');
    try {
        value = parseFloat(value);
    } catch (e) {
        value = 0
    }
    input = `<input id="edit-price" type="number" step="0.01" min="0" placeholder="Item price" max="9999999.99"
           class="form-control" value="${value}" form="edit-row-form">`;
    $itemPrice.removeAttr('id');
    $itemPrice.html(input);

    const $itemDone = $form.find('.item-done');
    value = $container.find('.item-done').data('value');
    let checked = value === 'True' ? 'checked' : '';

    input = `<div class="custom-control custom-switch">`;
    input += `<input class="custom-control-input" type="checkbox" id="edit-done" ${checked}>`;
    input += `<label class="custom-control-label" for="edit-done">Done?</label></div>`;

    $itemDone.removeAttr('id');
    $itemDone.html(input);

    $form.find('.item-action').removeAttr('id');
    $form.removeAttr('id');
    return $form.html();
}

/**
 * Initialize the button for toggling an item's is_done state.
 */
function initToggleItemDone() {
    $('.toggle-done').off('click').on('click', function (e) {
        let value = $(this).attr('data-value');
        value = value === 'True' ? 'False' : 'True';
        $(this).attr('data-value', value);
        $(this).html(getItemDoneElement(value));
    })
}

/**
 * Get the right image for the item's is_done status.
 * @param value - str value of the item's is_done attribute
 * @returns {string}
 */
function getItemDoneElement(value) {
    if (value === 'True') {
        return '<i class="fa-15x text-success fas fa-check-circle"></i>';
    }
    return '<i class="fa-15x text-danger far fa-times-circle"></i>';
}

/**
 * Initialize the item edit form submit functionality. Remove the from,
 * replace it with td tags containing the new data.
 * @param rowMap - map containing the active row and the
 * selector for the container
 */
function initSubmitEditRowForm(rowMap) {
    $('#edit-row-form').submit(function (e) {
        e.preventDefault();
        const form = document.querySelector('#edit-row-form');
        if (form.checkValidity()) {
            let activeRow = rowMap.get('activeRow');
            if (!activeRow) {
                return false;
            }
            const $container = activeRow['container'];
            const row = activeRow['row'];
            const code = $('#edit-code').val();
            const itemCode = row.find('.item-code');
            itemCode.attr('data-value', code);
            itemCode.html(code);

            const quantity = $('#edit-quantity').val();
            const quantityItem = row.find('.item-quantity');
            quantityItem.attr('data-value', quantity);
            quantityItem.html(quantity);

            const price = $('#edit-price').val();
            const priceItem = row.find('.item-price');
            priceItem.attr('data-value', price);
            priceItem.html(price);

            const done = $('#edit-done').prop('checked') ? 'True' : 'False';
            const doneItem = row.find('.item-done');
            doneItem.attr('data-value', done);
            doneItem.html(getItemDoneElement(done));

            $container.html(row.children());
            initEditListEditItemRow(rowMap);
            initCancelEditBtn(rowMap);
            activeRow = null;
            rowMap.set('activeRow', activeRow);

            initEditListEditItemRow(rowMap);
            initToggleItemDone();
            initDeleteItemRow();
            return false;
        }
    })
}
