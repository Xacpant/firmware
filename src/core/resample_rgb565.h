// Copyright (C) 2026 yusuf9847748-cyber
// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
#include <cstdint>
#include <algorithm>
namespace xacpant {
// Area averaging avoids scanline aliasing when the original art is reduced.
template <typename PixelReader>
uint16_t areaSample565(int x, int y, int dw, int dh, int sw, int sh, PixelReader readPixel) {
    const uint32_t left = static_cast<uint64_t>(x) * sw * 256 / dw;
    const uint32_t right = static_cast<uint64_t>(x + 1) * sw * 256 / dw;
    const uint32_t top = static_cast<uint64_t>(y) * sh * 256 / dh;
    const uint32_t bottom = static_cast<uint64_t>(y + 1) * sh * 256 / dh;
    uint64_t r = 0, g = 0, b = 0, total = 0;
    for (uint32_t sy = top / 256; sy < (bottom + 255) / 256 && sy < static_cast<uint32_t>(sh); ++sy) {
        const uint32_t wy = (std::min)(bottom, (sy + 1) * 256) - (std::max)(top, sy * 256);
        for (uint32_t sx = left / 256; sx < (right + 255) / 256 && sx < static_cast<uint32_t>(sw); ++sx) {
            const uint32_t wx = (std::min)(right, (sx + 1) * 256) - (std::max)(left, sx * 256);
            const uint64_t weight = static_cast<uint64_t>(wx) * wy;
            const uint16_t pixel = readPixel(sx, sy);
            r += ((pixel >> 11) & 31) * weight;
            g += ((pixel >> 5) & 63) * weight;
            b += (pixel & 31) * weight;
            total += weight;
        }
    }
    if (total == 0) return 0;
    return static_cast<uint16_t>(((r / total) << 11) | ((g / total) << 5) | (b / total));
}
} // namespace xacpant
