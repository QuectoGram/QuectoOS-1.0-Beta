; ===================================================
;                QuectoOS Entry
; ===================================================
;              Bits: 16, 32
;              Written with: Assembly
;              Lines: 58
;              Made With: User123573
;              Details: (Empty)
; ===================================================





; Code Here ↓


[BITS 16]
SECTION .text

global _start
extern _kernel_main

_start:
    cli
    lgdt [dword gdt_descriptor]
    
    mov eax, cr0
    or eax, 1
    mov cr0, eax
    
    jmp dword 0x08:init_pm

[BITS 32]
init_pm:
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000
    call _kernel_main
    cli
.hang:
    hlt
    jmp .hang

align 4
gdt_start:
    dq 0x0000000000000000
    dq 0x00cf9a000000ffff
    dq 0x00cf92000000ffff
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start
; Code Done!

