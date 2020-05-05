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
    })

})