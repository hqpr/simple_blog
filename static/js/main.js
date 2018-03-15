(function($) {
    $('#loadMoreLink').on('click', function() {
        var link = $(this);
        var page = link.data('page');
        console.log(page);
        $.ajax({
            type: 'post',
            url: '/blog/load_more/',
            data: {
                'page': page
            },
            success: function(data) {
                console.log(data.posts_html);
                $('#posts').append(data.posts_html);
                if (data.has_next) {
                    link.data('page', page+1);
                } else {
                    link.hide();
                }
            },
            error: function(xhr, status, error) {
                // shit happens friends!
            }
        });
    });
}(jQuery));