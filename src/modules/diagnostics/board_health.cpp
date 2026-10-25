// Copyright (C) 2026 Xacpant
// SPDX-License-Identifier: AGPL-3.0-only
#include "board_health.h"
#include "core/bus_HAL.h"
#include "core/display.h"
#include "core/xacpant_brand.h"
#include <esp_system.h>
#include <esp32-hal-psram.h>
#include <globals.h>

// Probe only the three documented system-I2C devices. No radio is transmitted.
void showBoardHealth() {
    drawMainBorderWithTitle("Onboard Health");
    padprintln(XACPANT_NAME " / T-Embed Plus");
    TwoWire *bus = acquireI2CBus();
    if (bus == nullptr) {
        padprintln("I2C bus unavailable");
    } else {
        struct Device { uint8_t address; const char *name; };
        const Device devices[] = {{0x24, "PN532"}, {0x55, "BQ27220"}, {0x6b, "BQ25896"}};
        for (const auto &device : devices) {
            bus->beginTransmission(device.address);
            const int status = bus->endTransmission();
            padprintf("%s [0x%02X]: %s\n", device.name, device.address, status == 0 ? "ACK" : "no ACK");
            vTaskDelay(pdMS_TO_TICKS(1));
        }
        releaseI2CBus();
    }
    padprintf("PSRAM: %s\n", psramFound() ? "detected" : "not detected");
    padprintf("SD: %s\n", sdcardMounted ? "mounted" : "not mounted");
    padprintln("SEL / BACK: close");
    while (!returnToMenu && !check(EscPress) && !check(SelPress)) vTaskDelay(pdMS_TO_TICKS(20));
}

void showResetReason() {
    drawMainBorderWithTitle("Last Reset");
    const esp_reset_reason_t reason = esp_reset_reason();
    const char *name = "Other / unknown";
    switch (reason) {
        case ESP_RST_POWERON: name = "Power on"; break;
        case ESP_RST_SW: name = "Software restart"; break;
        case ESP_RST_PANIC: name = "Panic / exception"; break;
        case ESP_RST_INT_WDT: name = "Interrupt watchdog"; break;
        case ESP_RST_TASK_WDT: name = "Task watchdog"; break;
        case ESP_RST_WDT: name = "Other watchdog"; break;
        case ESP_RST_DEEPSLEEP: name = "Deep sleep wake"; break;
        case ESP_RST_BROWNOUT: name = "Brownout / low voltage"; break;
        default: break;
    }
    padprintln(name);
    padprintf("Reset code: %d\n", static_cast<int>(reason));
    padprintf("Min free heap: %lu KB\n", static_cast<unsigned long>(ESP.getMinFreeHeap() / 1024));
    padprintln("Read-only diagnostic");
    padprintln("SEL / BACK: close");
    while (!returnToMenu && !check(EscPress) && !check(SelPress)) vTaskDelay(pdMS_TO_TICKS(20));
}
