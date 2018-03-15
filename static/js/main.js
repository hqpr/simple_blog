(function($) {
    $('#loadMoreLink').on('click', function() {
        var link = $(this);
        var page = link.data('page');
        $.ajax({
            type: 'post',
            url: '/blog/load_more/',
            data: {
                'page': page,
                'url': link.data('url')
            },
            success: function(data) {
                $('#posts').append(data.posts_html);
                if (data.has_next) {
                    link.data('page', page+1);
                } else {
                    link.hide();
                    $('.pagination').hide();
                }
            },
            error: function(xhr, status, error) {
                // pass
            }
        });
    });
}(jQuery));