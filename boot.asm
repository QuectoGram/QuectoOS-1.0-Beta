; ====================================================
;               QuectoOS Boots
;=====================================================
;             Bits: 16
;             Written on: Assembly
;             Details: Adding message error
;             Made With: User123573
;=====================================================


; Code Here  ↓

[BITS 16]
[ORG 0x7C00]

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    mov [boot_drive], dl
    sti

    mov ah, 0x00
    mov dl, [boot_drive]
    int 0x13
    jc disk_error

    mov ah, 0x02
    mov al, 15                  
    mov ch, 0
    mov dh, 0
    mov cl, 2
    mov bx, 0x1000
    mov es, bx
    xor bx, bx
    mov dl, [boot_drive]
    int 0x13
    jc disk_error

    jmp 0x1000:0x0000

disk_error:
    xor ax, ax
    mov ds, ax
    mov si, msg_error
    call print_string
    jmp hang

print_string:
    cld
.loop:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp .loop
.done:
    ret

hang:
    cli
.loop:
    hlt
    jmp .loop

boot_drive db 0
msg_error db 'Disk read error!', 13, 10, 0

times 510-($-$$) db 0
dw 0xAA55

