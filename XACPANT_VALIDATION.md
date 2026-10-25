# Xacpant 0.1.0-dev doğrulama durumu

25 Ekim 2026. Kaynak kodu geliştirme paketidir; doğrulanmış kararlı firmware değildir.

- Son GPS menü düzeltmesinden sonra, etkin kaynak dallarında silinen donanım başlıkları ve Wigle/WDGoWars örnekleri bulunmadığını denetleyen hedef kontrol geçti.
- Önceki kapsamlı derleme-modu turu: 19 kontrol; 10 kaynak/kart kontrolü başarılı. 9 C++ test programı derlendi, çalıştırma bölümleri HOST_TEST_COMPILE_ONLY=1 ile açıkça atlandı.
- Windows'taki önceki çalışma zamanı denemelerinde 16 kontrol geçti; üç test programının çalıştırılması Windows Uygulama Denetimi (WinError 4551) tarafından engellendi. Windows'ta ASan/UBSan çalıştırılmadı.
- Tam ESP32 derlemesinde bulunan FastLED FP makro çakışması düzeltildi; sonraki derlemede FastLED aşaması geçti. GPS CSV yükleme callback başvuruları da düzeltildi ve ilgili önişlemci kontrolü geçti.
- Tam firmware derlemesi henüz tamamlanmadı. Hazır .bin, cihazda çalışma veya performans/menzil sonucu sunulmuyor.
- Gerçek cihazda RF/IR/NFC/USB, pil, ısı ve uzun süreli kararlılık testi yapılmadı. Flipper Zero ile kıyas testi yapılmadı.
- Xacpant'ın özgün logo dosyası SHA-256 kontrolünde korundu. Yeni ölçekleyici C++ nesnesi olarak derlendi; 6 Python yardımcı/test dosyasının sözdizimi doğrulandı.
- Tam GitHub kaynak yüklemesi otomatik onay denetimi tarafından reddedildi. Sadece mevcut README'den xacpant-tembed-plus dalı oluşturuldu; Xacpant kodu ve iş akışı yüklenmedi, uzak test çalışmadı.

Ayrıntılar: XACPANT_ANALIZ_TR.md, XACPANT_CHANGES_TR.md, review/XACPANT_PATCH.diff. Sahiplik bildirimi: COPYRIGHT.Xacpant. Bruce'un AGPL v3 ve üçüncü taraf bildirimleri korunmuştur.
