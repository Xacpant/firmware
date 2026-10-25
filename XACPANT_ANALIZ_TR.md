# Xacpant kaynak analizi

25 Ekim 2026. Hedef: LilyGO T-Embed CC1101 Plus, ESP32-S3, 16 MB flash, 8 MB PSRAM.

## Kapsam

Bruce kodunun üzerindeki uyarlamadır. Sıfırdan firmware yazılmadı. Normal uygulamalar topluca silinmedi. Kartta bulunmayan 13 donanım grubunun ilgili uygulama/sürücü/menü yolları kaldırıldı. Ayrıntı: REMOVED_HARDWARE_FILES.json. Diğer kart hedeflerinin tanımları da bu tek kart sürümünden çıkarılmıştır.

| Grup | Bu sürümdeki karşılık |
| --- | --- |
| CC1101 Sub-GHz | Korundu; PCB pinleri sabit |
| nRF24L01 | Korundu; CE43/CS44 |
| PN532 13.56 MHz | Korundu; I2C8/18 |
| IR TX/RX | Korundu; TX2/RX1; IR Monitor eklendi |
| Wi-Fi, BLE, USB/HID | Korundu; genel saldırı/spam kabiliyetleri genişletilmedi |
| SD, dosya, JavaScript | Korundu |
| Hoparlör, mikrofon, RGB LED | Korundu |
| LoRa SX1276/SX1262 | Kartta yok; çıkarıldı |
| SI4713 FM | Kartta yok; çıkarıldı |
| W5500 Ethernet | Kartta yok; çıkarıldı; ortak Wi-Fi esp-netif yardımcıları korundu |
| GPS UART | Kartta yok; çıkarıldı |
| 125 kHz RFID | PN532 desteklemez; çıkarıldı |
| ST25R3916, RC522, M5 RFID2 | Bu kartta yok; çıkarıldı |
| iButton | Bu kartta yok; çıkarıldı |
| AmiiboLink, Chameleon, PN532 BLE, PN532 UART/PN532Killer | Harici araçlar; çıkarıldı |

## Somut hata düzeltmeleri

1. Menü callback'i, çağrı sırasında ortak seçenek vektörü yenilense de yaşamaya devam edecek biçimde kopyalanıyor.
2. SPI/I2C/UART pin doğrulayıcıları değeri değil referansı güncelliyor; GPIO üst sınırı düzeltiliyor.
3. Kartta olmayan config alanları kaldırılıyor; menüler bu alanlara başvurmuyor.
4. I2C taramasında null bus kontrolü, ayrılmış adreslerin atlanması, iptal ve bus bırakma yolları korunuyor.
5. İlerleme çubuğu sıfır toplam, negatif ilerleme, aşırı değer ve dar ekran için sınırlandırılıyor.
6. RFID fabrikaları yalnızca yerleşik PN532 I2C oluşturuyor; başlatma hataları ve boş işaretçiler ele alınıyor.
7. RFID/IR/RF ayarlarının Back yolları üst menüyü yeniden çağırıp çağrı yığınını büyütmüyor.
8. USB host bulunmadığında BACK ile çıkılamayan bekleme iptal edilebilir hale getiriliyor.
9. HID komut tamponu başlatılıyor; REPEAT ilk satırda önceki bir komut varmış gibi davranmıyor.
10. HID gecikme durumu çalıştırmalar arasında taşınmıyor. Uzun bekleme ve buton beklemesi iptal edilebiliyor.
11. HID çıkışı/duraklatması tuşları bırakıyor; boş HID örneği denetleniyor.
12. Giriş görev tanıtıcısı yoksa vTaskSuspend(NULL) ile mevcut görevin yanlışlıkla askıya alınması önleniyor.
13. TFT reset -1 olarak üretici tanımına uyarlanıyor; GPIO40 hoparlör LRCLK olarak kalıyor.
14. Python derleme yardımcısı venv pio giriş yolunu PATH'e ekliyor ve Windows için yalnızca ilgili süreçte Git uzun yol desteğini açıyor.

## Yeni tanılama ve açılış

IR Monitor, Live Status, Onboard Health ve Last Reset ekranları eklendi. Logo kaynak PNG'si değiştirilmeden tutuluyor; SHA-256 özeti test ediliyor. Yerleşim boyuta ve dönüşe göre hesaplanıyor, kırpma yapılmıyor. Alan ortalaması, ince tarama çizgilerinin küçülürken parçalanmasını azaltıyor. Tam ekran sprite yerine 640 baytlık satır tamponu ve flash'taki RGB565 görsel kullanılıyor.

## Lisans ve doğrulama

Xacpant'a özgü eklemelerde Xacpant bildirimi bulunur. Bruce'un AGPL v3 ve üçüncü taraf bildirimleri korunmuştur. Özgün logonun mülkiyetinin devralındığı iddia edilmez.

Gerçek test durumu XACPANT_VALIDATION.md dosyasındadır. Host kontrolleri tüm ESP32 bileşenlerinin çalıştığını, donma nedenlerinin tamamının giderildiğini veya Flipper Zero'ya üstünlük sağlandığını kanıtlamaz. Cihaz testi yapılmadı.
