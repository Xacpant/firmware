# Xacpant 0.1.0-dev değişiklikleri

Bu sürüm Bruce kaynağının üzerinde geliştirilmiştir. Önceki ZIP'in merkezi dizini ve son dosyaları eksik olduğundan, 909 sağlam yerel ZIP kaydı CRC32 ile doğrulanarak kurtarıldı; eksik 193 normal dosya kullanıcının bilgisayarındaki özgün Bruce kaynağından tamamlandı. Kartta bulunmayan donanımların kaldırma listesi uygulanmaya devam eder.

## Bu turda düzeltilenler

- Yeniden gelen harici RFID include/factory ve menü başvuruları temizlendi; PN532 I2C korunuyor.
- Kartta bulunmayan pin alanlarına başvuran Config menüsü düzeltildi.
- RFID/IR/RF ayarlarında Back ile üst menüyü yeniden çağıran yollar düz döngüye çevrildi.
- Menüye IR Monitor ve Live Status bağlantıları yeniden eklendi.
- GPIO40 ses LRCLK olarak korunup TFT reset -1 yapıldı (üretici tanımı).
- USB host bağlı değilken sonsuz, iptal edilemeyen bekleme kaldırıldı; BACK ile çıkış ve sınırlı durum yenilemesi eklendi.
- HID komut tamponu sıfırlandı; ilk komuttan önce REPEAT kullanımı önceki komut belleğini okumuyor.
- HID gecikme ayarları her çalıştırmada güncel kullanıcı ayarından başlıyor.
- Uzun HID beklemelerinde ve buton beklemesinde ESC/Back işleniyor; çıkışta ve duraklatmada tuşlar bırakılıyor.
- Null HID örneği denetleniyor.
- Giriş görev tanıtıcısı yoksa vTaskSuspend(NULL) çağrılarak geçerli görevin yanlışlıkla askıya alınması önlendi.
- Görsel küçültülürken tarama çizgisi aliasing sorununu azaltan alan ortalaması eklendi.
- Açılış resmi için tam sayı taşmasına dayanıklı oranlı yerleşim ve sınırlı satır tamponu eklendi.
- Orijinal görselin SHA-256 özeti test ediliyor.
- Ürün adı, sürüm etiketi, varsayılan AP/BLE adı, MSC ürün etiketi ve derleme çıktı adı Xacpant olarak değiştirildi.
- Mevcut kayıt biçimleri ve Bruce iç sembolleri uyumluluk için korunuyor.
- Onboard Health ve Last Reset tanılama ekranları eklendi.

Bu çalışma RF çıkış gücünü artırmaz. Mevcut Wi-Fi/BLE/Sub-GHz uygulamalarının saldırı veya bozucu işlevleri bu turda genişletilmemiştir. Donma nedenlerinin tamamının giderildiği iddia edilmez; cihaz testi gereklidir.

## Derlemede bulunan kütüphane uyumluluk hatası

FastLED 3.10.8 tür adı FP ile kartın kısa yazı boyutu makrosu FP çakışıyordu. FP/FM/FG font sabitleri, kaynak dizgeleri ve yorumlar korunarak XACPANT_FONT_SMALL/MEDIUM/LARGE adlarına taşındı. Ekran boyut değerleri ve uygulamaların davranışı aynı kaldı.

Son derleme taramasında, GPS başlıkları kaldırılmışken dosya menüsündeki Wigle/WDGoWars CSV yükleme callback'lerinin etkin kaldığı bulundu. Bu dört GPS işlemi DISABLE_GPS korumasına alındı; genel CSV görüntüleme/kopyalama/dosya işlemleri korundu. İlgili regresyon kontrolü eklendi.
