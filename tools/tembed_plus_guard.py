"""Reject alternate PlatformIO targets before compiling this Xacpant specialization."""
Import("env")

if env.subst("$PIOENV") != "lilygo-t-embed-cc1101-plus":
    raise RuntimeError("Only lilygo-t-embed-cc1101-plus is supported by this Xacpant fork")
if env.GetProjectOption("board") != "lilygo-t-embed-cc1101":
    raise RuntimeError("This profile requires the T-Embed CC1101 board definition")
board = env.BoardConfig()
if board.get("build.mcu") != "esp32s3" or board.get("upload.flash_size") != "16MB":
    raise RuntimeError("T-Embed Plus requires ESP32-S3 and the 16MB flash layout")
