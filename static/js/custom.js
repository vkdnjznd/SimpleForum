// register page open function
function openRegisterPage(step){
    var current_url = location.protocol + "//" + location.host;
    var register_url = current_url + "/register";
    if (step == "agree")
        location.href = register_url + "?step=" + step;
    else if (step == "create"){
        var ServicesAgree = $("input:checkbox[name=ServicesAgree]").is(":checked");
        var PolicyAgree = $("input:checkbox[name=PolicyAgree]").is(":checked");
       
        if (!ServicesAgree || !PolicyAgree){
            alert("In order to use our services,\nyou must agree to Terms of Service and Privacy Policy.");
            return;
        }
        var token_url = current_url + "/" + "getRegisterToken";
        var token;
        // get csrf_token and setup ajax before post request
        var csrf_token = $('input[name="ag_csrf_token"]').attr('value');
        $.ajaxSetup({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        });

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

// register Validation Functions
function checkSpace(str) { 
    if (str.search(/\s/) != -1) { 
        return true; 
    } 
    else { 
        return false; 
    } 
}

function idValidator(){
    const MIN_LENGTH = 4;
    const MAX_LENGTH = 16;

    var ele = document.getElementById("id");
    var id = document.getElementById("id").value;
    var message = "";

    if (id == null || id == "") return;

    if (checkSpace(id)){
        message = "ID can't have white spaces";
    }
    else if (id.length < MIN_LENGTH){
        message = "ID must be at least " + MIN_LENGTH + " characters";
    }
    else if (MAX_LENGTH < id.length){
        message = "ID must be at most " + MAX_LENGTH + " characters";
    }
    else {
        for( var i=0; i < id.length;i++){         
            var c = id.charCodeAt(i);
            // Check each character is included in the range of numbers and alphabet
            if( !( (0x61 <= c && c <= 0x7A) || (0x41 <= c && c <= 0x5A) || (0x30 <= c && c <= 0x39 )) ) {   
                message = "Only English and Numbers are allowed for ID";
                break;
            }
        }
    }
    if (message.length == 0) {
        var current_url = location.protocol + "//" + location.host;
        var checkid_url = current_url + "/" + "checkDuplicated_ID";
        var csrf_token = $('input[name="csrf_token"]').attr('value');
        $.ajaxSetup({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        });

        $.ajax({
            type: "POST",
            url: checkid_url,
            async: false,
            data: {'id' : id},
            dataType: "JSON",
            success: function(res){
                console.log(res)
                if (res['result'] != "True")
                    message = "Duplicated ID";
            },
            error: function(request, status, error){
                console.log(request.status);
            }
        });
    }
    
    if (! message.length == 0){
        ele.style.color = "red";
        ele.style.backgroundImage = "url(static/image/x2.png)";
    }
    else{
        message = "Available ID";
        ele.style.color = "green";
        ele.style.backgroundImage = "url(static/image/o.png)";
    }

    ele.style.backgroundRepeat = "no-repeat";
    ele.style.backgroundSize = "24px 24px";
    ele.style.backgroundPosition = "center right";

    $('#id').attr('title', message);
    return;
};

function nickValidator(){
    const MIN_LENGTH = 2;
    const MAX_LENGTH = 16;

    var ele = document.getElementById("nickname");
    var nick = document.getElementById("nickname").value;
    var message = "";

    if (nick == null || nick == "") return;

    if (checkSpace(nick)){
        message = "Nickname can't have white spaces";
    }
    else if (nick.length < MIN_LENGTH){
        message = "Nickname must be at least " + MIN_LENGTH + " characters";
        
    }
    else if (MAX_LENGTH < nick.length){
        message = "Nickname must be at most " + MAX_LENGTH + " characters";
        
    } 
    
    if (! message.length == 0){
        ele.style.color = "red";
        ele.style.backgroundImage = "url(static/image/x2.png)";
    }
    else{
        message = "Available Nickname";
        ele.style.color = "green";
        ele.style.backgroundImage = "url(static/image/o.png)";
    }

    ele.style.backgroundRepeat = "no-repeat";
    ele.style.backgroundSize = "24px 24px";
    ele.style.backgroundPosition = "center right";

    $('#nickname').attr('title', message);
    
    return;
};

function pValidator(){
    const MIN_LENGTH = 8;
    const MAX_LENGTH = 32;

    var ele = document.getElementById("password");
    var pw = document.getElementById("password").value;
    var message = "";

    if (pw == null || pw == "") return;

    var num = pw.search(/[0-9]/g);
    var eng = pw.search(/[a-zA-Z]/ig);
    var spe = pw.search(/[`~!@@#$%^&*|₩₩₩'₩";:₩/?]/gi);
    var kor = pw.search(/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/);

    if (checkSpace(pw)){
        message = "Password can't have white spaces";
    }
    else if (kor != -1){
        message = "Password must be alphabet or digit or special symbol";
    }
    else if (pw.length < MIN_LENGTH){
        message = "Password must be at least " + MIN_LENGTH + " characters";
    }
    else if (MAX_LENGTH < pw.length){
        message = "Password must be at most " + MAX_LENGTH + " characters";
    }
    else if (num < 0 || eng < 0 || spe < 0){
        message = "Password must contain numbers, alphabets, and special symbols";
    }

    if (! message.length == 0){
        ele.style.color = "red";
        ele.style.backgroundImage = "url(static/image/x2.png)";
    }
    else{
        message = "Available Password";
        ele.style.color = "green";
        ele.style.backgroundImage = "url(static/image/o.png)";
    }

    ele.style.backgroundRepeat = "no-repeat";
    ele.style.backgroundSize = "24px 24px";
    ele.style.backgroundPosition = "center right";

    $('#password').attr('title', message);
    return;
};

function pcValidator(){
    var pw = document.getElementById("password").value;
    var pwc = document.getElementById("password_c").value;
    var message = "";
    var ele = document.getElementById("password_c");

    if (pw == null || pwc == null || pwc == "") return;

    if (pw.length == 0){
        message = "Please enter your password first";
        document.getElementById("password_c").value = "";
        document.getElementById("password").focus();
    }
    else if (!(pw === pwc)){
        message = "Confirm password must be the same as the password";
    }

    if (! message.length == 0){
        ele.style.color = "red";
        ele.style.backgroundImage = "url(static/image/x2.png)";
    }
    else{
        message = "Password Confirmed";
        ele.style.color = "green";
        ele.style.backgroundImage = "url(static/image/o.png)";
    }

    ele.style.backgroundRepeat = "no-repeat";
    ele.style.backgroundSize = "24px 24px";
    ele.style.backgroundPosition = "center right";

    $('#password_c').attr('title', message);
    return;
};

function allDataValidate(){
    var inputs = document.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++){
        var input = inputs.item(i);
        var color = input.style.color;
        if (!(color === "green") || color == undefined || input.length == 0){
            alert('Check this input');
            input.focus();
            return false;
        }
    }

    return true;
}

function setTooltipHTML(type, min, max){
    if (type == 'id'){
        var html;

        html = '<p>ID Rules</p><p>';
        html += '<li>Only English and Numbers are allowed for ID</li>';
        html += '<li>ID cannot have white spaces</li>';
        html += '<li>ID must be at least ' + min + ' characters</li>';
        html += '<li>ID must be at most ' + max + ' characters</li>';        
        html += '</p>';

        $('#id-tips').attr('data-bs-original-title', html);
    }
    else if (type == 'nickname'){
        var html;

        html = '<p>Nickname Rules</p><p>';
        html += '<li>Nickname cannot have white spaces</li>';
        html += '<li>Nickname must be at least ' + min + ' characters</li>';
        html += '<li>Nickname must be at most ' + max + ' characters</li>';        
        html += '</p>';

        $('#nick-tips').attr('data-bs-original-title', html);
    }
    else if (type == 'password'){
        var html;

        html = '<p>Password Rules</p><p>';
        html += '<li>Password cannot have white spaces</li>';
        html += '<li>Password must be consist of alphabet and digit and special symbol</li>';
        html += '<li>Password must be at least ' + min + ' characters</li>';
        html += '<li>Password must be at most ' + max + ' characters</li>';        
        html += '</p>';

        $('#pass-tips').attr('data-bs-original-title', html);
    }
    else{
        return;
    }
}