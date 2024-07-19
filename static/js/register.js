const usernameField = document.querySelector('#usernameField')
const feedbackField =document.querySelector(".invalid-feedback")
const emailField = document.querySelector('#emailField')
const emailfeedbackField = document.querySelector('#emailfeedbackField')
const usernameChecking = document.querySelector('.username-check')
const emailChecking = document.querySelector('.email-check')
const showTogglePassword = document.querySelector('.showTogglePassword')
const passwordField = document.querySelector('#passwordField')
const passwordField2 = document.querySelector('#passwordField2')
const submitBtn = document.querySelector('.submit-btn')

document.addEventListener('DOMContentLoaded', () => {
    const closeBtn = document.querySelector('.btn-close');
    const alertContent = document.querySelector('.message-content');

    if (alertContent) {
        setTimeout(() => {
            alertContent.style.display = "none";
        }, 3000);

        closeBtn.addEventListener('click', () => {
            alertContent.style.display = "none";
        });
    }
});


const handleToggleInput = (e) => {
    if (showTogglePassword.textContent ==="SHOW") {
        showTogglePassword.textContent = "HIDE"
        passwordField.setAttribute("type","text")
        passwordField2.setAttribute("type","text")
    } else {
        showTogglePassword.textContent = "SHOW"
        passwordField.setAttribute("type","password")
        passwordField2.setAttribute("type","password")
    }
}


showTogglePassword.addEventListener('click', handleToggleInput);



    emailField.addEventListener('keyup', (e) =>{
         console.log("7777", 7777);
         const emailVal=e.target.value;
         emailChecking.style.display="block"
         emailChecking.textContent=`Checking ${emailVal}`

        if (emailVal.length > 0) {
            fetch("/authentication/validate-email", {
                body: JSON.stringify({ email: emailVal}),
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
             })
             .then((res) => res.json())
             .then((data) => {
               
                emailChecking.textContent=`Checking ${emailVal}`
                setTimeout(() => {
                    emailChecking.style.display = "none";
                }, 1000);
                console.log('data', data);
            if(data.email_error){
                submitBtn.disabled = true
                emailField.classList.add("is-invalid")
                emailfeedbackField.style.display = "block"
                emailfeedbackField.innerHTML = `<p>${data.email_error}</p>`;
            }
            else {
                // Check if email field does not have error
                const usernameVal = usernameField.value;
                if (!usernameVal || !usernameField.classList.contains("is-invalid")) {
                    submitBtn.removeAttribute('disabled');
                }
                emailField.classList.remove("is-invalid");
                emailfeedbackField.style.display = "none";
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        }
        
    })



    usernameField.addEventListener('keyup', (e)=>{
   
    const usernameVal=e.target.value;
    usernameChecking.style.display="block"
    usernameChecking.textContent=`Checking ${usernameVal}`

    if (usernameVal.length > 0) {
        fetch("/authentication/validate-username", {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then((res) => res.json())
        .then((data) => {
            if (usernameVal.length > 0) {

                usernameChecking.textContent=`Checking ${usernameVal}`
            setTimeout(() => {
                usernameChecking.style.display = "none";
            }, 1000);
            }
            
            console.log('data', data);
            if(data.username_error){
                submitBtn.disabled = true
                usernameField.classList.add("is-invalid")
                feedbackField.style.display = "block"
                feedbackField.innerHTML = `<p>${data.username_error}</p>`;
            }
            else {
                // Check if email field does not have error
                const emailVal = emailField.value;
                if (!emailVal || !emailField.classList.contains("is-invalid")) {
                    submitBtn.removeAttribute('disabled');
                }
                usernameField.classList.remove("is-invalid");
                feedbackField.style.display = "none";
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
    
    
})
