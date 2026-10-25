// Copyright (C) 2026 yusuf9847748-cyber
// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
#include <cstdint>
namespace xacpant {
struct ImageRect { int x = 0, y = 0, width = 0, height = 0; };
inline ImageRect fitImage(int sw, int sh, int dw, int dh) {
    if (sw <= 0 || sh <= 0 || dw <= 0 || dh <= 0) return {};
    int width = dw;
    const int64_t scaledHeight = static_cast<int64_t>(sh) * dw / sw;
    int height = 0;
    if (scaledHeight > dh) {
        height = dh;
        width = static_cast<int>(static_cast<int64_t>(sw) * dh / sh);
    } else {
        height = static_cast<int>(scaledHeight);
    }
    if (width < 1) width = 1;
    if (height < 1) height = 1;
    return {(dw - width) / 2, (dh - height) / 2, width, height};
}
} // namespace xacpant
