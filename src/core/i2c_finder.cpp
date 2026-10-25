#include "i2c_finder.h"
#include "bus_HAL.h"
#include "display.h"
#include "mykeyboard.h"

#define FIRST_I2C_ADDRESS 0x08
#define LAST_I2C_ADDRESS 0x77

void find_i2c_addresses() {
    drawMainBorderWithTitle("I2C Finder");
    padprintln("");
    padprintln("");

    bool first_found = true;
    TwoWire *Wire = acquireI2CBus();
    if (Wire == nullptr) {
        displayError("I2C bus unavailable", true);
        return;
    }

    padprintln("Checking I2C addresses ...\n\n");
    delay(300);

    padprint("Found: ");

    for (uint8_t i = FIRST_I2C_ADDRESS; i <= LAST_I2C_ADDRESS; i++) {
        if (check(EscPress)) {
            returnToMenu = true;
            releaseI2CBus();
            return;
        }
        Wire->beginTransmission(i);
        if (Wire->endTransmission() == 0) {
            if (!first_found) tft.print(", ");
            else first_found = false;
            tft.printf("0x%X", i);
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }

    while (1) {
        if (check(EscPress) || check(SelPress)) {
            returnToMenu = true;
            break;
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    releaseI2CBus();
}

uint8_t find_first_i2c_address() {
    TwoWire *Wire = acquireI2CBus();
    if (Wire == nullptr) return 0;
    uint8_t found = 0;
    for (uint8_t i = FIRST_I2C_ADDRESS; i <= LAST_I2C_ADDRESS; i++) {
        Wire->beginTransmission(i);
        if (Wire->endTransmission() == 0) {
            found = i;
            break;
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    releaseI2CBus();
    return found;
}

bool check_i2c_address(uint8_t i2c_address) {
    if (i2c_address < FIRST_I2C_ADDRESS || i2c_address > LAST_I2C_ADDRESS) return false;
    TwoWire *Wire = acquireI2CBus();
    if (Wire == nullptr) return false;
    Wire->beginTransmission(i2c_address);
    int error = Wire->endTransmission();
    releaseI2CBus();
    return (error == 0);
}
