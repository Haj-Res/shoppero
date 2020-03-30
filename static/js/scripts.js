/**
 * Helper function for displaying errors on submission failure
 * @param errors - object in the from of {field_name: [err1, err2]}
 */
function displayErrors(errors) {
    $('.error').html('');
    for (let key in errors) {
        if (errors.hasOwnProperty(key)) {
            let err_content = '<small><ul>';
            errors[key].forEach(err => {
                err_content += '<li>' + err + '</li>';
            });
            err_content += '</ul></small>';
            $('#' + key + '_errors').html(err_content);
        }
    }
}

/**
 * Helper function for getting the set cookie.
 * @param name
 * @returns {null}
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break
            }
        }
    }
    return cookieValue;
}

/**
 * Initialize modal with special show and hide callback methods
 */
function initModal(modalId, showCallback, hideCallback) {
    $(modalId).on('shown.bs.modal', function () {
        showCallback();
    });

    $(modalId).on('hide.bs.modal', function () {
        hideCallback();
    });
}

/**
 * Helper function for adding a row to a table. Takes care of
 * the #last id of rows while adding
 * @param tableId - id of the table
 * @param row - html code of the row to be inserted
 */
function addRowToTable(tableId, row) {
    const $emptyRow = $(`#${tableId} #table-empty`);
    if ($emptyRow.length) {
        $emptyRow.remove();
        $(`#${tableId} tbody`).html(row);
    } else {
        const $last = $(`#${tableId} tbody #last`);
        $(row).insertAfter($last);
        $last.removeAttr('id');
    }
}

/**
 * Delete row from table. Take care of the #last id of the row.
 * Display special row if table is empty after delete
 * @param tableId - id of the table
 * @param $row - jquery selector of the row to be deleted
 * @param colspan - how wide the table is. Used for creating
 * the empty table row
 * @param emptyTableMessage - message displayed in the empty table row
 */
function deleteRowFromTable(tableId, $row, colspan, emptyTableMessage) {
    if ($row.attr('id') === 'last') {
        if ($row.prev().length < 1) {
            const emptyRow = createEmptyRow(colspan, emptyTableMessage);
            $(`#${tableId} tbody`).html(emptyRow);
        } else {
            $row.prev().attr('id', 'last');
        }
    }
    $row.remove();
}

/**
 * Helper function fro creating empty table rows
 * @param colspan - width of the table
 * @param emptyTableMessage - message in the row
 * @returns {string}
 */
function createEmptyRow(colspan, emptyTableMessage) {
    if (emptyTableMessage === undefined) {
        emptyTableMessage = 'No data'
    }
    let emptyRow = '<tr id="table-empty">';
    emptyRow += `<td class="table-data" colspan="${colspan}">${emptyTableMessage}</td>`;
    emptyRow += `</tr>`;
    return emptyRow;
}

/**
 * Get headers with the CSRF token
 * @returns {{"X-CSRFToken": *}}
 */
function getHeaders() {
    return {'X-CSRFToken': getCookie('csrftoken')}
}


/**
 * Create and show a toast message to the user
 * @param message - Message shown
 * @param level - message level (info, success, warn, error)
 * @param duration - how long the message is shown in MS, def: 2000
 * @param title - toast title
 */
function createToastMessage(message, level, duration, title) {
    level = level ? level : 'info';
    duration = duration ? duration : 2000;
    title = title ? title : 'Notification';
    const timestamp = new Date().getTime();
    const toast_element = `<div id="${timestamp}" class="toast border-${level} min-w-300" role="alert" aria-live="assertive" aria-atomic="true" data-delay="${duration}">
            <div class="toast-header">
                <strong class="mr-auto">${title}</strong>
                <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="toast-body">${message}</div>
        </div>`;
    $('.message-element').append(toast_element);
    $(`#${timestamp}`).toast('show');
}

/**
 * Initialize Bootstrap tooltip messages
 */
function initTooltips() {
    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });
}

/**
 * Wrapper function for the jQuery ajax function request with
 * predefined headers for CSRF tokenand content and data type json.
 * Use jsonReuquest(foo, bar, baz).then(function(response){}).catch(function(response){})
 * to deal with the server's response
 * @param url - endpoint for the reuqest
 * @param data - data sent to endpoint
 * @param method - http method to be used
 * @returns {jQuery|{getAllResponseHeaders: (function(): *), abort: (function(*=): jqXHR), setRequestHeader: (function(*=, *): jqXHR), readyState: number, getResponseHeader: (function(*): *), overrideMimeType: (function(*): jqXHR), statusCode: (function(*=): jqXHR)}|string|(function(*=, *=): *)|(function(*=, *=): *)|HTMLElement|*}
 */
function jsonRequest(url, data, method) {
    if (method === undefined) {
        method = 'GET'
    }
    return $.ajax({
        headers: getHeaders(),
        url: url,
        type: method,
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: data ? JSON.stringify(data) : data,
        success: function (response) {
            return {'success': true, 'response': response}
        },
        error: function (response) {
            return {'success': false, 'response': response}
        }
    })
}

/**
 * Wrapper function of the createToastMessage with default submission
 * error toast message
 */
function createSubmissionErrorToast() {
    const title = 'Submission Error';
    const message = `An error occurred. Please try again later. If this keeps
    persisting, please contact support.`;
    const level = 'error';
    const duration = 3000;
    createToastMessage(message, level, duration, title);
}