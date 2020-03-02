function initClickableTableRow() {
    $(".table-row").click(function () {
        window.document.location = $(this).data("href");
    });
}

function displayErrors(errors) {
    for (let key in errors) {
        if (errors.hasOwnProperty(key)) {
            let err_content = '<ul>';
            errors[key].forEach(err => {
                err_content += '<li><small>' + err + '</small></li>';
            });
            err_content += '</ul>';
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

