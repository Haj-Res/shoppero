/*****************************
 * Basic profile information *
 *****************************/
function initSubmitNewAvatarImage() {
    $('#avatarInput').change(function (e) {
        let fd = new FormData();
        let avatar = $('#avatarInput')[0].files[0];
        fd.append('avatar', avatar);
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
            const url = $(this).attr('action');
            const method = 'PATCH';
            jsonRequest(url, data, method).then(function (response) {
                $('#p-first-name').html(response.first_name);
                $('#p-last-name').html(response.last_name);
                createToastMessage('Information updated', 'success');
                updateInformationForm(response);
                hideInformationForm();
            }).catch(function (response) {
                createToastMessage('Submission error', 'error');
                displayErrors(response.responseJSON)
            });
        }
    })
}

function deleteAvatar() {
    const url = $('#avatarInput').data('url');
    const method = 'DELETE';
    jsonRequest(url, null, method).then(function (response) {
        $("#avatar").attr("src", response.avatar);
    }).catch(function (response) {
        createToastMessage('Submission Error. Try again later.', 'error');
    });
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

/*****************************
 * Profile security settings *
 *****************************/

function initPasswordChangeBtn() {
    $('#change-password-btn').on('click', function () {
        const $container = $('.change-password-container');
        if (!$container.hasClass('show')) {
            $container.addClass('show');
            $('#old_password').focus();
            $(this).hide();
        }
    });
}

function initCancelPasswordChangeBtn() {
    $('#cancel-password-change').on('click', function () {
        const $container = $('.change-password-container');
        if ($container.hasClass('show')) {
            cleanPasswordForm();
            $container.removeClass('show');
            $(this).html('Change Password');
            $('#change-password-btn').show();
        }
    });
}

function initSubmitPasswordChangeForm() {
    $('#change-password-form').submit(function (e) {
        e.preventDefault();
        const form = document.querySelector('#change-password-form');
        if (form.checkValidity()) {
            const $pass1_input = $('#new_password');
            const $pass2_input = $('#confirm_password');
            const pass1 = $pass1_input.val().trim();
            const pass2 = $pass2_input.val().trim();
            if (pass1 !== pass2) {
                $pass1_input.val('');
                $pass1_input.focus();
                $pass2_input.val();
                displayErrors({
                    'new_password': ['Passwords do not match'],
                    'confirm_password': ['Passwords do not match']
                })
            } else {
                const data = {
                    'old_password': $('#old_password').val().trim(),
                    'new_password': pass1
                };
                const url = $(this).attr('action');
                const method = 'POST';
                jsonRequest(url, data, method).then(function (response) {
                    cleanPasswordForm();
                    $('.change-password-container').removeClass('show');
                    $('#change-password-btn').show();
                    createToastMessage(response.message, 'success');
                }).catch(function (response) {
                    displayErrors(response.responseJSON)
                });
            }
        }
    })
}

/*****************************
 * Two Factor Authentication *
 *****************************/

function cleanPasswordForm() {
    $('#old_password').val('');
    $('#new_password').val('');
    $('#new_password_errors').html();
    $('#confirm_password').val('');
    $('#confirm_password_errors').html();
    $('#old_password_errors').html();
}

function initShowTwoFactorConfBtn() {
    $('#two-factor-btn').on('click', function (e) {
        $(this).hide();
        $('.two-factor-confirmation').addClass('show')
    });
}

function initCancelTwoFactorConfBtn() {
    $('#two-factor-cancel-btn').on('click', function (e) {
        $('.two-factor-confirmation').removeClass('show');
        $('#two-factor-btn').show();
    });
}

function initGetTwoFactorCodeBtn() {
    $('#two-factor-get-code').on('click', function (e) {
        const url = $(this).data('url');
        jsonRequest(url).then(function (result) {
            $('#two-factor-form').attr('action', result.url);
            $('.two-factor-confirmation').removeClass('show');
            $('.two-factor-container').addClass('show');
        }).catch(function (response) {
            createToastMessage('An error occurred. Please try again later.', 'error')
        });
    });
}

function initCancelTwoFactorFromBtn() {
    $('#two-factor-cancel-form-btn').on('click', function (e) {
        $('.two-factor-container').removeClass('show');
        $('#two-factor-btn').show();
    });
}

function initSubmitTwoFactorForm() {
    $('#two-factor-form').submit(function (e) {
        e.preventDefault();
        const form = document.querySelector('#two-factor-form');
        if (form.checkValidity()) {
            const data = {'token': $('#token').val()};
            const url = $(this).attr('action');
            const method = 'POST';
            jsonRequest(url, data, method).then(function (response) {
                createToastMessage(response.message, 'success');
                $('.two-factor-container').removeClass('show');
                $('#two-factor-btn').show();
                const $btn = $('#two-factor-get-code');
                $('#token').val('');
                if ($btn.html().trim() === 'Disable 2FA') {
                    $btn.html('Enable 2FA');
                } else {
                    $btn.html('Disable 2FA');
                }
            }).catch(function (response) {
                displayErrors(response.responseJSON);
            });

        }
    });
}

/*********************************
 * Default share level functions *
 *********************************/

function initSubmitShareLevelForm() {
    $('#share-level-form').submit(function (e) {
        e.preventDefault();
        const form = document.querySelector('#share-level-form');
        if (form.checkValidity()) {
            const url = $(this).attr('action');
            const data = {'share_level': $('#share_level').val()};
            const method = 'PATCH';
            jsonRequest(url, data, method).then(function (response) {
                createToastMessage('Share Level updated.', 'success')
            }).catch(function (response) {
                if ('responseJSON' in response) {
                    const data = response.responseJSON;
                    displayErrors(data);
                } else {
                    createToastMessage(
                        'Submission error. Please try later.',
                        'error'
                    );
                }
            })
        }
    })
}

function initDeleteAccountBtn() {
    $('#delete-account').on('click', function (e) {
        const url = $(this).data('url')
        jsonRequest(url).then(function (response) {
            createToastMessage(response.message, 'success');
        }).catch(function (response) {
            createSubmissionErrorToast();
        })
    })
}