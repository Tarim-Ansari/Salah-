// const mainBtn = document.querySelector(".main-btn");
// if (mainBtn) {
//     mainBtn.addEventListener("click", () => {
//         // homepage logic (if any)
//     });
// }
function goToLogin(role){
    localStorage.setItem("userRole", role);
    window.location.href = "login.html";
}

function goToSignup(){
    window.location.href = "signup.html";
}

function goToLoginPage(){
    window.location.href = "login.html";
}

window.onload = function(){
    let role = localStorage.getItem("userRole");

    if(document.getElementById("roleText")){
        document.getElementById("roleText").innerText = "Login as " + role;
    }

    if(document.getElementById("roleInput")){
        document.getElementById("roleInput").value = role;
    }
};
