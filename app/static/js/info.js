$(function() {
    //获取浏览器上的参数
    var args = window.location.search.split('?')[1];
    console.log(args);
    $.ajax({
        url: '/topic',
        type: 'get',
        data: args,
        dataType: 'json',
        success: function (data) {
            console.log(data);
            $('.news_con').html(data.content)
            }
    });
    $('.voke').click(function () {
        console.log('点赞')
        $.ajax({
            url: '/voke',
            type: 'post',
            data: args,
            dataType: 'json',
            success: function (data) {
                console.log(data);
                $('#diggnum').text(data.num);
                $('.like').text(data.num);
            }
        })
    })

})