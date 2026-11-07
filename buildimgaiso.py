import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

def build_and_run():
    run_cmd('nasm -f bin boot.asm -o boot.bin')
    boot_path = os.path.join(BASE_DIR, "boot.bin")
    if os.path.getsize(boot_path) != 512:
        raise RuntimeError("boot.bin must be exactly 512 bytes.")
        
    run_cmd('nasm -f elf32 entry.asm -o entry.o')
    run_cmd('g++ -m32 -ffreestanding -fno-pie -fno-stack-protector -fno-rtti -fno-exceptions -nostdlib -c kernel.cpp -o kernel.o')
    run_cmd('g++ -m32 -nostdlib -T linker.ld entry.o kernel.o -o kernel.exe')
    run_cmd('objcopy -O binary kernel.exe kernel.bin')
    kernel_path = os.path.join(BASE_DIR, "kernel.bin")
    
    img_path = os.path.join(BASE_DIR, "QuectoOS-1.0-Beta.img")
    with open(img_path, "wb") as outfile:
        with open(boot_path, "rb") as infile:
            outfile.write(infile.read())
        with open(kernel_path, "rb") as infile:
            outfile.write(infile.read())
        
        current_size = outfile.tell()
        padding_needed = (512 - (current_size % 512)) % 512
        if padding_needed > 0:
            outfile.write(b'\x00' * padding_needed)

    iso_path = os.path.join(BASE_DIR, "QuectoOS-1.0-Beta.iso")
    with open(img_path, "rb") as src, open(iso_path, "wb") as dst:
        dst.write(src.read())

    print(f"Build successful! '{img_path}' and '{iso_path}' created natively.")
    print("Launching QEMU via hardware drive master channel mapping...")

    run_cmd(f'qemu-system-i386 -drive format=raw,file="{iso_path}" -boot c -net none -no-reboot')

if __name__ == "__main__":
    build_and_run()


