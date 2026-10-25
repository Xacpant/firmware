"""Hardware pruning, target guard and host C++ regression checks; no device required."""
import configparser
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CXX = json.loads(os.environ.get("HOST_CXX_JSON", '["g++"]'))
SANITIZERS = [] if os.name == "nt" else ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]


def function(source, signature):
    start = source.index(signature)
    brace = source.index('{', start)
    depth, pos = 1, brace + 1
    while depth:
        if source[pos] == '{': depth += 1
        elif source[pos] == '}': depth -= 1
        pos += 1
    return source[start:pos]


class TEmbedPlusTests(unittest.TestCase):
    def run_host_binary(self, executable):
        if os.environ.get("HOST_TEST_COMPILE_ONLY") == "1":
            self.skipTest("C++ compiled; runtime intentionally not executed in compile-only mode")
        subprocess.run([str(executable)], check=True, env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0"})

    def test_only_plus_environment(self):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(ROOT / 'platformio.ini')
        self.assertEqual(cfg['platformio']['default_envs'], 'lilygo-t-embed-cc1101-plus')
        cfg.read(ROOT / 'boards/lilygo-t-embed-cc1101/lilygo-t-embed-cc1101.ini')
        self.assertEqual([s for s in cfg.sections() if s.startswith('env:')], ['env:lilygo-t-embed-cc1101-plus'])
        self.assertNotIn('env_light', cfg)
        self.assertNotIn('env_4mb', cfg)
        self.assertEqual([x.name for x in (ROOT / 'boards/_boards_json').glob('*.json')], ['lilygo-t-embed-cc1101.json'])

    def test_absent_hardware_implementations_removed(self):
        removed = json.loads((ROOT / 'REMOVED_HARDWARE_FILES.json').read_text())
        self.assertGreater(len(removed), 100)
        for name in removed:
            self.assertFalse((ROOT / name).exists(), name)
        for name in ('gps', 'fm', 'lora'):
            self.assertFalse((ROOT / 'src/modules' / name).exists())
        for name in ('PN532.cpp', 'tag_o_matic.cpp'):
            self.assertTrue((ROOT / 'src/modules/rfid' / name).is_file())
        for name in ('NRF24', 'rf', 'ir'):
            self.assertTrue((ROOT / 'src/modules' / name).is_dir())
        self.assertTrue((ROOT / 'src/modules/ethernet/ARPScanner.cpp').is_file())
        self.assertNotIn('ETH.netif()', (ROOT / 'src/modules/ethernet/ARPScanner.cpp').read_text())

    def test_no_disabled_config_fields(self):
        source = (ROOT / 'src/core/configPins.h').read_text() + (ROOT / 'src/core/configPins.cpp').read_text()
        for name in ('LoRa_bus', 'W5500_bus', 'ST25R_bus', 'gps_bus', 'gpsBaudrate', 'setiButtonPin'):
            self.assertNotIn(name, source)

    def test_guard_rejects_alternate_targets(self):
        code = compile((ROOT / 'tools/tembed_plus_guard.py').read_text(), 'guard', 'exec')
        class Env:
            def __init__(self, target, board='lilygo-t-embed-cc1101', mcu='esp32s3', flash='16MB'):
                self.target, self.board, self.mcu, self.flash = target, board, mcu, flash
            def subst(self, value): return self.target
            def GetProjectOption(self, value): return self.board
            def BoardConfig(self): return {'build.mcu': self.mcu, 'upload.flash_size': self.flash}
        def run(env): exec(code, {'env': env, 'Import': lambda *args: None})
        run(Env('lilygo-t-embed-cc1101-plus'))
        for env in (Env('m5stack-cardputer'), Env('lilygo-t-embed-cc1101'), Env('lilygo-t-embed-cc1101-plus', board='other'), Env('lilygo-t-embed-cc1101-plus', mcu='esp32'), Env('lilygo-t-embed-cc1101-plus', flash='4MB')):
            with self.assertRaises(RuntimeError): run(env)

    def test_pin_header_compiles_only_for_plus_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'soc').mkdir()
            (base / 'soc/soc_caps.h').write_text('// External ESP-IDF header stub, for pin constants only.\n')
            src = base / 'pins.cpp'
            src.write_text('#include "' + (ROOT / 'boards/pinouts/pins_arduino.h').as_posix() + '"\nstatic_assert(SCK == 11 && MISO == 10 && MOSI == 9);\nstatic_assert(TFT_RST == -1 && WCLK == 40);\nstatic_assert(NRF24_CE_PIN == 43 && NRF24_SS_PIN == 44);\nstatic_assert(CC1101_SS_PIN == 12 && PN532_IRQ == 17);\n')
            cmd = [*CXX, '-std=c++17', '-c', '-o', str(base / 'pins.o'), '-I' + temp, '-DT_EMBED_1101', str(src)]
            rejected = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('supports only', rejected.stderr)
            accepted = subprocess.run(cmd + ['-DBRUCE_TEMBED_PLUS'], capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

    def test_production_pin_validators_and_menu_callback(self):
        src = (ROOT / 'src/core/configPins.cpp').read_text()
        methods = '\n'.join(function(src, 'void BruceConfigPins::' + name) for name in ('validateSpiPins(', 'validateI2CPins(', 'validateUARTPins('))
        display = (ROOT / 'src/core/display.cpp').read_text()
        dispatch = re.search(r'auto operation = options\[chosen\]\.operation;\s*if \(operation\) operation\(\);', display)
        self.assertIsNotNone(dispatch)
        test = r'''
#include <cassert>
#include <functional>
#include <memory>
#include <vector>
constexpr int GPIO_PIN_COUNT = 49;
constexpr int GPIO_NUM_NC = -1;
class BruceConfigPins {
public:
    struct SPIPins { int sck, miso, mosi, cs, io0, io2; };
    struct I2CPins { int sda, scl; };
    struct UARTPins { int rx, tx; };
    void validateSpiPins(SPIPins &value);
    void validateI2CPins(I2CPins &value);
    void validateUARTPins(UARTPins &value);
};
''' + methods + r'''
struct Option { std::function<void()> operation; };
int main() {
    BruceConfigPins config;
    BruceConfigPins::SPIPins spi{49, -20, 48, 12, 99, 0};
    config.validateSpiPins(spi);
    assert(spi.sck == -1 && spi.miso == -1 && spi.mosi == 48);
    assert(spi.cs == 12 && spi.io0 == -1 && spi.io2 == 0);
    BruceConfigPins::I2CPins i2c{49, 18}; config.validateI2CPins(i2c);
    assert(i2c.sda == -1 && i2c.scl == 18);
    BruceConfigPins::UARTPins uart{-8, 48}; config.validateUARTPins(uart);
    assert(uart.rx == -1 && uart.tx == 48);
    for (int i = 0; i < 10000; ++i) {
        std::vector<Option> options;
        auto state = std::make_shared<int>(42);
        std::weak_ptr<int> lifetime = state;
        options.push_back({[state, &options, &lifetime]() {
            options.clear(); options.shrink_to_fit();
            assert(!lifetime.expired());
            assert(*state == 42);
        }});
        state.reset();
        const int chosen = 0;
        { ''' + dispatch[0] + r''' }
        assert(lifetime.expired());
    }
}
'''
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'test.cpp').write_text(test)
            subprocess.run([*CXX, '-std=c++17', '-g', *SANITIZERS, str(base / 'test.cpp'), '-o', str(base / ('regression.exe' if os.name == 'nt' else 'regression'))], check=True, capture_output=True)
            # This container cannot expose /proc to LeakSanitizer. ASan/UBSan stay enabled.
            self.run_host_binary(base / ('regression.exe' if os.name == 'nt' else 'regression'))

    def test_deleted_headers_are_not_in_active_source_branches(self):
        board_ini = (ROOT / 'boards/lilygo-t-embed-cc1101/lilygo-t-embed-cc1101.ini').read_text()
        definitions = re.findall(r'-D([A-Za-z_][A-Za-z_0-9]*)', board_ini)
        definitions += ['T_EMBED_1101', 'BOARD_HAS_PSRAM']
        deleted_headers = {Path(x).name for x in json.loads((ROOT / 'REMOVED_HARDWARE_FILES.json').read_text()) if x.endswith(('.h', '.hpp')) and x.startswith('src/')}
        sources = ['src/core/main_menu.h', 'src/core/main_menu.cpp', 'src/core/sd_functions.cpp', 'src/core/menu_items/RFIDMenu.cpp', 'src/core/menu_items/OthersMenu.cpp', 'src/core/menu_items/ConfigMenu.cpp', 'src/modules/rfid/tag_o_matic.cpp', 'src/core/serial_commands/rfid_commands.cpp', 'src/core/configPins.h', 'src/core/configPins.cpp', 'src/core/settings.cpp']
        for filename in sources:
            # Keep include names as tokens so the real C++ preprocessor selects branches,
            # without pretending these external ESP32 dependencies have been compiled.
            source = re.sub(r'^\s*#include\s*([<"].*[>"])', r'SOURCE_INCLUDE \1', (ROOT / filename).read_text(), flags=re.M)
            command = [*CXX, '-E', '-P', '-x', 'c++'] + ['-D' + d for d in definitions] + ['-']
            result = subprocess.run(command, input=source, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, filename + ': ' + result.stderr)
            self.assertNotRegex(result.stdout, r"\b(?:Wigle|WDGoWars)\s+\w+", filename)
            for header in re.findall(r'SOURCE_INCLUDE [<"]([^>"\n]+)', result.stdout):
                self.assertNotIn(Path(header).name, deleted_headers, filename + ': ' + header)

    def compile_and_run_host(self, source):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'test.cpp').write_text(source)
            subprocess.run([*CXX, '-std=c++17', *SANITIZERS, str(base / 'test.cpp'), '-o', str(base / ('check.exe' if os.name == 'nt' else 'check'))], check=True, capture_output=True)
            self.run_host_binary(base / ('check.exe' if os.name == 'nt' else 'check'))

    def test_progress_zero_negative_oversized_and_large_totals(self):
        body = function((ROOT / 'src/core/display.cpp').read_text(), 'void progressHandler(')
        self.compile_and_run_host(r"""
#include <cassert>
#include <cstdint>
#include <cstddef>
#include <limits>
#include <string>
using String = std::string;
int tftWidth = 320, tftHeight = 170;
struct Config {int bgColor=0, priColor=1;} bruceConfig;
constexpr int TFT_WHITE=1;
int fills=0, lastWidth=-1;
struct Display {
 void fillRect(int x,int y,int width,int height,int color) {
  ++fills; assert(width>=0); assert(width<=tftWidth);
  if(x==20) lastWidth=width;
 }
 void drawRect(int,int,int,int,int) {}
} tft;
void displayRedStripe(const String&,int,int) {}
""" + body + r"""
int main() {
 progressHandler(0,0,""); assert(fills==0);
 progressHandler(-5,100,""); assert(lastWidth==0);
 progressHandler(50,100,""); assert(lastWidth==140);
 progressHandler(1000,100,""); assert(lastWidth==280);
 progressHandler(2147483647,std::numeric_limits<size_t>::max(),""); assert(lastWidth==0);
 tftWidth=20; int previous=fills;
 progressHandler(10,10,""); assert(fills==previous);
}
""")

    def test_i2c_null_bus_cancellation_reserved_addresses_and_release(self):
        src = (ROOT / 'src/core/i2c_finder.cpp').read_text()
        bodies = '\n'.join(function(src, name) for name in ('void find_i2c_addresses()', 'uint8_t find_first_i2c_address()', 'bool check_i2c_address('))
        constants = '\n'.join(re.findall(r'^#define (?:FIRST|LAST)_I2C_ADDRESS .*', src, re.M))
        self.compile_and_run_host(r"""
#include <cassert>
#include <cstdint>
#include <vector>
std::vector<int> probes;
int releases=0, errors=0, cancelAfter=-1;
bool available=true, returnToMenu=false;
constexpr int EscPress=1, SelPress=2;
struct TwoWire {
 int address=0;
 void beginTransmission(uint8_t a) { address=a; probes.push_back(a); }
 int endTransmission() {return address==0x24 || address==0x55 ? 0 : 2;}
} wire;
TwoWire* acquireI2CBus() {return available ? &wire : nullptr;}
void releaseI2CBus() {++releases;}
void drawMainBorderWithTitle(const char*) {}
void padprintln(const char*) {}
void padprint(const char*) {}
void displayError(const char*,bool) {++errors;}
void delay(int) {}
void vTaskDelay(int) {}
int pdMS_TO_TICKS(int ms) {return ms;}
bool check(int key) {
 if(key==EscPress) return cancelAfter>=0 && static_cast<int>(probes.size())>=cancelAfter;
 return probes.size()==112;
}
struct Display {void print(const char*) {} void printf(const char*,int) {}} tft;
void reset() {probes.clear(); releases=0; errors=0; cancelAfter=-1; returnToMenu=false;}
""" + constants + '\n' + bodies + r"""
int main() {
 available=false;
 find_i2c_addresses(); assert(errors==1 && releases==0);
 assert(find_first_i2c_address()==0 && !check_i2c_address(0x24));
 available=true; reset();
 assert(!check_i2c_address(0x00) && !check_i2c_address(0x78));
 assert(probes.empty() && releases==0);
 assert(check_i2c_address(0x24) && releases==1);
 reset(); assert(find_first_i2c_address()==0x24 && releases==1);
 assert(probes.front()==0x08 && probes.back()==0x24);
 reset(); cancelAfter=3; find_i2c_addresses();
 assert(probes.size()==3 && releases==1 && returnToMenu);
 reset(); find_i2c_addresses();
 assert(probes.size()==112 && probes.front()==0x08 && probes.back()==0x77);
 assert(releases==1 && returnToMenu);
}
""")

    def test_system_i2c_config_roundtrip_with_real_arduinojson(self):
        include = Path(os.environ.get('ARDUINOJSON_INCLUDE', ROOT / '.pio/libdeps/lilygo-t-embed-cc1101-plus/ArduinoJson/src'))
        if not (include / 'ArduinoJson.h').is_file():
            self.skipTest('Install project dependencies, or set ARDUINOJSON_INCLUDE for this integration test')
        header = (ROOT / 'src/core/configPins.h').read_text()
        pins_struct = function(header, 'struct I2CPins') + ';'
        production = (ROOT / 'src/core/configPins.cpp').read_text()
        statements = re.search(r'    JsonObject _si2c = root\["sys_i2c"\].*?;\n    sys_i2c.toJson\(_si2c\);', production)
        self.assertIsNotNone(statements)
        source = '#include <ArduinoJson.h>\n#include <cassert>\nusing gpio_num_t = int;\nconstexpr int GPIO_NUM_NC = -1;\n' + pins_struct + '\nint main() {\nJsonDocument doc; JsonObject root = doc.to<JsonObject>();\nI2CPins sys_i2c(8,18);\n' + statements[0] + '\nassert(doc["sys_i2c"]["sda"].as<int>()==8);\nassert(doc["sys_i2c"]["scl"].as<int>()==18);\n}\n'
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp); (base/'check.cpp').write_text(source)
            subprocess.run([*CXX,'-std=c++17','-I'+str(include),str(base/'check.cpp'),'-o',str(base/('check.exe' if os.name == 'nt' else 'check'))],check=True,capture_output=True)
            self.run_host_binary(base / ('check.exe' if os.name == 'nt' else 'check'))

    def test_ir_monitor_counters_saturate_reset_and_wrap(self):
        state=(ROOT/'src/modules/diagnostics/monitor_state.h').read_text()
        self.compile_and_run_host(state + r"""
#include <cassert>
int main() {
 IRMonitorState s;
 s.record(false,false,0xfffffff0U);
 assert(s.frames==1 && s.repeats==0 && s.hasFrame);
 assert(s.ageMs(0x10U)==32);
 s.record(true,true,30);
 assert(s.frames==2 && s.repeats==1 && s.overflows==1);
 s.frames=UINT32_MAX-1; s.repeats=UINT32_MAX; s.overflows=UINT32_MAX;
 s.record(true,true,40); s.record(true,true,50);
 assert(s.frames==UINT32_MAX && s.repeats==UINT32_MAX && s.overflows==UINT32_MAX);
 s.reset(); assert(s.frames==0 && s.repeats==0 && s.overflows==0 && !s.hasFrame);
}
""")

    def feature_host_stubs(self):
        return r"""
#include <cassert>
#include <cstdint>
#include <cstdarg>
#include <cstdio>
#include <string>
#include <vector>
using String=std::string;
constexpr int XACPANT_FONT_SMALL=1, EscPress=1, SelPress=2;
constexpr int SAFE_STACK_BUFFER_SIZE=4096;
struct Config {int priColor=1,bgColor=0;} bruceConfig;
struct Pins {int irRx=1;} bruceConfigPins;
uint32_t nowMs=0;
int loops=0, stopAt=60, selectedAt=-1, selectedAgainAt=-1;
int draws=0,errors=0;
bool returnToMenu=false,sdcardMounted=false;
std::vector<String> messages;
uint32_t millis() {return nowMs;}
int pdMS_TO_TICKS(int n) {return n;}
void vTaskDelay(int n) {nowMs+=n; ++loops;}
bool check(int key) {
 if(key==EscPress) return loops>=stopAt;
 return loops==selectedAt || loops==selectedAgainAt;
}
void displayError(const char*,bool) {++errors;}
void drawMainBorderWithTitle(const char* text) {++draws; messages.emplace_back(text);}
void padprintln(const String& s) {messages.push_back(s);}
void padprintf(const char* format,...) {
 char buffer[128]; va_list ap; va_start(ap,format);
 vsnprintf(buffer,sizeof(buffer),format,ap); va_end(ap);
 messages.emplace_back(buffer);
}
struct Display {void setCursor(int,int){} void setTextSize(int){} void setTextColor(int,int){}} tft;
void resetTest() {nowMs=0;loops=0;draws=0;errors=0;selectedAt=-1;selectedAgainAt=-1;returnToMenu=false;messages.clear();}
"""

    def test_ir_monitor_cancellation_and_receiver_cleanup(self):
        src=function((ROOT/'src/modules/ir/ir_monitor.cpp').read_text(),'void irReceiverMonitor()')
        state=(ROOT/'src/modules/diagnostics/monitor_state.h').read_text()
        self.compile_and_run_host(self.feature_host_stubs()+state+r"""
int enables=0,disables=0,resumes=0;
struct decode_results {bool repeat=false,overflow=false;int decode_type=0;uint16_t bits=0;};
struct IRrecv {
 IRrecv(int,int,int) {}
 void enableIRIn(){++enables;}
 void disableIRIn(){++disables;}
 void resume(){++resumes;}
 bool decode(decode_results* r) {
  if(loops!=0 && loops!=5) return false;
  r->repeat=loops==5;r->overflow=loops==5;r->decode_type=1;r->bits=32;return true;
 }
};
String typeToString(int,bool){return "NEC";}
"""+src+r"""
int main() {
 irReceiverMonitor();
 assert(enables==1 && disables==1 && resumes==2 && loops==60);
 assert(draws==3);
 bool sawTwo=false;
 for(const auto& s:messages) if(s.find("Frames: 2  Repeats: 1")!=String::npos) sawTwo=true;
 assert(sawTwo);
 resetTest(); selectedAt=10; stopAt=20; irReceiverMonitor();
 assert(enables==2 && disables==2 && resumes==4);
 bool cleared=false;
 for(const auto& s:messages) if(s.find("Frames: 0  Repeats: 0")!=String::npos) cleared=true;
 assert(cleared);
 resetTest(); bruceConfigPins.irRx=-1; irReceiverMonitor();
 assert(errors==1 && enables==2 && disables==2);
}
""")

    def test_live_status_refresh_pause_and_missing_psram(self):
        src=function((ROOT/'src/modules/diagnostics/live_status.cpp').read_text(),'void showLiveSystemStatus()')
        self.compile_and_run_host(self.feature_host_stubs()+r"""
bool hasPsram=true;
int heapReads=0,psramReads=0;
bool psramFound(){return hasPsram;}
struct Esp {
 uint32_t getFreeHeap(){++heapReads;return 100*1024;}
 uint32_t getMaxAllocHeap(){return 80*1024;}
 uint32_t getMinFreeHeap(){return 70*1024;}
 uint32_t getFreePsram(){++psramReads;return 6*1024*1024;}
 uint32_t getPsramSize(){return 8*1024*1024;}
} ESP;
"""+src+r"""
int main() {
 stopAt=70; selectedAt=1; selectedAgainAt=10; showLiveSystemStatus();
 assert(draws==4 && heapReads==4 && psramReads==4);
 bool sawPause=false;
 for(const auto& s:messages) if(s.find("PAUSED")!=String::npos)sawPause=true;
 assert(sawPause);
 resetTest(); hasPsram=false; stopAt=2; showLiveSystemStatus();
 assert(draws==1 && heapReads==5 && psramReads==4);
 bool sawMissing=false;
 for(const auto& s:messages) if(s=="PSRAM: not detected")sawMissing=true;
 assert(sawMissing);
}
""")

    def test_rfid_navigation_does_not_recurse_into_parent(self):
        src = (ROOT / 'src/core/menu_items/RFIDMenu.cpp').read_text()
        config = function(src, 'void RFIDMenu::configMenu()')
        self.assertNotIn('optionsMenu()', config)
        self.assertIn('while (!returnToMenu)', config)
        for filename, signature in (('src/modules/rfid/tag_o_matic.cpp', 'void TagOMatic::set_rfid_module()'), ('src/core/serial_commands/rfid_commands.cpp', 'static RFIDInterface *_createRfidModule()')):
            body = function((ROOT / filename).read_text(), signature)
            self.assertIn('PN532::CONNECTION_TYPE::I2C', body)
            self.assertNotIn('switch', body)


if __name__ == '__main__':
    unittest.main(verbosity=2)
