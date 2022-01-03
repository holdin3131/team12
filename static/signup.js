function register() {
    $.ajax({
        type: "POST",
        url: "/api/register",
        data: {
            id_give: $('#userid').val(),
            pw_give: $('#userpw').val(),
            fullname_give: $('#fullname').val(),
            username_give: $('#username').val()

        },
        success: function (response) {
            if (response['result'] == 'success') {
                alert('회원가입이 완료되었습니다.')
                window.location.href = '/login'
            } else {
                alert(response['msg'])
            }
        }
    })
}
function login_page() {
    window.location.href = "/login"
}
//
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