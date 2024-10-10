// Wait for the DOM to be ready
$(function() {
    console.log( "Custom JS Loaded!" );
    function openCommentModal(contentType, objectId, objectTitle) {
        $('#commentModalLabel').text(`Add Comment to ${objectTitle}`);
        $('#commentForm').attr('action', `/add_comment/${contentType}/${objectId}/`);
        $('#commentModal').modal('show');
    }
});