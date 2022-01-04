//{% if msg %}
//alert("{{ msg }}")
//{% endif %}

function login() {
    $.ajax({
        type: "POST",
        url: "/api/login",
        data: {id_give: $('#userid').val(), pw_give: $('#userpw').val()},
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token']);

                alert('로그인 완료!')
                window.location.href = '/main'
            } else {
                alert(response['msg'])
            }
        }
    })
}

function signup_page() {
    window.location.href = "/signup"
}

// const loginButton = document.querySelector(".loginBtn");
//
// loginButton.addEventListener("click", function () {
//     const loginId = document.querySelector(".id").value;
//     const loginPassword = document.querySelector(".password").value;
//
//     loginId && loginPassword
//         ? (document.querySelector(".loginBtn").style.backgroundColor = "blue")
//         : 0;
// });