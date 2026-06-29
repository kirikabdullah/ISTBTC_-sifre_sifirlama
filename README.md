# Active Directory Self-Service Password Reset (SSPR) Portal

Bu proje, şirket veya laboratuvar ağlarındaki (Intranet) Active Directory kullanıcılarının, şifrelerini unuttuklarında IT departmanına (Bilgi İşlem) ihtiyaç duymadan kendi kendilerine şifrelerini sıfırlayabilmelerini sağlayan web tabanlı bir **SSPR (Self-Service Password Reset)** uygulamasıdır.

## 🚀 Özellikler
- **OTP (Tek Kullanımlık Şifre) Doğrulaması:** Kullanıcı sisteme adını girdiğinde, Active Directory'de kayıtlı e-posta adresine 6 haneli güvenli bir doğrulama kodu gönderilir.
- **Kurumsal SMTP Entegrasyonu:** E-postalar varsayılan Gmail altyapısı veya kurumsal SMTP Relay (Brevo, SendGrid vb.) üzerinden güvenle gönderilir.
- **Doğrudan AD Bağlantısı:** Şifre sıfırlama işlemi onaylandığında, Python `ldap3` kütüphanesi üzerinden LDAPS (Port 636) kullanılarak Active Directory sunucusunda şifre anında güncellenir.
- **Modern ve Şık Arayüz:** Kullanıcı dostu, karanlık mod (Dark Mode) destekli HTML/CSS tasarımı.

## 🛠️ Teknolojiler
- **Backend:** Python 3.x, Flask, ldap3
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Protokoller:** LDAP/LDAPS, SMTP
- **Veritabanı:** Doğrudan Microsoft Active Directory

## ⚙️ Kurulum ve Ayarlar

1. Projeyi bilgisayarınıza indirin:
   ```bash
   git clone https://github.com/KULLANICI_ADINIZ/proje-adi.git
   ```

2. Gerekli Python kütüphanelerini yükleyin:
   ```bash
   pip install flask ldap3
   ```

3. Konfigürasyon dosyasını ayarlayın:
   - `config.example.py` dosyasının adını `config.py` olarak değiştirin.
   - Kendi Active Directory IP adresinizi, Admin kullanıcı adı/şifrenizi ve SMTP (E-posta) bilgilerinizi dosyaya girin. *(Not: config.py dosyası .gitignore içindedir, GitHub'a yüklenmez).*

4. Uygulamayı başlatın:
   ```bash
   python app.py
   ```
   Uygulama `http://localhost:5000` adresinde çalışmaya başlayacaktır.

## 🔒 Güvenlik Uyarıları
- Bu projeyi canlı (Production) ortamda kullanırken mutlaka bir Reverse Proxy (Nginx, IIS) arkasında ve **HTTPS/SSL** sertifikası ile çalıştırın.
- `config.py` dosyanızı asla public (herkese açık) repolara yüklemeyin.

---
*Bu proje, sistem yönetimi ve siber güvenlik ağ altyapıları konseptlerini anlamak amacıyla laboratuvar ortamı için geliştirilmiştir.*
