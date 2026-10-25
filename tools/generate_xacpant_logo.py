from PIL import Image
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/xacpant-logo.png'
im=Image.open(source).convert('RGBA')
background=Image.new('RGBA',im.size,(0,0,0,255)); background.alpha_composite(im); im=background.convert('RGB')
w,h=im.size
pixels=[((r>>3)<<11)|((g>>2)<<5)|(b>>3) for r,g,b in im.getdata()]
header=['#pragma once','#include <cstdint>','#include <pgmspace.h>',f'constexpr int XACPANT_LOGO_WIDTH = {w};',f'constexpr int XACPANT_LOGO_HEIGHT = {h};','static const uint16_t xacpantLogoPixels[] PROGMEM = {']
header+= [','.join(f'0x{v:04x}' for v in pixels[i:i+16])+',' for i in range(0,len(pixels),16)]
header+=['};','']
target=ROOT/'src/assets/xacpant_logo_rgb565.h';target.parent.mkdir(parents=True,exist_ok=True);target.write_text('\n'.join(header),encoding='utf-8')
print(hashlib.sha256(source.read_bytes()).hexdigest(),w,h)
