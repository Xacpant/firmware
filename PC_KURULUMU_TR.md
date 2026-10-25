# PC'de Bruce derleme kütüphanelerini kurma

Bu yardımcı yalnızca bu Bruce projesinin derleme araçlarını ve kütüphanelerini hazırlar. Gereken Python sürümü 3.10 veya üzeridir.

1. ZIP dosyasını çıkartın.
2. T-Embed-Plus.code-workspace dosyasını Cursor'da açın.
3. Cursor terminalini firmware-tembed-plus klasöründe açın.
4. Windows'ta şu komutu çalıştırın:

```powershell
py -3 tools\setup_build.py --build
```

`py` komutu bulunamazsa ve Python PATH'e ekliyse:

```powershell
python tools\setup_build.py --build
```

Yardımcı, proje içinde `.build-tools/venv` Python ortamını oluşturur, PlatformIO 6.2.0'ı bu ortama kurar ve `lilygo-t-embed-cc1101-plus` bağımlılıklarını indirir. PlatformIO çekirdeği ve paketleri de proje içindeki `.build-tools/platformio` dizininde tutulur. `--build` sonunda aynı Plus hedefini derler.

Yalnızca kurulum için `--build` bölümünü kaldırın. İşlem listesini değişiklik yapmadan görmek için `--plan --build` kullanın.

## USB/HID bileşenleri

- USB klavye/fare ve HID sürücüleri mevcut `lib/Bad_Usb_Lib` klasöründedir.
- Kartın USB desteği ESP32/Arduino çekirdeğinin TinyUSB bileşenlerine bağlıdır; çekirdeğin indirilmesi gerekir.
- BLE klavye desteğinde mevcut yerel sürücü ve NimBLE-Arduino 2.5.1 kullanılır.
- Yeni bir otomatik PC program kurma yükü veya BadUSB betiği eklenmedi. Bu yardımcı, firmware projesinin derlenmesi içindir ve cihaza otomatik yazdırmaz.

## Bu oturumda doğrulananlar

Kurulum yardımcısının Python sözdizimi kontrolü ve değişiklik yapmayan `--plan --build` çalıştırması geçti. Proje içindeki 14 önceki test sonucu korunmaktadır. Windows bilgisayarına bu oturumdan erişilmedi; oraya kurulum yapılmadı.

Bulut ortamında PlatformIO 6.2.0 ve bağımsız ArduinoJson 7.4.3 kurulabildi. Tüm proje bağımlılıklarının kurulumu, Arduino ESP32 çekirdek arşivini indirirken `CERTIFICATE_VERIFY_FAILED` hatasında durdu. Son çıktı SETUP_ATTEMPT.txt içindedir. Tam firmware derlemesi ve gerçek USB/HID cihaz testi yapılmış sayılmaz.
