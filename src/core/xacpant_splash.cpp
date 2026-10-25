// Copyright (C) 2026 Xacpant
// SPDX-License-Identifier: AGPL-3.0-only
#include "xacpant_splash.h"
#include "splash_fit.h"
#include "resample_rgb565.h"
#include "xacpant_brand.h"
#include "assets/xacpant_logo_rgb565.h"
#include <globals.h>
#include <array>
#include <pgmspace.h>

void drawXacpantSplash() {
    const int width = tft.width();
    const int height = tft.height();
    tft.fillScreen(TFT_BLACK);
    if (width <= 0 || height <= 22 || width > 320) return;
    const auto fit = xacpant::fitImage(XACPANT_LOGO_WIDTH, XACPANT_LOGO_HEIGHT, width, height - 22);
    // One bounded row on the stack; the source image remains in flash.
    std::array<uint16_t, 320> row;
    for (int y = 0; y < fit.height; ++y) {
        for (int x = 0; x < fit.width; ++x) {
            row[x] = xacpant::areaSample565(x, y, fit.width, fit.height, XACPANT_LOGO_WIDTH, XACPANT_LOGO_HEIGHT,
                [](uint32_t sx, uint32_t sy) { return pgm_read_word(xacpantLogoPixels + sy * XACPANT_LOGO_WIDTH + sx); });
        }
        // TFT_eSPI defaults to byte-swapping RAM image data. Explicitly preserve it.
        const bool swapped = tft.getSwapBytes();
        tft.setSwapBytes(true);
        tft.pushImage(fit.x, fit.y + y, fit.width, 1, row.data());
        tft.setSwapBytes(swapped);
        if ((y & 15) == 15) vTaskDelay(pdMS_TO_TICKS(1));
    }
    tft.setTextSize(2);
    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.drawCentreString(XACPANT_NAME, width / 2, height - 19, 1);
}
