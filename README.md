# Xacpant — LilyGO T-Embed CC1101 Plus

Sürdürme ve Xacpant değişiklik bildirimleri: **Xacpant** — [COPYRIGHT.Xacpant](COPYRIGHT.Xacpant).

Bruce tabanlı, yalnızca LilyGO T-Embed CC1101 Plus için hazırlanmış geliştirme sürümü.

Bu proje **cihaz üzerinde henüz doğrulanmış bir kararlı sürüm değildir**. Derleme ve test durumu `XACPANT_VALIDATION.md` dosyasında açıklanır. Flipper Zero ile karşılaştırmalı performans ölçümü yapılmamıştır.

## Korunan donanım ve işlevler

CC1101 Sub-GHz, nRF24L01, PN532 I2C NFC, IR TX/RX, Wi-Fi, BLE, USB/HID, SD ve LittleFS, mikrofon, hoparlör, RGB LED, saat, dosya ve JavaScript araçları korunur. Bunların korunması, her protokolün ve uygulamanın kart üzerinde çalışmasının doğrulandığı anlamına gelmez.

Kartta bulunmayan 13 donanım grubu kaldırılmıştır: LoRa, SI4713 FM, W5500 Ethernet, GPS UART, 125 kHz RFID, ST25R3916, RC522, M5 RFID2, iButton, harici AmiiboLink, Chameleon, PN532 BLE ve PN532 UART/PN532Killer. Tam dosya listesi: `REMOVED_HARDWARE_FILES.json`.

## Xacpant değişiklikleri

- Açılış: kullanıcının özgün görseli, kırpılmadan ve oranı korunarak ekrana sığdırılır. Orijinal PNG `assets/xacpant-logo.png` içinde değiştirilmeden korunur.
- Xacpant açılış gösterimi 2 saniyedir ve tuşla atlanabilir. Mevcut Instant Boot ayarı korunur. SD/LittleFS/tema üzerinden özel JPG/GIF açılış medyası kullanılıyorsa Xacpant görselinden sonra gösterilir.
- Büyük ekran tamponu yerine flash'taki görsel ve 640 baytlık satır tamponu kullanılır.
- IR Monitor: alınan protokol/bit sayısı, tekrar ve taşma sayaçları.
- Live Status: anlık/minimum heap, en büyük ayrılabilir blok, PSRAM ve SD durumu.
- Onboard Health: PN532, BQ27220, BQ25896 adreslerinden I2C ACK kontrolü; PSRAM ve SD durumu.
- Last Reset: watchdog, panic, düşük voltaj, yazılım yeniden başlatma ve uyanma nedenleri.
- PCB üzerindeki sabit pinler korunur. GPIO43/44 nRF24 için ayrılmıştır; bu pinlerde UART seçimi engellenir.
- TFT reset pini, üreticinin tanımına göre -1 yapılır; ses LRCLK pin40 ekran reseti olarak kullanılmaz.
- HID: iptal edilebilir uzun beklemeler, çıkışta/duraklatmada tuş bırakma, null kontrolü ve çalıştırmalar arasında temiz durum.
- Menü callback ömrü, GPIO sınır kontrolü, I2C hataları ve ilerleme çubuğu sınırları düzeltilmiştir.

## Windows'ta derleme

Python 3.12 ve Git kurulu olmalıdır.

```powershell
py -3.12 tools\setup_build.py --build
```

Yardımcı, proje içinde bağımlılıkları kurar ve yalnızca `lilygo-t-embed-cc1101-plus` hedefini derler. Cihaza otomatik yüklemez.

## Testler

Linux/GitHub Actions üzerinde:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

Host C++ testleri varsayılan olarak g++ kullanır. Windows'ta `HOST_CXX_JSON` ortam değişkeni, derleyici ve sabit argümanlarını JSON dizisi olarak seçebilir. Windows host testlerinde AddressSanitizer/UndefinedBehaviorSanitizer kullanılmaz; Linux'ta kullanılır. `HOST_TEST_COMPILE_ONLY=1`, test programlarını yalnızca derler; çalıştırma kontrollerini açıkça atlanmış olarak raporlar. ArduinoJson bütünleştirme testi, ilgili başlık yoksa açıkça atlanır.

## Uyumluluk ve kaynak

Kullanıcıya görünen ürün adı Xacpant'tır. Bruce'un iç sınıf adları, eski kayıt dosyaları ve protokol tanımları uyumluluk için korunmuştur. Bu nedenle kaynakta Bruce adı bulunması beklenir.

Bruce ve katkıda bulunanların telif/lisans bildirimleri korunur: [LICENSE](LICENSE), [THIRD_PARTY.md](THIRD_PARTY.md). Özgün proje bilgileri [UPSTREAM_README.md](UPSTREAM_README.md) içindedir.

Donanım dayanağı: [LILYGO resmî depo](https://github.com/Xinyuan-LilyGO/T-Embed-CC1101), [Plus ürün sayfası](https://lilygo.cc/products/t-embed-cc1101-plus).

GitHub kaynak aktarımında yalnızca firmware için gerekmeyen büyük `media/` ve `pcbs/` arşivleri dışarıda tutulur. Yerel tam pakette bu dosyalar korunur.
