function cleanItemForm() {
    const $name = $('#name');
    $name.val('');
    $('#code').val('');
    $('#price').val('');
    $('#tags').val('');
    $name.focus();
}

function prepareItemForTable(item, rowNum) {
    rowNum = parseInt(rowNum) + 1;
    let tableRow = `<tr id="last" class="table-row item-${item.id}">`;
    tableRow += createItemTableData(item, rowNum);
    tableRow += '</tr>';
    return tableRow;
}

function createItemTableData(item, rowNum) {
    let tableRow = `<th class="num" scope="row">${rowNum}</th>`;
    tableRow += `<td>${item['name']}</td>`;
    tableRow += `<td>${item['code']}</td>`;
    tableRow += `<td class="justify-text-right">${item['price']}</td>`;
    tableRow += `<td>${item['tags']}</td>`;
    tableRow += `<td>
<span data-url="${item['url']}" class="i-btn edit-item-btn"><i class="fas fa-pen"></i>
<span data-url="${item['url']}" class="ml-3 i-btn delete-item-btn"><i class="fas fa-trash-alt"></i></span>
</span></td>`;
    return tableRow;
}

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

function updateItemRow(item) {
    const $itemRow = $(`.item-${item.id}`);
    const rowNum = $(`.item-${item.id} .num`).html();
    const itemData = createItemTableData(item, rowNum);
    $itemRow.html(itemData);
}

function initItemEditBtn() {
    $('.edit-item-btn').off('click').on('click', function (e) {
            let url = $(this).data('url');
            itemModalToEdit(url);
            $.getJSON(url, function (item, textStatus, jqXHR) {
                $('#name').val(item.name);
                $('#code').val(item.code);
                $('#price').val(item.price);
                $('#tags').val(item.tags);
                $('#itemModal').modal('show');
            });
        }
    )
}

function initItemDeleteBtn() {
    $('.delete-item-btn').off('click').on('click', function (e) {
        const url = $(this).data('url');
        const $parent = $(this).parent().parent();
        // TODO add confirmation modal
        $.ajax({
            headers: getHeaders(),
            url: url,
            type: 'PATCH',
            success: function (response, textStatus, jqHxr) {
                let is_empty = false;

                if ($parent.attr('id') === 'last') {
                    if ($parent.prev().length < 1) {
                        is_empty = true;
                    } else {
                        $parent.prev().attr('id', 'last')
                    }
                }
                $parent.remove();
                if (is_empty) {
                    const empty_row = '<tr id="table-empty">\n' +
                        '                    <td class="table-data" colspan="6">No items found</td>\n' +
                        '                </tr>';
                    $('tbody').html(empty_row);
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                // TODO handle error
            }
        })
    });
}

function itemModalToAddNew() {
    let $form = $('#item-form');
    let url = $form.data('new');
    $form.attr('action', url);
    $form.attr('method', 'post');
    $('.modal-title').html('New Item');
}

function itemModalToEdit(url) {
    let $form = $('#item-form');
    $form.attr('action', url);
    $form.attr('method', 'put');
    $('.modal-title').html('Update item');
}

function validateItemForm() {
    let errors = {};

    const name = $('#name').val()?.trim();
    let name_err = [];
    if (name === undefined || name === null || name === '') {
        name_err.push('required')
    } else if (name.length < 2) {
        name_err.push('must be at least 2 characters');
    }

    if (name_err.length > 0) {
        errors['name'] = name_err;
        return errors;
    }
    return null;
}

function postOrPutItemData() {
    $('#item-form').submit(function (e) {
        e.preventDefault();
        const form = document.querySelector('#item-form');
        if (form.checkValidity()) {
            const $form = $('#item-form');
            const data = {
                name: $('#name').val(),
                code: $('#code').val(),
                price: $('#price').val() ? $('#price').val() : null,
                tags_string: $('#tags').val()
            };
            $.ajax({
                    headers: getHeaders(),
                    url: $form.attr('action'),
                    type: $form.attr('method').toUpperCase(),
                    contentType: 'application/json; charset=utf-8',
                    dataType: 'json',
                    data: JSON.stringify(data),
                    success: function (response, textStatus, jqHxr) {
                        if ($form.attr('method').toUpperCase() === 'POST') {
                            addItemRow(response);
                        } else if ($form.attr('method').toUpperCase() === 'PUT') {
                            updateItemRow(response);
                            $('#itemModal').modal('hide');
                        }
                        initItemEditBtn();
                        initItemDeleteBtn();
                        cleanItemForm();
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        const errors = jqXHR.responseJSON;
                        displayErrors(errors);
                    }
                }
            );
        }
    });
}
