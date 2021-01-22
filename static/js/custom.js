// register function
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

function clearValidNotice(){
    var noticeValids = document.getElementsByName("noticeValid");
    
    for (var i = 0; i < noticeValids.length; i++){
        document.getElementsByName("noticeValid")[i].innerHTML = "";
    }
}

function idValidator(){
    clearValidNotice();

    const MIN_LENGTH = 4;
    const MAX_LENGTH = 16;

    var id = document.getElementById("id").value;
    if (id == null) return;

    if (checkSpace(id)){
        document.getElementById("id_Valid").innerHTML = "ID can't have white spaces";
        document.getElementById("id").focus();
        document.getElementById("id").value = id.replace(' ', '');
        return;
    }

    if (id.length < MIN_LENGTH){
        document.getElementById("id_Valid").innerHTML = "ID must be at least ${MIN_LENGTH} characters";
        return;
    }
    else if (MAX_LENGTH < id.length){
        document.getElementById("id_Valid").innerHTML = "ID must be at most ${MAX_LENGTH} characters";
        return;
    }

    for( var i=0; i < id.length;i++){         
        var c = id.charCodeAt(i);
        // Check each character is included in the range of numbers and alphabet
        if( !( (0x61 <= c && c <= 0x7A) || (0x41 <= c && c <= 0x5A) || (0x30 <= c && c <= 0x39 )) ) {        
            document.getElementById("id_Valid").innerHTML = "Only English and Numbers are allowed for ID";
            return;
        }
      }     
    
    // DB 중복검사 필요 
    document.getElementById("id_Valid").innerHTML = "Available ID";
    return;
};

function nickValidator(){
    clearValidNotice();

    const MIN_LENGTH = 2;
    const MAX_LENGTH = 16;

    var nick = document.getElementById("nickname").value;
    if (nick == null) return;

    if (checkSpace(nick)){
        document.getElementById("nick_Valid").innerHTML = "Nickname can't have white spaces";
        document.getElementById("nickname").focus();
        document.getElementById("nickname").value = nick.replace(' ', '');
        return;
    }

    if (nick.length < MIN_LENGTH){
        document.getElementById("nick_Valid").innerHTML = "Nickname must be at least ${MIN_LENGTH} characters";
        return;
    }
    else if (MAX_LENGTH < nick.length){
        document.getElementById("nick_Valid").innerHTML = "Nickname must be at most ${MAX_LENGTH} characters";
        return;
    } 
    
    document.getElementById("nick_Valid").innerHTML = "Available Nickname";
    return;
};

function pValidator(){
    clearValidNotice();

    const MIN_LENGTH = 8;
    const MAX_LENGTH = 32;

    var pw = document.getElementById("password").value;
    if (pw == null) return;

    var num = pw.search(/[0-9]/g);
    var eng = pw.search(/[a-zA-Z]/ig);
    var spe = pw.search(/[`~!@@#$%^&*|₩₩₩'₩";:₩/?]/gi);
    var kor = pw.search(/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/);

    if (checkSpace(pw)){
        document.getElementById("pass_Valid").innerHTML = "Password can't have white spaces";
        document.getElementById("password").focus();
        document.getElementById("password").value = pw.replace(' ', '');
        return;
    }

    if (kor > 0){
        document.getElementById("pass_Valid").innerHTML = "Password must be alphabet or digit or special symbol";
        return;
    }

    if (pw.length < MIN_LENGTH){
        document.getElementById("pass_Valid").innerHTML = "Password must be at least ${MIN_LENGTH} characters";
        return;
    }
    else if (MAX_LENGTH < pw.length){
        document.getElementById("pass_Valid").innerHTML = "Password must be at most ${MAX_LENGTH} characters";
        return;
    }

    if (num < 0 || eng < 0 || spe < 0){
        document.getElementById("pass_Valid").innerHTML = "Password must contain numbers, alphabets, and special symbols";
    }

    document.getElementById("pass_Valid").innerHTML = "Available Password";
    return;
};

function pcValidator(){
    clearValidNotice();

    var pw = document.getElementById("password").value;
    var pwc = document.getElementById("password_c").value;

    if (pw == null || pwc == null) return;

    if (pw.length == 0){
        document.getElementById("passc_Valid").innerHTML = "Please enter your the password first";
        document.getElementById("password_c").value = "";
        document.getElementById("password").focus();
        return;
    }

    if (!(pw === pwc)){
        document.getElementById("passc_Valid").innerHTML = "Confrim password must be the same as the password";
        return;
    }

    document.getElementById("passc_Valid").innerHTML = "Password Confirmed";
    return;
};

