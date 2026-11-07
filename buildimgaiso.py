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
    print(f"Writing raw binary image to: {img_path}")
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
    print(f"Writing optical ISO image to: {iso_path}")
    with open(img_path, "rb") as f:
        img_data = f.read()
    SECTOR_SIZE = 2048
    img_sectors = len(img_data) // SECTOR_SIZE
    if len(img_data) % SECTOR_SIZE != 0:
        img_sectors += 1
    iso_size = (32 + img_sectors + 10) * SECTOR_SIZE
    iso_image = bytearray(iso_size)
    def write_sector(sector_num, data):
        offset = sector_num * SECTOR_SIZE
        iso_image[offset:offset+len(data)] = data
    pvd = bytearray(SECTOR_SIZE)
    pvd[0] = 1
    pvd[1:6] = b'CD001'
    pvd[6] = 1
    pvd[80:92] = b'QUECTOOS_ISO'
    total_sectors = len(iso_image) // SECTOR_SIZE
    pvd[80:84] = total_sectors.to_bytes(4, 'little')
    pvd[84:88] = total_sectors.to_bytes(4, 'big')
    pvd[128:130] = (2048).to_bytes(2, 'little')
    pvd[132:136] = (2048).to_bytes(4, 'little')
    pvd[136:140] = (2048).to_bytes(4, 'big')
    write_sector(16, pvd)
    vdt = bytearray(SECTOR_SIZE)
    vdt[0] = 255
    vdt[1:6] = b'CD001'
    vdt[6] = 1
    write_sector(17, vdt)
    with open(iso_path, "wb") as f:
        f.write(iso_image)
    print(f"Build successful! Created:\n - {img_path} ({os.path.getsize(img_path)} bytes)\n - {iso_path} ({os.path.getsize(iso_path)} bytes)")
    print("Launching QEMU via floppy emulation (-fda)...")
    run_cmd(f'qemu-system-i386 -fda "{img_path}" -boot a -net none -no-reboot')
if __name__ == "__main__":
    build_and_run()
