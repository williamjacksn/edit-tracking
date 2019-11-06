$('#modal-add-user').on('show.bs.modal', function (e) {
    let button = $(e.relatedTarget);
    $('#add-user-email').val(button.attr('data-email'));
    $('.form-check-input').prop('checked', false);
    let current_permissions = button.attr('data-permissions').split(' ');
    current_permissions.forEach(function (item) {
        $(`#permission-${item}`).prop('checked', true);
    });
}).on('shown.bs.modal', function () {
    $('#add-user-email').focus();
});
