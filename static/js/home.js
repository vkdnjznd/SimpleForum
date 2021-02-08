import { loginValidate } from './register.js';

function login(id, password){
    var base_url = location.protocol + "//" + location.host;
    var login_url = base_url + '/' + "login";

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
                location.href = base_url;
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
        var base_url = location.protocol + "//" + location.host;
        var logout_url = base_url + '/' + "logout";
        location.href = logout_url;
    })
}

// functions for writing new post
if($('#writeForm').length){
    const MAX_TITLE_LENGTH = 32;
    const MAX_CONTENTS_LENGTH = 300;
    const urlParams = new URLSearchParams(window.location.search);

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
        var board_type = document.getElementById('boardType').value;

        var title_len = title_ele.value.length;
        var contents_len = contents_ele.value.length;

        if (board_type == 'Secret'){
            var post_password = document.getElementById('postPassword').value;
            var exp = post_password.search(/[^0-9]/g);

            if (post_password.length == 0 || 4 < post_password.length){
                alert("Post password consist of only four digits");
                if (exp != -1)
                    document.getElementById('postPassword').value = post_password.replace(/[^0-9]/g, "");

                document.getElementById('postPassword').focus();
                return;
            }
        }

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

            if (this.innerText == 'Secret')
                $('#postPasswordArea').css('display', '');
            else
                $('#postPasswordArea').css('display', 'none');

            $('.dropdown-menu').toggle();
        })
    }

}

if($('#boardPost').length){
    var postEle = document.querySelectorAll('#boardPost');

    for (var i = 0; i < postEle.length; i++){
        postEle[i].addEventListener('click', function(){
            const urlParams = new URLSearchParams(window.location.search); // get parameters from current URL
            
            var base_url = location.protocol + "//" + location.host;
            var board_url = base_url + '/' + "board";
            var type = urlParams.get('type');
            var page = urlParams.get('page');
            var id = this.firstElementChild.textContent;

            location.href = board_url + "?" + "type=" + type + "&page=" + page + "&boardNum=" + id;
        });    
    }
}

if($('#detailView').length){
    if($('#postDeleteBtn').length){
        document.querySelector('#postDeleteBtn').addEventListener('click', function(){
            var deleteCheck = confirm('Are you sure to delete this post?');
            if (!deleteCheck)
                return;

            const urlParams = new URLSearchParams(window.location.search); // get parameters from current URL
            
            var base_url = location.protocol + "//" + location.host;
            var delete_url = base_url + '/' + "deletePost";
            var board_url = base_url + '/' + "board";

            var type = urlParams.get('type');
            var page = urlParams.get('page');
            var boardNum = urlParams.get('boardNum');

            var csrf_token = $('input[name="csrf_token"]').attr('value');
            $.ajaxSetup({
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                }
            });

            $.ajax({
                type: "POST",
                url: delete_url,
                async: false,
                data: {'type' : type, 'page' : page, 'boardNum' : boardNum},
                dataType: "JSON",
                success: function(res){
                    if (res['result'] == "OK"){
                        alert("Delete Complete");
                        location.href = board_url + "?" + "type=" + type + "&page=" + page;
                    }
                    else{
                        alert(res['result']);
                    }
                },
                error: function(request, status, error){
                    console.log(request.status);
                }
            });
        });

        document.querySelector('#postUpdateBtn').addEventListener('click', function(){
            const urlParams = new URLSearchParams(window.location.search); // get parameters from current URL
            
            var base_url = location.protocol + "//" + location.host;
            var boardWrite_url = base_url + '/' + "board_write";

            var title = document.getElementById('title').innerText;
            var contents = document.getElementById('contents').innerText;
            var type = urlParams.get('type');
            var page = urlParams.get('page');
            var boardNum = urlParams.get('boardNum');

            location.href = boardWrite_url + "?" + "type=" + type + "&page=" + page + "&boardNum=" + boardNum +
                            "&title=" + title + "&contents=" + contents;
        });
    }

    document.querySelector('#goListBtn').addEventListener('click', function(){
        const urlParams = new URLSearchParams(window.location.search); // get parameters from current URL
        
        var base_url = location.protocol + "//" + location.host;
        var board_url = base_url + '/' + "board";

        var type = urlParams.get('type');
        var page = urlParams.get('page');

        location.href = board_url + "?" + "type=" + type + "&page=" + page;
    });
}