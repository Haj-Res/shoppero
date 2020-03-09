function initItemAutocompleteSearch() {
    const $elem = $('#item-name');
    $elem.on('input', function (e) {
        const val = $elem.val();
        if (val.length >= 3) {
            let url = $elem.data('url') + `?name=${val}`;
            $.getJSON(url, function (result, textStatus, jqXHR) {
                const dataList = itemListToDataList(result);
                $('#item-datalist').html(dataList);
            })
        }
    })
}

function itemListToDataList(items) {
    let dataList = '';
    items.forEach(item => {
        dataList += `<option data-code="${item.code}" data-price="${item.price}">${item.name}</option>`;
    });
    return dataList;
}

function itemInputOnChange() {
    const $elem = $('#item-name');
    $elem.change(function () {
        const options = $('#item-datalist option');
        options.each(function (index) {
            const text = ($(this).text());
            if (text.toLowerCase() === $elem.val().toLowerCase()) {
                $('#price').val($(this).data('price'));
                $('#code').val($(this).data('code'));
            }
        })
    })
}

function createShoppingListItemRow(item, id) {
    let tableRow = `<tr id="last" data-id="${id}">`;
    tableRow += `<td>${item.name}</td>`;
    tableRow += `<td>${item.code ? item.code : '-'}</td>`;
    tableRow += `<td>${item.quantity}</td>`;
    tableRow += `<td>${item.price ? item.price : '-'}</td>`;
    tableRow += `<td>${item.is_done ? 'Completed' : '-'}</td>`;
    tableRow += `<td><span class="link delete-item ml-3"><i class="fas fa-trash-alt"></i></span></td>`;
    tableRow += '</tr>';
    return tableRow;
}

function validateShoppingListItem(item) {
    const errors = {};
    if (!item.name || item.name === '') {
        errors['item-name'] = ['Field is required']
    } else if (item.name.length > 200) {
        errors['item-name'] = [`Ensure that field is not longer than 200 (currently ${item.name.length})`]
    }
    if (item.code.length > 20) {
        errors['code'] = [`Ensure that field is not longer than 20 (currently ${item.code.length})`]
    }
    if (item.quantity >= 100) {
        errors['quantity'] = [`Must be less than 100`]
    } else if (item.quantity < 0) {
        errors['quantity'] = [`Must be greater or equal than 0`]
    }
    if (item.price >= 10000000) {
        errors['price'] = [`Must be less than 10,000,000`]
    } else if (item.price < 0) {
        errors['price'] = [`Must be greater or equal than 0`]
    }
    return errors
}

function initAddItemToMapButton(itemMap) {
    $('#add-item').off('click').on('click', function (e) {
        e.preventDefault();
        const ITEM_IN_LIST_LIMIT = 30;
        if (itemMap.size < ITEM_IN_LIST_LIMIT) {
            const $code = $('#code');
            const $quantity = $('#quantity');
            const $price = $('#price');

            const item = {
                name: $('#item-name').val().trim(),
                code: $code.val(),
                quantity: $quantity.val() ? parseFloat($quantity.val()) : 1,
                price: $price.val(),
                is_done: $('#is-done').prop('checked')
            };
            const errors = validateShoppingListItem(item);
            if ($.isEmptyObject(errors)) {
                const itemString = `${item.name}${item.quantity}${item.price}${item.is_done}`;
                const hash = itemString.hashCode();
                if (!itemMap.has(hash)) {
                    const row = createShoppingListItemRow(item, hash);
                    addRowToTable('items', row);
                    initDeleteItemRow(itemMap);
                    clearShoppingListItemForm();
                    itemMap.set(hash, item);
                }
            } else {
                displayErrors(errors)
            }
        } else {
            createToastMessage(`List can't have more than ${ITEM_IN_LIST_LIMIT} items`,
                'warning');
        }
    })
}

function initDeleteItemRow(itemMap) {
    $('#last .delete-item').off('click').on('click', function (e) {
        const $parent = $(this).parent().parent();
        const id = $parent.data('id');
        const tableId = 'items';
        const colspan = 6;
        const emptyTableMessage = 'No items';
        itemMap.delete(id);
        deleteRowFromTable(tableId, $parent, colspan, emptyTableMessage);
    })
}

function clearShoppingListItemForm() {
    $('#item-name').val('');
    $('#code').val('');
    $('#quantity').val('');
    $('#price').val('');
    $('#is-done').prop('checked', false);
    $('#item-name').focus()
}

function initShareEmailForm(sharedUser) {
    $('#share-list-form').submit(function (e) {
        e.preventDefault();
        const $mail = $('#email');
        const mail = $mail.val();
        const emailHasErrors = validateEmail(mail);
        if (!emailHasErrors) {
            if (!sharedUser.has(mail.toLowerCase())) {
                sharedUser.add(mail.toLowerCase());
                const row = createEmailRow(mail);
                addRowToTable('email', row);
                initSharedMailDeleteButton(sharedUser);
                cleanShareMailForm($mail);
                $('#email_errors').html('');
            } else {
                // TODO notify email is already in list
            }
        } else {
            displayErrors({'email': [emailHasErrors]})
        }
    })
}

function createEmailRow(mail) {
    let mailRow = `<tr id="last">`;
    mailRow += `<td class="py-1">${mail}</td>`;
    mailRow += `<td class="py-1 w-3-rem"><span class="link delete-mail ml-3" data-mail="${mail}"><i class="fas fa-trash-alt"></i></span></td>`;
    mailRow += `</tr>`;
    return mailRow;
}

function cleanShareMailForm($mail) {
    $mail.val('');
    $mail.focus();
}

function initSharedMailDeleteButton(sharedUser) {
    $('#last .delete-mail').off('click').on('click', function (e) {
        const mail = $(this).data('mail');
        const tableId = 'email';
        const colspan = 2;
        const emptyTableMessage = "No emails";
        const $parent = $(this).parent().parent();
        sharedUser.delete(mail);
        deleteRowFromTable(tableId, $parent, colspan, emptyTableMessage);
    })
}

function initSubmitShoppingList(itemMap, emailSet) {
    $('#submit-shopping-list').off('click').on('click', function (e) {
        let emails = Array.from(emailSet);
        if (!emails.length) {
            emails = [''];
        }
        let items = [];
        for (const key of itemMap.keys()) {
            const i = itemMap.get(key);
            const obj = {
                item: i.name,
                code: i.code,
                quantity: i.quantity,
                price: i.price,
                is_done: i.is_done,
            };
            items.push(obj)
        }
        const data = {
            shopping_list: {name: $('#name').val().trim()},
            items: items,
            emails: emails
        };
        const url = $(this).data('url');

        $.ajax({
            headers: getHeaders(),
            url: url,
            type: 'POST',
            data: data,
            success: function (response, textStatus, jqHXR) {
                if (response.status === 'success') {
                    window.location.replace(response.url);
                } else {
                    if ('message' in response) {
                        createToastMessage(response.message, response.status,
                            2000, 'Submission Error');
                    } else if ('errors' in response) {
                        displayErrors(response.errors)
                    }
                }
            },
            error: function (jqHXR, testStatus, errorThrown) {
            }
        });
    })
}

function initListArchiveBtn() {
    $('.archive-list').on('click', function (e) {
        const url = $(this).data('url');
        deleteOrArchiveList(url, 'PUT', 'List archived');
    })
}

function initListDeleteBtn() {
    $('.delete-list').off('click').on('click', function (e) {
        $('.btn-ok').data('url', $(this).data('url'));
        $('#confirm-delete').modal('show');
    })
}

function initListDeleteConfirmBtn() {
    $('.btn-ok').on('click', function (e) {
        const url = $(this).data('url');
        deleteOrArchiveList(url, 'DELETE', 'List deleted');
    })
}

function deleteOrArchiveList(url, method, toastMessage) {
    $.ajax({
        headers: getHeaders(),
        url: url,
        type: method,
        success: function (response, textStatus, jqHXR) {
            if (response.status === 'success') {
                const table = generateShoppingListTable(response.content);
                $('#shopping-list-table tbody').html(table);
                initListArchiveBtn();
                initListDeleteBtn();
                $('.modal').modal('hide');
                createToastMessage(toastMessage, 'info');
            }
        }
    })
}

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
        table = `<tr id="table-empty"><td class="table-data" colspan="4">
            Click <a href="/shopping-list/lists/">here</a> to add a new 
            list and start using the site.
            </td></tr>`
    }

    return table;
}