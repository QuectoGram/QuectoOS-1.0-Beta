@echo off
setlocal
echo 1 Building 16 bit Bootloader
nasm -f bin boot.asm -o boot.bin
if errorlevel 1 goto error
echo 2 Building 32 bit Entry & C++ Kernel
nasm -f elf32 entry.asm -o entry.o
if errorlevel 1 goto error
g++ -m32 -ffreestanding -fno-pie -fno-stack-protector -fno-rtti -fno-exceptions -nostdlib -c kernel.cpp -o kernel.o
if errorlevel 1 goto error
g++ -m32 -nostdlib -Wl,-nmagic -T linker.ld entry.o kernel.o -o kernel.exe
if errorlevel 1 goto error
objcopy -O binary kernel.exe kernel.bin
if errorlevel 1 goto error
echo 3 Generating QuectoOS 1.0 Beta img (11 KB)
copy /b boot.bin + kernel.bin "QuectoOS-1.0-Beta.img" > nul
powershell -Command "$f = [System.IO.File]::OpenWrite('QuectoOS-1.0-Beta.img'); $f.SetLength(11264); $f.Close()"
echo.
echo SUCCESS Generated QuectoOS 1.0 Beta
pause
exit /b 0
:error
echo.
echo Build failed
pause
exit /b 1
