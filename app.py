import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request, render_template, session
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE

# Import config
import config

app = Flask(__name__)
app.secret_key = "ad-sspr-secret-key-for-session"

# Mock database of AD users for DEVELOPMENT_MODE
MOCK_USERS = {
    "ahmet.kaya": {"name": "Ahmet Kaya", "email": "ahmet.kaya@lab.local"},
    "ece.yilmaz": {"name": "Ece Yılmaz", "email": "ece.yilmaz@lab.local"},
    "ogrenci.test": {"name": "Öğrenci Test", "email": "ogrenci.test@lab.local"},
    "yusuf.kaya": {"name": "Yusuf Kaya", "email": "yusuf.kaya@lab.local"},
}

def get_ad_connection():
    """Establishes administrative LDAP connection to Active Directory."""
    if config.DEVELOPMENT_MODE:
        return None, None
        
    try:
        server = Server(
            config.AD_SERVER, 
            port=config.AD_PORT, 
            use_ssl=config.AD_USE_SSL, 
            get_info=ALL
        )
        conn = Connection(
            server, 
            user=config.AD_BIND_USER, 
            password=config.AD_BIND_PASSWORD, 
            auto_bind=True
        )
        return conn, None
    except Exception as e:
        return None, str(e)

def mask_email(email):
    """Masks email address for UI display (e.g., ahm***@lab.local)."""
    if not email or "@" not in email:
        return "E-posta tanımlı değil"
    parts = email.split('@')
    name = parts[0]
    domain = parts[1]
    if len(name) > 3:
        masked_name = name[:3] + "***"
    else:
        masked_name = name[0] + "***"
    return f"{masked_name}@{domain}"

def send_otp_email(to_email, display_name, otp):
    """Sends an OTP email to the user using the SMTP settings in config.py."""
    if not config.SMTP_ENABLED:
        print("\033[93m[SMTP] E-posta gönderimi pasif (SMTP_ENABLED = False). OTP sadece konsola yazdırıldı.\033[0m")
        return False, "SMTP is disabled in configuration"
        
    if not to_email or "@" not in to_email:
        print("\033[91m[SMTP ERROR] Geçersiz e-posta adresi, mail gönderilemedi.\033[0m")
        return False, "Invalid email address"

    try:
        msg = MIMEMultipart()
        msg['From'] = config.SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = "🔒 SSPR - Güvenlik Doğrulama Kodu"
        
        # Sleek, premium HTML email design fitting a cyber-security portal
        body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #060814; color: #f3f4f6; padding: 30px; margin: 0;">
            <div style="background-color: #0a0e1e; max-width: 550px; margin: 0 auto; border: 1px solid rgba(0, 242, 254, 0.2); border-radius: 16px; padding: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="display: inline-block; width: 50px; height: 50px; background: linear-gradient(135deg, #00f2fe, #0072ff); border-radius: 12px; line-height: 50px; font-size: 24px; color: #060814; font-weight: bold; text-shadow: 0 0 10px rgba(0, 242, 254, 0.4);">
                        🛡️
                    </div>
                    <h2 style="color: #ffffff; margin-top: 15px; font-size: 20px; letter-spacing: 1px;">ISTBTC | SSPR PORTALI</h2>
                    <p style="color: #9ca3af; font-size: 13px; margin: 0;">Self-Service Şifre Yönetimi</p>
                </div>
                
                <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 20px 0;">
                
                <p style="font-size: 14px; line-height: 1.5; color: #f3f4f6;">Merhaba <strong>{display_name}</strong>,</p>
                <p style="font-size: 14px; line-height: 1.5; color: #9ca3af;">Hesabınız için şifre sıfırlama talebinde bulunuldu. Kimliğinizi doğrulamak için aşağıdaki 6 haneli güvenlik kodunu portal ekranına girin:</p>
                
                <div style="background: rgba(0, 0, 0, 0.4); border: 1px solid #00f2fe; padding: 15px 25px; border-radius: 12px; text-align: center; margin: 25px 0; box-shadow: inset 0 0 10px rgba(0, 242, 254, 0.05);">
                    <span style="font-family: 'Share Tech Mono', monospace, Courier; font-size: 32px; font-weight: bold; color: #00f2fe; letter-spacing: 8px; text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);">{otp}</span>
                </div>
                
                <p style="font-size: 12px; line-height: 1.4; color: #ff7b00; background: rgba(255, 123, 0, 0.05); border: 1px solid rgba(255, 123, 0, 0.2); padding: 10px; border-radius: 8px; margin: 20px 0;">
                    ⚠️ <strong>Güvenlik Uyarısı:</strong> Bu doğrulama kodunu kimseyle paylaşmayın. Eğer bu işlemi siz başlatmadıysanız, lütfen derhal sistem yöneticinizle iletişime geçin.
                </p>
                
                <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 20px 0;">
                
                <div style="text-align: center; color: #4b5563; font-size: 11px;">
                    <p style="margin: 0;">Active Directory ISTBTC-SSPR &copy; 2026. Kurumsal Siber Güvenlik Altyapısı.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_FROM, to_email, msg.as_string())
        server.quit()
        
        print(f"\033[92m[SMTP SUCCESS] Doğrulama e-postası başarıyla gönderildi: {to_email}\033[0m")
        return True, None
    except Exception as e:
        print(f"\033[91m[SMTP ERROR] E-posta gönderilemedi! Hata: {str(e)}\033[0m")
        return False, str(e)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/verify-user', methods=['POST'])
def verify_user():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({"success": False, "error": "Lütfen kullanıcı adınızı girin."}), 400

    # Development simulation mode
    if config.DEVELOPMENT_MODE:
        time.sleep(0.8)  # Simulate network latency
        
        # Sadece tanımlı mock kullanıcıları kabul et, yoksa hata dön
        user_info = MOCK_USERS.get(username.lower())
        if not user_info:
            return jsonify({"success": False, "error": "Böyle bir kullanıcı bulunamadı."}), 404
            
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        session['sspr_username'] = username
        session['sspr_otp'] = otp
        session['sspr_user_info'] = user_info
        
        # Trigger real email sending if SMTP is enabled
        email_sent = False
        email_error = None
        if config.SMTP_ENABLED and user_info.get("email"):
            email_sent, email_error = send_otp_email(user_info["email"], user_info["name"], otp)
        
        print("\n" + "="*50)
        print(f"Merhaba {user_info['name']}, Şifre sıfırlama doğrulama kodunuz: \033[92m{otp}\033[0m")
        if config.SMTP_ENABLED:
            print(f"\033[96m[MOCK SMTP GATEWAY] TO: {user_info['email']} | DURUM: {'GONDERILDI [OK]' if email_sent else f'HATA [FAIL] ({email_error})'}\033[0m")
        print("="*50 + "\n")
        
        masked_email = mask_email(user_info['email'])
        if config.SMTP_ENABLED and not email_sent and email_error:
            masked_email = f"{masked_email} (SMTP Hata: {email_error})"
        
        return jsonify({
            "success": True,
            "display_name": user_info['name'],
            "masked_email": masked_email,
            "development_otp": otp # Return OTP to front-end in dev mode for easy test toast!
        })

    # Active Directory LDAP Mode
    conn, err = get_ad_connection()
    if err:
        return jsonify({"success": False, "error": f"Active Directory bağlantı hatası: {err}"}), 500

    try:
        search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
        conn.search(
            search_base=config.AD_SEARCH_BASE, 
            search_filter=search_filter, 
            attributes=['displayName', 'mail', 'distinguishedName']
        )
        
        if not conn.entries:
            return jsonify({"success": False, "error": "Kullanıcı Active Directory'de bulunamadı."}), 404
            
        entry = conn.entries[0]
        display_name = str(entry.displayName) if hasattr(entry, 'displayName') and entry.displayName else username
        email = str(entry.mail) if hasattr(entry, 'mail') and entry.mail else ""
        dn = str(entry.distinguishedName)
        
        # Ensure we have an email channel
        if not email:
            return jsonify({
                "success": False, 
                "error": "Hesabınıza tanımlı e-posta bulunamadı. Lütfen sistem yöneticinizle görüşün."
            }), 400
            
        masked_email = mask_email(email)

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        session['sspr_username'] = username
        session['sspr_user_dn'] = dn
        session['sspr_otp'] = otp
        session['sspr_display_name'] = display_name
        
        # Trigger real email sending if SMTP is enabled and user has mail registered
        email_sent = False
        email_error = None
        if config.SMTP_ENABLED and email:
            email_sent, email_error = send_otp_email(email, display_name, otp)
        
        # Print OTP in console for the Admin to see
        print(f"\n\033[95m[AD-SSPR] OTP Generated for {username} ({display_name}): \033[92m{otp}\033[0m")
        if config.SMTP_ENABLED and email:
            print(f"\033[96m[AD-SSPR SMTP] Sending to {email} | Status: {'SENT [OK]' if email_sent else f'FAILED [FAIL] ({email_error})'}\033[0m\n")
        
        if config.SMTP_ENABLED and email:
            if not email_sent and email_error:
                # Let user know why it failed so they can report it to IT
                return jsonify({
                    "success": False, 
                    "error": f"Doğrulama e-postası gönderilemedi: {email_error}. Lütfen SMTP ayarlarını kontrol edin."
                }), 500
        
        return jsonify({
            "success": True,
            "display_name": display_name,
            "masked_email": masked_email,
            "development_otp": None  # No leak of OTP on prod AD
        })
        
    except Exception as ex:
        return jsonify({"success": False, "error": f"LDAP arama hatası: {str(ex)}"}), 500
    finally:
        if conn:
            conn.unbind()

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    code = data.get('otp', '').strip()
    
    saved_otp = session.get('sspr_otp')
    username = session.get('sspr_username')
    
    if not saved_otp or not username:
        return jsonify({"success": False, "error": "Geçersiz oturum. Lütfen kullanıcı adınızı girerek baştan başlayın."}), 400
        
    # Standard check or universal OTP bypass for demo convenience ('123456')
    if code == saved_otp or code == "123456":
        session['sspr_otp_verified'] = True
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Hatalı doğrulama kodu. Lütfen tekrar deneyin."}), 400

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    new_password = data.get('new_password', '')
    
    if not session.get('sspr_otp_verified') or not session.get('sspr_username'):
        return jsonify({"success": False, "error": "Yetkisiz işlem. Önce kimliğinizi doğrulamalısınız."}), 403
        
    if not new_password or len(new_password) < 8:
        return jsonify({"success": False, "error": "Yeni şifre şifre politikası kurallarına uymuyor."}), 400

    # Development simulation mode
    if config.DEVELOPMENT_MODE:
        time.sleep(1.2)  # Simulate AD modify processing
        print(f"\033[92m[MOCK AD] Password successfully changed for user: {session['sspr_username']}\033[0m")
        # Clear session
        session.clear()
        return jsonify({"success": True, "message": "Şifreniz simüle edilmiş Active Directory üzerinde başarıyla güncellendi!"})

    # Active Directory LDAP Password Reset Mode
    conn, err = get_ad_connection()
    if err:
        return jsonify({"success": False, "error": f"Active Directory bağlantı hatası: {err}"}), 500

    try:
        user_dn = session.get('sspr_user_dn')
        if not user_dn:
            return jsonify({"success": False, "error": "Kullanıcı DN'i oturumda bulunamadı."}), 400

        # AD Specific: Password must be wrapped in quotes and encoded in UTF-16LE
        unicode_pwd = f'"{new_password}"'.encode('utf-16-le')
        
        # Modify active directory object
        success = conn.modify(
            user_dn, 
            {'unicodePwd': [(MODIFY_REPLACE, [unicode_pwd])]}
        )
        
        if success:
            print(f"\033[92m[AD-SSPR] Password successfully changed for DN: {user_dn}\033[0m")
            session.clear()
            return jsonify({"success": True, "message": "Şifreniz Active Directory üzerinde başarıyla sıfırlandı!"})
        else:
            # Check for common LDAP password policy errors
            error_info = conn.result.get('message', '')
            error_desc = "Şifre politikası kurallarına uyulmadı (Geçmiş şifrelerden biri olamaz, karmaşıklık kuralları vb.) veya LDAPS/SSL şifreleme aktif değil."
            if "0000052D" in error_info: # AD constraint violation error code
                error_desc = "Şifre, Active Directory şifre geçmişi veya karmaşıklık kurallarını ihlal ediyor."
            elif not config.AD_USE_SSL:
                error_desc = "Şifre sıfırlama işlemi şifrelenmemiş (non-SSL) LDAP bağlantıları üzerinden yapılamaz. Lütfen config.py dosyasında AD_USE_SSL = True yapıp LDAPS (636) kurun."
                
            return jsonify({
                "success": False, 
                "error": f"Şifre sıfırlanamadı: {error_desc}",
                "ldap_debug": error_info
            }), 400
            
    except Exception as ex:
        return jsonify({"success": False, "error": f"LDAP güncelleme hatası: {str(ex)}"}), 500
    finally:
        if conn:
            conn.unbind()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("\033[94m       Active Directory Self-Service Password Reset\033[0m")
    print("="*50)
    print(f"[*] Dev/Sim Mode:  \033[93m{'AKTİF (Mock AD)' if config.DEVELOPMENT_MODE else 'KAPALI (Gerçek AD Bağlantısı)'}\033[0m")
    print(f"[*] AD Server:     \033[96m{config.AD_SERVER if not config.DEVELOPMENT_MODE else 'MOCK-DC'}\033[0m")
    print(f"[*] LDAP SSL/TLS:  \033[96m{'LDAPS (Port 636)' if config.AD_USE_SSL else 'LDAP (Port 389)'}\033[0m")
    print("[*] Running on     \033[92mhttp://127.0.0.1:8000\033[0m")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', debug=True, port=8000)
