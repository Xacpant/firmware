// Copyright (C) 2026 yusuf9847748-cyber
// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
#include <cstdint>

// Independent of Arduino so timing/counter boundaries can be tested on the host.
struct IRMonitorState {
    uint32_t frames = 0;
    uint32_t repeats = 0;
    uint32_t overflows = 0;
    uint32_t lastFrameAt = 0;
    bool hasFrame = false;

    static void increment(uint32_t &counter) {
        if (counter != UINT32_MAX) ++counter;
    }
    void record(bool repeat, bool overflow, uint32_t now) {
        increment(frames);
        if (repeat) increment(repeats);
        if (overflow) increment(overflows);
        lastFrameAt = now;
        hasFrame = true;
    }
    uint32_t ageMs(uint32_t now) const { return now - lastFrameAt; }
    void reset() { *this = IRMonitorState{}; }
};
