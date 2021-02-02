import { loginValidate } from './register.js';

function openRegisterAgreePage(){
    var current_url = location.protocol + "//" + location.host;
    var register_url = current_url + "/register";
    var step = "agree";

    location.href = register_url + "?step=" + step;
}

function login(id, password){
    var current_url = location.protocol + "//" + location.host;
    var login_url = current_url + '/' + "login";

    var csrf_token = $('input[name="csrf_token"]').attr('value');
    $.ajaxSetup({
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    });

    $.ajax({
        type: "POST",
        url: login_url,
        async: false,
        data: {'id' : id, 'password' : password},
        dataType: "JSON",
        success: function(res){
            if (res['result'] == "OK"){
                location.href = current_url;
            }
            else{
                alert(res['result']);
            }
        },
        error: function(request, status, error){
            console.log(request.status);
        }
    });

    return;
}

// check user's login inputs before sent to the backend
function loginValidator(){
    var id = document.getElementById("id").value;
    var pw = document.getElementById("password").value;
    var result = loginValidate();

    if (result[0] != 0){
        alert("Check your ID");
        $('#id').focus();
        return;
    }
    else if (result[1] != 0){
        alert("Check your Password");
        $('#password').focus();
        return;
    }
    
    login(id, pw)
}

// event Listeners
if($('#homeContent').length){
    var registerPageEle = document.querySelectorAll('#registerPage');
    for (var i = 0; i < registerPageEle.length; i++)
        registerPageEle[i].addEventListener('click', openRegisterAgreePage);
}

if($('#loginModal').length){
    document.querySelector('#loginBtn').addEventListener('click', loginValidator);
}

if($('#logoutBtn').length){
    document.querySelector('#logoutBtn').addEventListener('click', function(){
        var current_url = location.protocol + "//" + location.host;
        var logout_url = current_url + '/' + "logout";
        location.href = logout_url;
    })
}
