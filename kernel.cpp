// ========================================================
//                QuectoOS Kernels
// ========================================================



//     Code Here


inline void outb(unsigned short port, unsigned char val) {
    __asm__ volatile ("outb %0, %1" : : "a"(val), "d"(port));
}
inline unsigned char inb(unsigned short port) {
    unsigned char ret;
    __asm__ volatile ("inb %1, %0" : "=a"(ret) : "d"(port));
    return ret;
}
extern "C" void kernel_main(void) {
    (void)inb(0x3DA);
    outb(0x3C0, 0x10);
    unsigned char mode = inb(0x3C1);
    mode &= ~0x08;
    (void)inb(0x3DA);
    outb(0x3C0, 0x10); 
    outb(0x3C0, mode); 
    (void)inb(0x3DA);
    outb(0x3C0, 0x20);
    volatile char *video_memory = (volatile char*) 0xB8000;
    for (int i = 0; i < 80 * 25; i++) {
        video_memory[i * 2] = ' ';
        video_memory[i * 2 + 1] = 0x1F;
    }
    const char *str = "Welcome to QuectoOS";
    int i = 0;
    while (str[i] != '\0') {
        video_memory[i * 2] = str[i];
        video_memory[i * 2 + 1] = 0x1F;
        i++;
    }
    const char *str1 = "Made by U123573";
    int j = 0;
    int row1_offset = 80 * 2;
    while (str1[j] != '\0') {
        video_memory[row1_offset + (j * 2)] = str1[j];
        video_memory[row1_offset + (j * 2) + 1] = 0x1F;
        j++;
    }
    while (1) {
        __asm__ volatile ("hlt");
    }
}


