function openRegisterPage(step){
    var current_url = location.protocol + "//" + location.host;
    var register_url = current_url + "/register";
    if (step == "agree")
        location.href = register_url + "?step=" + step;
    else if (step == "create"){
        var ServicesAgree = $("input:checkbox[name=ServicesAgree]").is(":checked");
        var PolicyAgree = $("input:checkbox[name=PolicyAgree]").is(":checked");
       
        if (!ServicesAgree || !PolicyAgree){
            alert("In order to use our services,you must agree to Terms of Service and Privacy Policy.");
            return;
        }
        var token_url = current_url + "/" + "getRegisterToken";
        var token;
        $.ajax({
            type: "POST",
            url: token_url,
            async: false,
            dataType: "JSON",
            success: function(data){
                token = data['token'];
            },
            error: function(request, status, error){
                console.log(request.status);
            }
        });

        location.href = register_url + "?step=" + step + "&ServicesAgree=" + ServicesAgree + "&PolicyAgree=" + PolicyAgree + "&RegisterToken=" + token;
    }
};

