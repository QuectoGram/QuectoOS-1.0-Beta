@echo off
qemu-system-i386 -machine pc -drive file=QuectoOS.img,format=raw,if=floppy
pause
