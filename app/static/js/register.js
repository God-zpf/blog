$(function () {
    // 注册表单是否可以提交的标志，true可以提交，false不可提交
    var flag1, flag2;
    // ajax异步验证注册
    // 获取loginname的值
    $('[name=loginname]').blur(function () {
        loginname = $(this).val();
        console.log(loginname);
        if(loginname){
            $.ajax({
                url: '/check',
                type: 'get',
                data: 'loginname='+loginname,
                dataType: 'json',
                success: function(data){
                    console.log(data);
                    $('.infoText').html(data.msg);
                    if (data.code == 0){
                        flag1 = false;
                        console.log(flag1, '已经注册')
                    }
                    else{
                        flag1 = true;
                        console.log(flag1, '注册重名通过')
                    }
                }
            });
        }

    });

    //校验二次确认密码
    $('.left-form li:last>input').blur(function () {
        if ($(this).val()!==$('[name=password]').val()){
            $('.checkPassword').html('二次密码不一致');
            flag2 = false;
            console.log(flag2, '二次密码验证不通过')
        }
        else{
            flag2 = true;
            console.log(flag2, '二次密码通过')
        }
    });

    //校验是否可以提交注册表单
    $('.form').submit(function () {
        var flag = flag1 && flag2
        console.log(flag, '提交表单')
        return flag;
    })

});