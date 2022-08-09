

        .area   CODE1   (ABS)
        .org    0x5300

START:
        ; init
        LD      SP,0xffff
        LD      A,0
        LD      C,0xE0
        OUT     (C),A
        LD      C,0xE4
        OUT     (C),A
        LD      C,0xEC
        OUT     (C),A

        ; cls
        LD      D,0x80
        LD      HL,0x3c00
        LD      BC,0x0400
CLR:    LD      (HL),D
        INC     HL
        DEC     BC
        LD      A,B
        OR      C 
        JP      NZ,CLR

        ; wait for end of vblank
LOOP1:  IN      A,(0xff)
        BIT     6,A
        JP      NZ,LOOP1

        ; wait for start of vblank
LOOP2:  IN      A,(0xff)
        BIT     6,A
        JP      Z,LOOP2

        ; draw initial frame
        CALL    IFRAME
 
        ; wait for end of vblank
LOOP3:  IN      A,(0xFF)
        BIT     6,A
        JP      NZ,LOOP3

        ; wait for start of vblank
LOOP4:  IN      A,(0xFF)
        BIT     6,A
        JP      Z,LOOP4

        ; switch to left frame
        LD      C,0xFF
        LD      A,2
        OUT     (C),A

        ; draw left frame
        CALL    LFRAME

        ; wait for end of vblank
LOOP5:  IN      A,(0xFF)
        BIT     6,A
        JP      NZ,LOOP5

        ; wait for start of vblank
LOOP6:  IN      A,(0xFF)
        BIT     6,A
        JP      Z,LOOP6

        ; switch to right frame
        LD      C,0xFF
        LD      A,1
        OUT     (C),A

        ; draw right frame
        CALL    RFRAME

        ; loop!
        JP      LOOP3

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

