import { loginValidate } from './register.js';

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

// functions for writing new post
if($('#writeForm').length){
    const MAX_TITLE_LENGTH = 32;
    const MAX_CONTENTS_LENGTH = 300;

    document.querySelector('#title').addEventListener('keyup', function(){
        var title_len = this.value.length;
        if (title_len > MAX_TITLE_LENGTH){
            alert("Maximum title length must be at most "+ MAX_TITLE_LENGTH);
            this.value = this.value.substr(0, MAX_TITLE_LENGTH);
            this.focus();
        }

        return;
    });

    document.querySelector('#contents').addEventListener('keyup', function(){
        var contents_len = this.value.length;
        if (contents_len > MAX_CONTENTS_LENGTH){
            alert("Maximum contents length must be at most "+ MAX_CONTENTS_LENGTH);
            this.value = this.value.substr(0, MAX_CONTENTS_LENGTH);
            this.focus();
        }

        return;
    });

    document.querySelector('#writeForm').addEventListener('submit', function(event){
        event.preventDefault();

        var title_ele = document.getElementById('title');
        var contents_ele = document.getElementById('contents');
        var title_len = title_ele.value.length;
        var contents_len = contents_ele.value.length;

        if (0 == title_len || title_len > MAX_TITLE_LENGTH){
            alert("Check this input");
            title_ele.focus();
            return;
        }
        else if (0 == contents_len || contents_len > MAX_CONTENTS_LENGTH){
            alert("Check this input");
            contents_ele.focus();
            return;
        }
        else{
            this.submit();
        }
        
    });

    // dropdown list eventListener
    document.querySelector('#boardTypeMenu').addEventListener('click', function(){
        $('.dropdown-menu').toggle();
    });

    var typeCells = document.querySelectorAll('#typeCell');
    for (var i = 0; i < typeCells.length; i++){
        typeCells[i].addEventListener('click', function(){
            document.getElementById('boardTypeMenu').innerText = this.innerText;
            $('#boardType').attr('value', this.innerText);
            $('.dropdown-menu').toggle();
        })
    }
}

if($('#boardPost').length){
    var postEle = document.querySelectorAll('#boardPost');

    for (var i = 0; i < postEle.length; i++){
        postEle[i].addEventListener('click', function(){
            const urlParams = new URLSearchParams(window.location.search); // get parameters from current URL
            
            var current_url = location.protocol + "//" + location.host;
            var board_url = current_url + '/' + "board";
            var type = urlParams.get('type');
            var page = urlParams.get('page');
            var id = this.firstElementChild.textContent;

            location.href = board_url + "?" + "type=" + type + "&page=" + page + "&boardNum=" + id;
        });    
    }
}
