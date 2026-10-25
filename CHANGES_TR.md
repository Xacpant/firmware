# Bruce — LilyGO T-Embed CC1101 Plus özelleştirmesi

Bu proje sıfırdan yazılmadı. Kullanıcının mevcut Bruce kaynak kodu ve önceki değişiklikleri üzerinden düzenlendi. Bruce AGPL lisansı ve kaynak dosyaların yazar bilgileri korunuyor.

## Donanım karşılaştırması

| Korunan yerleşik donanım | Destek |
|---|---|
| ESP32-S3, 16 MB Flash, 8 MB PSRAM | Wi-Fi, BLE, USB, temel sistem |
| CC1101 | Mevcut Sub-GHz işlevleri |
| nRF24L01 (Plus) | Mevcut nRF24 işlevleri |
| PN532 I2C | Mevcut NFC işlevleri |
| IR TX/RX | Kızılötesi |
| ST7789 320×170, encoder, WS2812 | Ekran ve arayüz |
| Mikrofon, hoparlör, microSD | Ses ve depolama |
| BQ25896 ve BQ27220 | Güç/batarya yönetimi |

Kartta bulunmayan SX1276/SX1262 LoRa, SI4713 FM, W5500 Ethernet, GPS UART, 125 kHz RFID, ST25R3916, RC522, M5 RFID2, iButton, AmiiboLink, Chameleon, harici PN532 BLE ve PN532 UART/Killer sürücülerinin uygulama ve başlık dosyaları çıkarıldı. Diğer kartların tanımları kaldırıldı. Tam dosya listesi REMOVED_HARDWARE_FILES.json içindedir.

Ethernet dizininde Wi-Fi'nin de kullandığı esp-netif ağ yardımcıları korunur; W5500 donanım sürücüsü ve ETH başlatma girişi çıkarıldı. RadioLib'in korunması LoRa donanımının etkin olduğu anlamına gelmez; kaynakta mevcut diğer radyo bağımlılıkları için tutulur.

## Yapılan düzeltmeler

- Yalnızca `lilygo-t-embed-cc1101-plus` hedefi var. Farklı hedef, kart, MCU veya Flash düzeni derleme öncesinde reddedilir.
- Yerleşik PN532 fabrika kodu yalnızca I2C okuyucuyu oluşturur. Eski ayarlar CC1101 ve PN532 I2C için doğrulanır.
- GPS/LoRa/W5500/ST25/iButton ayar alanları ve JSON kayıtları çıkarıldı; gereksiz alanlar RAM ve ayar dosyasında tutulmaz.
- RF modül/pin seçicisi ve nRF24 pinleriyle çakışan UART yönlendirmesi bu kartta kaldırıldı.
- SPI SCK/MISO sabitleri düzeltildi. Kartın yerleşik SPI/I2C/IR pin ayarları korunur.
- Pin doğrulayıcıları kopya yerine gerçek ayarları referansla düzeltir. GPIO_PIN_COUNT sınırı artık geçerli pin sayılmaz.
- RFID Config → Back geçişinde üst menüyü tekrar çağıran özyineleme kaldırıldı; döngüyle geri dönülür.
- Önceki menü işlem kopyalama, sıfır toplam boyut kontrolü ve RFID başlatma kontrolleri korundu.
- Cursor derleme görevi doğrudan yalnızca Plus hedefini derler. Diğer kartlara ait CI derleme matrisleri çıkarıldı.

Bu hedef/pin kısıtı donanım kimliği doğrulaması değildir: aynı ESP32-S3 kullanan başka bir karta zorla yazdırmayı fiziksel olarak engellediği iddia edilmez. Diğer kartlar desteklenmez.

## Doğrulama

14 otomatik test geçti. Pin sabitleri C++ derleyicisiyle kontrol edildi; farklı profil derleme sırasında reddedildi. Üretim kaynaklarından alınan pin doğrulayıcıları ve menü işlem kodu, 10.000 menü listesi değiştirme döngüsüyle ASan/UBSan altında test edildi. Ortamın /proc kısıtı nedeniyle LeakSanitizer devre dışıdır; bellek sızıntısı testi yapılmış sayılmaz.

PlatformIO proje yapılandırmasını doğru okudu. Tam ESP32 derlemesi Arduino bağımlılığı indirilirken `CERTIFICATE_VERIFY_FAILED` hatasında durdu. Firmware derlendi, cihazda çalıştı veya tüm donmalar düzeldi diye bir iddia yok. Donanım testi ve hız/RAM ölçümü yapılmadı.

## Cursor ve derleme

ZIP'i çıkartıp `T-Embed-Plus.code-workspace` dosyasını açın. Kaynak klasörde:

```sh
pio run -e lilygo-t-embed-cc1101-plus
python3 tests/test_tembed_plus.py
```

C++ testleri için g++ gerekir. Yalnızca testler bilgisayar üzerinde çalışır; cihaz testi yerine geçmez. Başarılı firmware derlemesinden sonra ekran/encoder, PN532, microSD, IR, ses, radyo menüleri ve güç işlevlerini gerçek cihazda denetlemek gerekir.

## Resmî kaynaklar

- LilyGO Plus ürün sayfası: https://lilygo.cc/en-us/products/t-embed-cc1101-plus
- LilyGO donanım/kod belgeleri: https://github.com/Xinyuan-LilyGO/T-Embed-CC1101
- Bruce uyumluluk tablosu: https://bruce.computer/

Bu oturum bulut ortamında çalıştı; Windows bilgisayarındaki açık Cursor projesine doğrudan yazılmadı. Düzenlenmiş kaynak bu pakettedir.

## 25 Ekim 2026 — performans ve bakım güncellemesi

Mevcut Bruce kodu üzerinde yapılan ek değişiklikler:

- Ana menü ve uygulama gizleme ekranında disabledMenus listesinin gereksiz kopyaları kaldırıldı; menü seçenekleri ve başlangıç uygulama listesi için kapasite önceden ayrılıyor.
- I2C Finder bağlantı oluşturulamadığında null işaretçi kullanmıyor. Tarama sırasında ESC ile iptal edilebiliyor; iptal ve normal bitişte I2C bırakılıyor. Tarama 0x08–0x77 aralığında yapılıyor, adımlar arasında görev zamanlayıcısına fırsat veriliyor.
- İlerleme çubuğu negatif ilerlemeyi 0'a, toplamdan büyük ilerlemeyi sona sınırlar. Sıfır toplam ve küçük ekran için erken dönüş var. Hesap 64 bit ara değer kullanır.
- Uzak menü seçimi artık çalıştırılan seçeneğin gerçek indeksini döndürür; 16 bit seçiciye daraltma kaldırıldı.
- sys_i2c ayar nesnesi kayıt sırasında oluşturuluyor; pinler JSON'a gerçekten yazılıyor. Bu işlem ArduinoJson 7.4.3 ile C++ üzerinde doğrulandı.

### Kütüphaneler

| Bağımlılık | Önceki tanım | Yeni tanım | Durum |
|---|---|---|---|
| NimBLE-Arduino | @2.5 | @2.5.1 | Resmî düzeltme sürümüne sabitlendi; cihaz entegrasyonu doğrulanmadı |
| ArduinoJson | Sürüm belirtilmemiş | @7.4.3 | Resmî düzeltme sürümüne sabitlendi; gerçek kütüphaneyle JSON testi geçti |
| Arduino-ESP32 / pioarduino | Bruce'un mevcut 3.3.9 platformu + özel exFAT kitaplık paketi | Korundu | Yeni 3.3.12 sürümü var; özel paketle uyumluluk doğrulanmadan çekirdek taşınmadı |
| Diğer kitaplıklar/forklar | Mevcut Bruce tanımları | Korundu | Hepsinin en son sürüme yükseltildiği iddia edilmez |

NimBLE 2.5.1 notları yeniden başlatma döngüsü çökmeleri ve bellek ömrü düzeltmeleri içeriyor:
https://github.com/h2zero/NimBLE-Arduino/releases/tag/2.5.1

ArduinoJson 7.4.3 sürüm notları sayısal dönüştürmede tampon taşması düzeltmesi içeriyor:
https://github.com/bblanchon/ArduinoJson/releases

ESP32 çekirdek sürümleri:
https://github.com/espressif/arduino-esp32/releases

### Test kapsamı ve sınırlar

11 testin tamamı geçti: hedef kısıtı, dosya temizliği, C++ pin sabitleri, pin doğrulaması, 10.000 menü işlem döngüsü, I2C null/iptal/adres aralığı/bus bırakma yolları, ilerleme sınırları ve gerçek ArduinoJson ile kayıt testi. ASan/UBSan kullanılan testler bilgisayar üzerinde çalışır. LeakSanitizer ortam kısıtı nedeniyle kapalıdır.

PlatformIO güncel bağımlılık tanımlarını doğru çözdü. ESP32 derleme denemesi Arduino çekirdek arşivinin TLS sertifikası doğrulanamadığı için yine derleme aşamasına ulaşamadı. Son kayıt BUILD_ATTEMPT.txt içindedir. Cihazda ölçülmüş hız, RAM, pil veya menzil sonucu yoktur; radyo çıkış gücü ayarları değiştirilmedi. Bütün kodun veya bütün kütüphanelerin en güncel/hatasız olduğu iddia edilmez.

JSON entegrasyon testini bağımsız çalıştırmak için ArduinoJson kaynak dizini ARDUINOJSON_INCLUDE ortam değişkeniyle verilebilir. Normalde proje bağımlılıkları kuruluysa .pio/libdeps içinden bulunur; yoksa bu tek test açıkça atlanır.

## Yeni yerleşik donanım özellikleri

### IR → IR Monitor

Mevcut IRremoteESP8266 kütüphanesini kullanan, yalnızca alım yapan bir canlı kumanda test ekranı eklendi. Son çözülen protokolü ve bit sayısını, çerçeve/tekrar sayaçlarını, alınan taşma bayraklarını ve son çerçevenin yaşını gösterir. SEL sayaçları temizler, BACK çıkar. Çıkışta alıcı kesmesi kapatılır; alınan ham tampon işaretçileri saklanmaz. Ekran en fazla saniyede dört kez yenilenir.

### Config → Live Status

Boş heap, en büyük ayrılabilir heap bloğu, şimdiye kadarki en düşük boş heap, boş/toplam PSRAM, çalışma süresi ve SD'nin mevcut bağlılık durumunu gösteren canlı ekran eklendi. SEL duraklatır/sürdürür; BACK çıkar. Ekran saniyede bir yenilenir. SD kartı kendiliğinden bağlamaz, dosya yazmaz; radyo iletimi başlatmaz.

### IR ve RF kütüphaneleri

IRremoteESP8266'nın tam protokol profili `-D_IR_ENABLE_DEFAULT_=true` ile açıkça seçildi. Kütüphanenin normal varsayılanı zaten tam profildir; bu değişiklik yeni protokoller eklenmiş gibi sunulmaz. Kaynak:
https://github.com/crankyoldgit/IRremoteESP8266/blob/master/src/IRremoteESP8266.h

Mevcut Bruce forkundaki IRremoteESP8266, SmartRC-CC1101, RF24 ve RadioLib bağımlılıkları korunur. Aynı işi yapan birden fazla IR kütüphanesi veya kartta olmayan donanım sürücüleri eklenmedi. Bu yeni özellikler için başka bir üçüncü taraf kütüphane gerekmedi. Derlenmiş protokol desteği her marka/modelin otomatik tanınacağı veya kontrol edileceği anlamına gelmez.

### Yeni test kapsamı

14 bilgisayar testi geçti. Önceki kontrollere ek olarak IR sayaçlarının doyması/sıfırlanması ve zaman sayacının taşması, IR monitörünün test alıcısıyla çerçeve alması ve çıkışta alıcıyı kapatması, sayaç temizleme/eksik pin yolları, canlı durum ekranının yenileme sınırı/duraklama/PSRAM yokluğu test edildi. Yeni ekranların donanım bağımlılıkları bu testlerde taklit edilir; gerçek IRremoteESP8266/ESP32 entegrasyonu derlenmiş sayılmaz. Önceki ArduinoJson entegrasyon testi gerçek kütüphaneyi kullanır.

Tam ESP32 derlemesini engelleyen çekirdek indirme sertifika sorunu sürüyor. Yeni ekranlar gerçek cihazda test edilmedi. Bu pakette yine yalnızca Bruce'un T-Embed CC1101 Plus hedefi vardır; Windows'taki asıl Cursor klasörü değişmedi.

## PC derleme kurulumu yardımcısı

`tools/setup_build.py` eklendi. Python 3.10+ ile proje içinde ayrı bir ortam oluşturup PlatformIO 6.2.0 ve Plus proje bağımlılıklarını kurar. `--build` isteğe bağlı olarak yalnızca Plus firmware'ini derler; cihaza yazdırma yapmaz. Windows komutu ve mevcut USB/HID bileşenleri PC_KURULUMU_TR.md içinde açıklanır. Sözdizimi ve değişiklik yapmayan kurulum planı kontrol edildi. Tam bağımlılık kurulumu buradaki ESP32 çekirdek indirmesinde TLS hatasına takıldı; kullanıcı bilgisayarına kurulum yapılmadı.
