String.prototype.hashCode = function () {
    let hash = 0;
    if (this.length === 0) return hash;
    for (let i = 0; i < this.length; i++) {
        let char = this.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return hash;
};


function initClickableTableRow() {
    $(".table-row").click(function () {
        window.document.location = $(this).data("href");
    });
}

function displayErrors(errors) {
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

function showMessage(type, message) {
    let messageType = 'alert-primary';
    switch (type) {
        case 'success':
            messageType = 'alert-success';
            break;
        case 'error':
            messageType = 'alert-danger';
    }
    let messageElement = `<div class="alert ${messageType} alert-dismissible fade show px-5 py-2 " role="alert">${message}</div>`;
    $('#message').html(messageElement);
    setTimeout(() => {
        $('.alert').alert('close');
    }, 3000);
}

function initModal(modalId, showCallback, hideCallback) {
    $(modalId).on('shown.bs.modal', function () {
        showCallback();
    });

    $(modalId).on('hide.bs.modal', function () {
        hideCallback();
    });
}

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

function createEmptyRow(colspan, emptyTableMessage) {
    if (emptyTableMessage === undefined) {
        emptyTableMessage = 'No data'
    }
    let emptyRow = '<tr id="table-empty">';
    emptyRow += `<td class="table-data" colspan="${colspan}">${emptyTableMessage}</td>`;
    emptyRow += `</tr>`;
    return emptyRow;
}

function validateEmail(mail) {
    if (!(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/).test(mail)) {
        return "Not a valid email format"
    } else if (mail.length >= 254) {
        return "Can not be longer than 254 character"
    }
    return false
}


function getHeaders() {
    return {'X-CSRFToken': getCookie('csrftoken')}
}

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