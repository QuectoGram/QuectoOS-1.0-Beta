import subprocess
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
def build_and_run():
    print("--- Building 16-bit Bootloader ---")
    run_cmd('nasm -f bin boot.asm -o boot.bin')
    boot_path = os.path.join(BASE_DIR, "boot.bin")
    if os.path.getsize(boot_path) != 512:
        raise RuntimeError("boot.bin must be exactly 512 bytes.")
    print("--- Building 32-bit Entry & C++ Kernel ---")
    run_cmd('nasm -f elf32 entry.asm -o entry.o')
    run_cmd('g++ -m32 -ffreestanding -fno-pie -fno-stack-protector -fno-rtti -fno-exceptions -nostdlib -c kernel.cpp -o kernel.o')
    run_cmd('g++ -m32 -nostdlib -Wl,--nmagic -T linker.ld entry.o kernel.o -o kernel.exe')
    run_cmd('objcopy -O binary kernel.exe kernel.bin')
    kernel_path = os.path.join(BASE_DIR, "kernel.bin")
    img_path = os.path.join(BASE_DIR, "QuectoOS-1.0-Beta.img")
    print(f"Creating raw disk image at: {img_path}")
    with open(img_path, "wb") as outfile:
        with open(boot_path, "rb") as infile:
            outfile.write(infile.read())
        with open(kernel_path, "rb") as infile:
            outfile.write(infile.read())
        current_size = outfile.tell()
        floppy_size = 1440 * 1024
        if current_size < floppy_size:
            outfile.write(b'\x00' * (floppy_size - current_size))
    iso_path = os.path.join(BASE_DIR, "QuectoOS-1.0-Beta.iso")
    iso_dir = os.path.join(BASE_DIR, "iso_root")
    os.makedirs(iso_dir, exist_ok=True)
    iso_img_copy = os.path.join(iso_dir, "floppy.img")
    with open(img_path, "rb") as src, open(iso_img_copy, "wb") as dst:
        dst.write(src.read())

    print("--- Packaging into ISO 9660 ---")
    iso_built = False
    try:
        run_cmd(f'xorriso -as mkisofs -o "{iso_path}" -b floppy.img "{iso_dir}"')
        iso_built = True
    except RuntimeError:
        pass
    if not iso_built:
        try:
            run_cmd(f'genisoimage -o "{iso_path}" -b floppy.img "{iso_dir}"')
            iso_built = True
        except RuntimeError:
            pass
    if not iso_built:
        print("\n[WARNING] 'xorriso' or 'genisoimage' not found in your MSYS2 environment.")
        print("To install xorriso via MSYS2 UCRT64 terminal, run:")
        print("    pacman -S mingw-w64-ucrt64-xorriso")
        print("For now, copying the valid 1.44MB .img file as the .iso fallback so you can still test.")
        with open(img_path, "rb") as src, open(iso_path, "wb") as dst:
            dst.write(src.read())
    print(f"\nBuild successful! Created '{img_path}' and '{iso_path}'.")
    print("Launching QEMU...")
    run_cmd(f'qemu-system-i386 -drive format=raw,file="{img_path}" -boot c -net none -no-reboot')
if __name__ == "__main__":
    build_and_run()


