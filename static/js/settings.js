/*****************************
 * Basic profile information *
 *****************************/
function initSubmitNewAvatarImage() {
    $('#avatarInput').change(function (e) {
        let fd = new FormData();
        let avatar = $('#avatarInput')[0].files[0];
        fd.append('avatar', avatar);
        console.log($(this).data('url'));
        $.ajax({
            headers: getHeaders(),
            url: $(this).data('url'),
            type: 'post',
            data: fd,
            contentType: false,
            processData: false,
            success: function (response) {
                if ('avatar' in response) {
                    $("#avatar").attr("src", response.avatar);
                } else {
                    alert('file not uploaded');
                }
            },
        });
    });
}

function initSubmitProfileInformationForm() {
    $('#information-form').submit(function (e) {
        e.preventDefault();
        const data = {
            'first_name': $('#first_name').val(),
            'last_name': $('#last_name').val()
        };
        const form = document.querySelector('#information-form');
        if (form.checkValidity()) {
            $.ajax({
                headers: getHeaders(),
                url: $(this).attr('action'),
                method: 'patch',
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                data: JSON.stringify(data),
                success: function (response) {
                    $('#p-first-name').html(response.first_name);
                    $('#p-last-name').html(response.last_name);
                    createToastMessage('Information updated', 'success');
                    updateInformationForm(response);
                    hideInformationForm();
                },
                error: function (response) {
                    console.log(response);
                    createToastMessage('Submission error', 'error');
                }
            })
        }
    })
}

function deleteAvatar() {
    const url = $('#avatarInput').data('url');
    $.ajax({
        headers: getHeaders(),
        url: url,
        type: 'delete',
        success: function (response) {
            if ('avatar' in response) {
                $("#avatar").attr("src", response.avatar);
            } else {
                alert('file not uploaded');
            }
        }
    })
}

function chooseFile() {
    $('#avatarInput').trigger('click');
}

function showInformationForm() {
    $('#information-container').addClass('d-none');
    $('#information-form-container').removeClass('d-none');
    const $showBtn = $('#information-button');
    $showBtn.removeClass('d-inline');
    $showBtn.addClass('d-none');
    const $formBtns = $('#information-form-button');
    $formBtns.removeClass('d-none');
    $formBtns.addClass('d-inline');
    $('#first_name').focus();
}

function hideInformationForm() {
    $('#information-container').removeClass('d-none');
    $('#information-form-container').addClass('d-none');
    const $showBtn = $('#information-button');
    $showBtn.addClass('d-inline');
    $showBtn.removeClass('d-none');
    const $formBtns = $('#information-form-button');
    $formBtns.addClass('d-none');
    $formBtns.removeClass('d-inline');
}

function updateInformationForm(data) {
    $('#first_name').val(data.first_name);
    $('#last_name').val(data.last_name);
}
