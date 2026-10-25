"""Xacpant-specific geometry, image identity and cancellation regressions."""
import hashlib
import re
import unittest
from pathlib import Path
import test_tembed_plus as base
ROOT = base.ROOT
function = base.function

class XacpantTests(unittest.TestCase):
    def run_host_binary(self, executable):
        base.TEmbedPlusTests.run_host_binary(self, executable)

    def compile_and_run_host(self, source):
        base.TEmbedPlusTests.compile_and_run_host(self, source)

    def test_original_logo_is_preserved(self):
        source = ROOT / "assets/xacpant-logo.png"
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         "f652f7ad01cb57b3583069739ecdf5991afb2f11582169169e87a5f504149c95")
        header = (ROOT / "src/assets/xacpant_logo_rgb565.h").read_text()
        self.assertIn("XACPANT_LOGO_WIDTH = 275", header)
        self.assertIn("XACPANT_LOGO_HEIGHT = 279", header)
        self.assertEqual(len(re.findall(r"0x[0-9a-f]{4}", header)), 275 * 279)

    def test_fit_geometry_rotations_and_extreme_sizes(self):
        header = (ROOT / "src/core/splash_fit.h").read_text()
        self.compile_and_run_host(header + r"""
#include <cassert>
#include <climits>
int main() {
    auto fit = xacpant::fitImage(275,279,320,148);
    assert(fit.width==145 && fit.height==148 && fit.x==87 && fit.y==0);
    fit = xacpant::fitImage(275,279,170,298);
    assert(fit.width==170 && fit.height==172 && fit.y==63);
    for (int w : {1,17,170,320,INT_MAX}) for (int h : {1,22,170,320,INT_MAX}) {
        for (int sw : {1,275,INT_MAX}) for (int sh : {1,279,INT_MAX}) {
            auto r=xacpant::fitImage(sw,sh,w,h);
            assert(r.width>0 && r.height>0 && r.width<=w && r.height<=h);
            assert(r.x>=0 && r.y>=0 && r.x+r.width<=w && r.y+r.height<=h);
        }
    }
    assert(xacpant::fitImage(0,279,320,170).width==0);
    assert(xacpant::fitImage(275,279,-1,170).height==0);
}
""".replace("#include <climits>", "#include <climits>\n#include <initializer_list>"))

    def test_long_hid_wait_cancellation_and_timer_rollover(self):
        src=(ROOT/"src/modules/badusb_ble/ducky_typer.cpp").read_text()
        body=function(src, "static bool waitForDuckyDelay(")
        self.compile_and_run_host(r"""
#include <cassert>
#include <cstdint>
uint32_t now=0;
bool returnToMenu=false;
constexpr int EscPress=1;
bool cancel=false;
int yields=0;
uint32_t millis() {return now;}
bool check(int) {return cancel;}
int pdMS_TO_TICKS(int x) {return x;}
void vTaskDelay(int n) {now+=n;++yields;}
""" + body + r"""
int main() {
    assert(waitForDuckyDelay(0) && yields==0);
    assert(waitForDuckyDelay(25) && now==30 && yields==3);
    cancel=true; assert(!waitForDuckyDelay(60000) && yields==3);
    cancel=false; returnToMenu=true; assert(!waitForDuckyDelay(60000));
    returnToMenu=false; now=0xfffffff0U; yields=0;
    assert(waitForDuckyDelay(40) && yields==4 && now==24);
}
""")

    def test_hid_state_and_cleanup_guards(self):
        src=(ROOT/"src/modules/badusb_ble/ducky_typer.cpp").read_text()
        body=function(src,"void key_input(FS fs,")
        self.assertIn("char Cmd[25] = {}", body)
        self.assertNotIn("static int nextStringDelay", body)
        self.assertNotIn("static int defaultStringDelay", body)
        self.assertIn("if (_hid == nullptr)", body)
        self.assertIn("if (Cmd[0] == 0) continue", body)
        self.assertIn("if (returnToMenu || check(EscPress)) goto EXIT", body)
        self.assertIn("_hid->releaseAll()", body[body.index("EXIT:"):])

    def test_only_the_requested_hardware_groups_are_removed(self):
        normal = ["src/modules/rf/rf_scan.cpp", "src/modules/ir/ir_read.cpp",
                  "src/modules/rfid/PN532.cpp", "src/modules/NRF24/nrf24.cpp",
                  "src/modules/badusb_ble/ducky_typer.cpp", "src/core/wifi/webInterface.cpp"]
        # NRF24 source filename varies upstream; verify the directory separately.
        for f in normal:
            if f.endswith("/NRF24/nrf24.cpp"): continue
            self.assertTrue((ROOT/f).is_file(), f)
        self.assertTrue(any((ROOT/"src/modules/NRF24").glob("*.cpp")))
        self.assertTrue((ROOT/"LICENSE").is_file())
        self.assertNotIn("Bruce", function((ROOT/"src/main.cpp").read_text(),"void boot_screen()"))

if __name__=="__main__":
    unittest.main(verbosity=2)
