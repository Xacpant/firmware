// Copyright (C) 2026 yusuf9847748-cyber
// SPDX-License-Identifier: AGPL-3.0-only
#include "ir_monitor.h"
#include "core/display.h"
#include "core/mykeyboard.h"
#include "modules/diagnostics/monitor_state.h"
#include <IRrecv.h>
#include <IRutils.h>
#include <globals.h>

void irReceiverMonitor() {
    if (bruceConfigPins.irRx < 0) {
        displayError("IR receiver pin unavailable", true);
        return;
    }
    IRrecv receiver(bruceConfigPins.irRx, SAFE_STACK_BUFFER_SIZE / 2, 50);
    decode_results result = {};
    IRMonitorState stats;
    String protocol = "Waiting";
    uint16_t bits = 0;
    uint32_t lastDrawAt = 0;
    bool firstDraw = true;
    returnToMenu = false;
    receiver.enableIRIn();

    while (!returnToMenu) {
        if (check(EscPress)) break;
        if (check(SelPress)) {
            stats.reset();
            protocol = "Waiting";
            bits = 0;
            firstDraw = true;
        }
        if (receiver.decode(&result)) {
            stats.record(result.repeat, result.overflow, millis());
            protocol = typeToString(result.decode_type, false);
            bits = result.bits;
            // No raw-buffer pointer is kept after the receiver is resumed.
            receiver.resume();
        }
        const uint32_t now = millis();
        if (firstDraw || now - lastDrawAt >= 250) {
            drawMainBorderWithTitle("IR RX Monitor");
            tft.setCursor(10, 30);
            tft.setTextSize(XACPANT_FONT_SMALL);
            tft.setTextColor(bruceConfig.priColor, bruceConfig.bgColor);
            padprintln("Protocol: " + protocol);
            padprintf("Bits: %u\n", static_cast<unsigned>(bits));
            padprintf("Frames: %lu  Repeats: %lu\n", static_cast<unsigned long>(stats.frames),
                      static_cast<unsigned long>(stats.repeats));
            padprintf("Overflow flags: %lu\n", static_cast<unsigned long>(stats.overflows));
            if (stats.hasFrame) padprintf("Last frame: %lu s ago\n", static_cast<unsigned long>(stats.ageMs(now) / 1000));
            else padprintln("Point a remote at the receiver");
            padprintln("SEL: clear   BACK: exit");
            lastDrawAt = now;
            firstDraw = false;
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    receiver.disableIRIn();
}
