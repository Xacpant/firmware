// Copyright (C) 2026 yusuf9847748-cyber
// SPDX-License-Identifier: AGPL-3.0-only
#include "live_status.h"
#include "core/display.h"
#include "core/mykeyboard.h"
#include <globals.h>

void showLiveSystemStatus() {
    bool paused = false;
    bool firstDraw = true;
    uint32_t lastDrawAt = 0;
    returnToMenu = false;
    while (!returnToMenu) {
        if (check(EscPress)) break;
        if (check(SelPress)) {
            paused = !paused;
            firstDraw = true;
        }
        const uint32_t now = millis();
        if (firstDraw || (!paused && now - lastDrawAt >= 1000)) {
            drawMainBorderWithTitle(paused ? "Live Status [PAUSED]" : "Live Status");
            tft.setCursor(10, 30);
            tft.setTextSize(XACPANT_FONT_SMALL);
            tft.setTextColor(bruceConfig.priColor, bruceConfig.bgColor);
            padprintf("Uptime: %lu s\n", static_cast<unsigned long>(now / 1000));
            padprintf("Heap free: %lu KB\n", static_cast<unsigned long>(ESP.getFreeHeap() / 1024));
            padprintf("Largest block: %lu KB\n", static_cast<unsigned long>(ESP.getMaxAllocHeap() / 1024));
            padprintf("Lowest free: %lu KB\n", static_cast<unsigned long>(ESP.getMinFreeHeap() / 1024));
            if (psramFound()) {
                padprintf("PSRAM free: %lu KB\n", static_cast<unsigned long>(ESP.getFreePsram() / 1024));
                padprintf("PSRAM total: %lu KB\n", static_cast<unsigned long>(ESP.getPsramSize() / 1024));
            } else padprintln("PSRAM: not detected");
            padprintln(sdcardMounted ? "SD: mounted" : "SD: not mounted");
            padprintln("SEL: pause/resume  BACK: exit");
            lastDrawAt = now;
            firstDraw = false;
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
