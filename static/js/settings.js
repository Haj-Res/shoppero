/*****************************
 * Basic profile information *
 *****************************/

/**
 * Initialize submission of a new avatar image
 */
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

/**
 * Initialize basic profile information form submission. Create a PATCH
 * request to update user form. On successful update change data in the
 * corresponding page elements. Otherwise display errors.
 */
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

/**
 * Make DELETE request to delete the user's current avatar image
 */
function deleteAvatar() {
    const url = $('#avatarInput').data('url');
    const method = 'DELETE';
    jsonRequest(url, null, method).then(function (response) {
        $("#avatar").attr("src", response.avatar);
    }).catch(function (response) {
        createToastMessage('Submission Error. Try again later.', 'error');
    });
}

/**
 * Open the "choose file" modal through JS. Used because the file input
 * field is hidden and everything is done through one button.
 */
function chooseFile() {
    $('#avatarInput').trigger('click');
}

/**
 * Display form for updating basic profile information and hide button
 * that is used for triggering this function
 */
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

/**
 * Hide form for updating basic profile information and display button
 * that is used for displaying the form
 */
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

/**
 * Update the data in the basic information form input fields
 * @param data - object containing the user's first and last name
 */
function updateInformationForm(data) {
    $('#first_name').val(data.first_name);
    $('#last_name').val(data.last_name);
}

/*****************************
 * Profile security settings *
 *****************************/

/**
 * Initialize button used for showing the change password form.
 * Button displays form, focuses on the old password input and hides itself
 */
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

/**
 * Initialize button for canceling password change form.
 * Clear and hide form, show button for displaying form.
 */
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

/**
 * Initialize submitting password change form. Run HTML form validation,
 * check that new password and confirmation password match. Make POST request.
 * Hide form on success and display button or display errors on faild request
 */
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

/**
 * Clean change password form's inputs
 */
function cleanPasswordForm() {
    $('#old_password').val('');
    $('#new_password').val('');
    $('#new_password_errors').html();
    $('#confirm_password').val('');
    $('#confirm_password_errors').html();
    $('#old_password_errors').html();
}

/*****************************
 * Two Factor Authentication *
 *****************************/


/**
 * Display the from with cancel and continue action for toggling 2FA
 * and hide the button.
 */
function initShowTwoFactorConfBtn() {
    $('#two-factor-btn').on('click', function (e) {
        $(this).hide();
        $('.two-factor-confirmation').addClass('show')
    });
}

/**
 * Hide the from for toggling 2FA and display button
 */
function initCancelTwoFactorConfBtn() {
    $('#two-factor-cancel-btn').on('click', function (e) {
        $('.two-factor-confirmation').removeClass('show');
        $('#two-factor-btn').show();
    });
}

/**
 * Make a GET request to app to send the confirmation code to user's email.
 * Prepare toggle 2FA form and display it. Hide previous modal.
 */
function initGetTwoFactorCodeBtn() {
    $('#two-factor-get-code').on('click', function (e) {
        const url = $(this).data('url');
        jsonRequest(url).then(function (result) {
            $('#two-factor-form').attr('action', result.url);
            $('.two-factor-confirmation').removeClass('show');
            $('.two-factor-container').addClass('show');
        }).catch(function (response) {
            createSubmissionErrorToast()
        });
    });
}

/**
 * Cancel toggling 2FA and hide the from.
 */
function initCancelTwoFactorFromBtn() {
    $('#two-factor-cancel-form-btn').on('click', function (e) {
        $('.two-factor-container').removeClass('show');
        $('#two-factor-btn').show();
    });
}

/**
 * Submit the 2FA toggling. Make a POST request to server with with token.
 * Display errors if they are returned from the server or hide the from
 * and update elements to reflect the change. Display toast message.
 */
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

/**
 * Initialize the Share Level from submit action. Create a PATCH request
 * to the API with the share_level date. Display toast and errors if needed.
 */
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

/**
 * Initialize button from deleting user's account. Makes a GET request
 * that triggers the account delete sequence of actions.
 */
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