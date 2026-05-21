// --- Active Directory SSPR Front-End Controller ---

document.addEventListener("DOMContentLoaded", () => {
    let currentStep = 1;
    let username = "";
    
    // DOM Elements - Sections
    const section1 = document.getElementById("section-step-1");
    const section2 = document.getElementById("section-step-2");
    const section3 = document.getElementById("section-step-3");
    const sectionSuccess = document.getElementById("section-step-success");
    const sections = [section1, section2, section3, sectionSuccess];

    // DOM Elements - Progress Bar
    const pStep1 = document.getElementById("p-step-1");
    const pStep2 = document.getElementById("p-step-2");
    const pStep3 = document.getElementById("p-step-3");
    const pLine1 = document.getElementById("p-line-1");
    const pLine2 = document.getElementById("p-line-2");

    // DOM Elements - Inputs & Outputs
    const inputUsername = document.getElementById("username");
    const displayMaskedEmail = document.getElementById("display-masked-email");
    const inputOtp = document.getElementById("otp-code");
    const inputNewPassword = document.getElementById("new-password");
    const inputConfirmPassword = document.getElementById("confirm-password");
    const successMessage = document.getElementById("success-message");
    const successProtocol = document.getElementById("success-protocol");

    // DOM Elements - Buttons
    const btnNext1 = document.getElementById("btn-next-1");
    const btnNext2 = document.getElementById("btn-next-2");
    const btnBack2 = document.getElementById("btn-back-2");
    const btnSubmitReset = document.getElementById("btn-submit-reset");
    const btnRestart = document.getElementById("btn-restart");
    
    // DOM Elements - Passwords utilities
    const togglePwd1 = document.getElementById("toggle-pwd-1");
    const togglePwd2 = document.getElementById("toggle-pwd-2");
    const pwdStrengthBar = document.getElementById("pwd-strength-bar");
    const pwdStrengthTxt = document.getElementById("pwd-strength-txt");
    
    // Requirements Checklist items
    const reqLength = document.getElementById("req-length");
    const reqUpper = document.getElementById("req-upper");
    const reqNumber = document.getElementById("req-number");
    const reqSpecial = document.getElementById("req-special");

    /* --- Step Navigation Function --- */
    function goToStep(step) {
        currentStep = step;
        
        // Hide all sections, show current
        sections.forEach((sec, idx) => {
            if (idx === step - 1) {
                sec.classList.add("active");
            } else {
                sec.classList.remove("active");
            }
        });

        // Update progress bar visuals
        if (step === 1) {
            pStep1.className = "progress-step active";
            pStep2.className = "progress-step";
            pStep3.className = "progress-step";
            pLine1.className = "progress-line";
            pLine2.className = "progress-line";
        } else if (step === 2) {
            pStep1.className = "progress-step completed";
            pStep2.className = "progress-step active";
            pStep3.className = "progress-step";
            pLine1.className = "progress-line completed";
            pLine2.className = "progress-line";
        } else if (step === 3) {
            pStep1.className = "progress-step completed";
            pStep2.className = "progress-step completed";
            pStep3.className = "progress-step active";
            pLine1.className = "progress-line completed";
            pLine2.className = "progress-line completed";
        } else if (step === 4) { // Success State
            pStep1.className = "progress-step completed";
            pStep2.className = "progress-step completed";
            pStep3.className = "progress-step completed";
            pLine1.className = "progress-line completed";
            pLine2.className = "progress-line completed";
        }
    }

    /* --- AŞAMA 1: Kullanıcı Sorgulama --- */
    btnNext1.addEventListener("click", async () => {
        username = inputUsername.value.trim();
        if (!username) {
            showToast("Giriş Hatası", "Lütfen Active Directory kullanıcı adınızı girin.", "error");
            return;
        }

        // Set Loading state
        setBtnLoading(btnNext1, true, "Sorgulanıyor...");

        try {
            const response = await fetch("/api/verify-user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: username })
            });

            const data = await response.json();

            if (data.success) {
                // Update UI text
                displayMaskedEmail.textContent = data.masked_email;
                successMessage.innerHTML = `Tebrikler <strong>${data.display_name}</strong>, şifreniz Active Directory üzerinde anlık olarak sıfırlandı ve dizinde güncellendi.`;
                
                // Show dev-mode OTP toast if available
                if (data.development_otp) {
                    showToast("Simülatör Aktif 📱", `E-posta adresinize gönderilen test kodu: <strong>${data.development_otp}</strong>`, "success");
                } else {
                    showToast("Kod Gönderildi", "E-posta adresinize doğrulama kodu başarıyla iletildi.", "success");
                }

                // Proceed to Step 2
                goToStep(2);
                // Auto focus OTP field
                setTimeout(() => inputOtp.focus(), 100);
            } else {
                showToast("AD Bulunamadı", data.error || "Kullanıcı sorgulama başarısız.", "error");
            }
        } catch (error) {
            showToast("Bağlantı Hatası", "AD sorgu sunucusu ile bağlantı kurulamadı.", "error");
        } finally {
            setBtnLoading(btnNext1, false, "Devam Et <i class='fa-solid fa-arrow-right-long'></i>");
        }
    });

    // Press enter on username input
    inputUsername.addEventListener("keypress", (e) => {
        if (e.key === "Enter") btnNext1.click();
    });

    /* --- AŞAMA 2: OTP Doğrulama --- */
    btnBack2.addEventListener("click", () => {
        goToStep(1);
    });

    btnNext2.addEventListener("click", async () => {
        const otpCode = inputOtp.value.trim();
        if (!otpCode || otpCode.length < 6) {
            showToast("Eksik Kod", "Lütfen 6 haneli doğrulama kodunu girin.", "error");
            return;
        }

        setBtnLoading(btnNext2, true, "Doğrulanıyor...");

        try {
            const response = await fetch("/api/verify-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ otp: otpCode })
            });

            const data = await response.json();

            if (data.success) {
                showToast("Kimlik Doğrulandı", "Giriş yetkisi sağlandı. Yeni şifrenizi belirleyin.", "success");
                goToStep(3);
                // Auto focus password field
                setTimeout(() => inputNewPassword.focus(), 100);
            } else {
                showToast("Hatalı Kod", data.error || "Doğrulama kodu geçersiz.", "error");
            }
        } catch (error) {
            showToast("Bağlantı Hatası", "Kimlik doğrulama API'sine erişilemedi.", "error");
        } finally {
            setBtnLoading(btnNext2, false, "Kodu Doğrula <i class='fa-solid fa-shield-checkmark'></i>");
        }
    });

    // Auto trigger verification when 6 digits are typed
    inputOtp.addEventListener("input", () => {
        // Strip non-digits
        inputOtp.value = inputOtp.value.replace(/\D/g, "");
        if (inputOtp.value.length === 6) {
            btnNext2.click();
        }
    });

    /* --- AŞAMA 3: Şifre Mukavemet ve Kriter Kontrolü --- */
    
    // Toggle Password visibility
    setupPasswordToggle(inputNewPassword, togglePwd1);
    setupPasswordToggle(inputConfirmPassword, togglePwd2);

    function setupPasswordToggle(inputEl, btnEl) {
        btnEl.addEventListener("click", () => {
            const icon = btnEl.querySelector("i");
            if (inputEl.type === "password") {
                inputEl.type = "text";
                icon.className = "fa-regular fa-eye-slash";
            } else {
                inputEl.type = "password";
                icon.className = "fa-regular fa-eye";
            }
        });
    }

    // Live password criteria auditor
    inputNewPassword.addEventListener("input", validateAndRatePassword);
    inputConfirmPassword.addEventListener("input", validateAndRatePassword);

    function validateAndRatePassword() {
        const pwd = inputNewPassword.value;
        const confirmPwd = inputConfirmPassword.value;

        // 1. Audit Criteria
        const criteria = {
            length: pwd.length >= 8,
            upper: /[A-Z]/.test(pwd),
            number: /[0-9]/.test(pwd),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(pwd)
        };

        // Update Checklist visual states
        updateCriteriaUI(reqLength, criteria.length);
        updateCriteriaUI(reqUpper, criteria.upper);
        updateCriteriaUI(reqNumber, criteria.number);
        updateCriteriaUI(reqSpecial, criteria.special);

        // 2. Calculate Strength Score (0 to 4)
        let score = 0;
        if (criteria.length) score++;
        if (criteria.upper) score++;
        if (criteria.number) score++;
        if (criteria.special) score++;

        // Update Strength Bar & Labels
        if (pwd.length === 0) {
            pwdStrengthBar.style.width = "0%";
            pwdStrengthBar.style.backgroundColor = "transparent";
            pwdStrengthTxt.textContent = "Çok Zayıf";
            pwdStrengthTxt.className = "strength-low";
        } else if (score <= 1) {
            pwdStrengthBar.style.width = "25%";
            pwdStrengthBar.style.backgroundColor = "var(--status-red)";
            pwdStrengthTxt.textContent = "Kritik / Zayıf 🔴";
            pwdStrengthTxt.className = "strength-low";
        } else if (score === 2) {
            pwdStrengthBar.style.width = "50%";
            pwdStrengthBar.style.backgroundColor = "var(--status-orange)";
            pwdStrengthTxt.textContent = "Orta Güçlükte 🟡";
            pwdStrengthTxt.className = "strength-medium";
        } else if (score === 3) {
            pwdStrengthBar.style.width = "75%";
            pwdStrengthBar.style.backgroundColor = "var(--accent-cyan)";
            pwdStrengthTxt.textContent = "Güçlü Şifre 🔵";
            pwdStrengthTxt.className = "strength-high";
        } else if (score === 4) {
            pwdStrengthBar.style.width = "100%";
            pwdStrengthBar.style.backgroundColor = "var(--status-green)";
            pwdStrengthTxt.textContent = "Mükemmel / Sızdırılamaz 🟢";
            pwdStrengthTxt.className = "strength-high";
        }

        // 3. Match Checking & Button enabling
        const allCriteriaMet = criteria.length && criteria.upper && criteria.number && criteria.special;
        const matches = pwd === confirmPwd && pwd.length > 0;

        if (allCriteriaMet && matches) {
            btnSubmitReset.disabled = false;
        } else {
            btnSubmitReset.disabled = true;
        }
    }

    function updateCriteriaUI(element, isMet) {
        const icon = element.querySelector("i");
        if (isMet) {
            element.classList.add("met");
            icon.className = "fa-solid fa-circle-check status-check";
        } else {
            element.classList.remove("met");
            icon.className = "fa-solid fa-circle-xmark status-x";
        }
    }

    // Submit Password Reset to Active Directory
    btnSubmitReset.addEventListener("click", async () => {
        const newPassword = inputNewPassword.value;
        
        setBtnLoading(btnSubmitReset, true, "AD Güncelleniyor...");

        try {
            const response = await fetch("/api/reset-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ new_password: newPassword })
            });

            const data = await response.json();

            if (data.success) {
                showToast("Şifre Değiştirildi", "Active Directory şifreniz başarıyla sıfırlandı.", "success");
                
                // Show protocol state
                successProtocol.textContent = data.message.includes("simüle") ? "MOCK-LDAP / unicodePwd Simulation" : "LDAPS (Secure Port 636) / unicodePwd Modification";
                
                // Transition to success screen
                goToStep(4);
            } else {
                showToast("AD İlke Hatası", data.error || "Şifre sıfırlanamadı.", "error");
            }
        } catch (error) {
            showToast("Bağlantı Hatası", "Dizin denetleyicisi ile iletişim kesildi.", "error");
        } finally {
            setBtnLoading(btnSubmitReset, false, "Şifreyi Active Directory'de Güncelle <i class='fa-solid fa-cloud-arrow-up'></i>");
        }
    });

    /* --- AŞAMA 4: Sıfırlama ve Baştan Başlama --- */
    btnRestart.addEventListener("click", () => {
        // Clear all inputs
        inputUsername.value = "";
        inputOtp.value = "";
        inputNewPassword.value = "";
        inputConfirmPassword.value = "";
        
        // Reset strength UI
        validateAndRatePassword();
        
        // Return to step 1
        goToStep(1);
    });

    /* --- Helper Functions --- */
    
    function setBtnLoading(btnEl, isLoading, loadingHtml) {
        if (isLoading) {
            btnEl.disabled = true;
            btnEl.setAttribute("data-original-html", btnEl.innerHTML);
            btnEl.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> ${loadingHtml}`;
        } else {
            btnEl.disabled = false;
            btnEl.innerHTML = btnEl.getAttribute("data-original-html") || loadingHtml;
        }
    }

    function showToast(title, desc, type = "success") {
        const container = document.getElementById("toast-container");
        
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        
        let iconClass = "fa-circle-check";
        if (type === "error") iconClass = "fa-circle-exclamation";
        
        toast.innerHTML = `
            <i class="fa-solid ${iconClass}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-desc">${desc}</div>
            </div>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => toast.classList.add("show"), 10);
        
        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => toast.remove(), 300);
        }, 4500);
    }
});
