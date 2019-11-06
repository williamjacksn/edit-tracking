$('#modal-edit-record').on('show.bs.modal', function (e) {
    let r = $(e.relatedTarget);
    $('#id').val(r.attr('data-id'));
    $('#month').val(r.attr('data-month'));
    $('#year').val(r.attr('data-year'));
    $('#clin').val(r.attr('data-clin'));
    $('#taskit-number').val(r.attr('data-taskit-number'));
    $('#researchers-edit-number').val(r.attr('data-researchers-edit-number'));
    $('#project').val(r.attr('data-project'));
    $('#received-on').val(r.attr('data-received-on'));
    $('#claimed-on').val(r.attr('data-claimed-on'));
    $('#editor').val(r.attr('data-editor'));
    $('#editing-transcription').val(r.attr('data-editing-transcription'));
    $('#edit-completed-on').val(r.attr('data-edit-completed-on'));
    $('#review-completed-on').val(r.attr('data-review-completed-on'));
    $('#total-pages').val(r.attr('data-total-pages'));
    $('#notes').val(r.attr('data-notes'));
});
