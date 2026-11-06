@echo off
qemu-system-i386 -machine pc -drive file=QuectoOS-1.0.img,format=raw,if=floppy
pause
