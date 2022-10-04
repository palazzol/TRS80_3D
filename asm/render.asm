        .area   CODE1   (ABS)
        
        .org    0x5300

START:
        DI
        JP      START2

;       RAM Variables

MTYPE:  .blkb   1       ; movie type, 0=mono, 1=stereo
SIDE:   .blkb   1       ; left frame first = 0, right frame first = 1
NFRAMES:.blkw   1       ; number of frames for this movie
NLINES: .blkb   1       ; number of lines for this frame

X1:     .blkb   1       ; Args for line draw...
Y1:     .blkb   1       ; (updated by line draw)
X2:     .blkb   1
Y2:     .blkb   1

BUF:    .blkb   1       ; buffer for cassout bits 

; line draw variables
SX:     .blkb   1       ; increment direction for X
SY:     .blkb   1       ; increment direction for Y
DX:     .blkw   1       ; two byte delta X
DY:     .blkw   1       ; two byte delta Y
ERR:    .blkw   1       ; Error value
E2:     .blkw   1       ; Error value * 2

;
;   Read the movie definition
;   (All registers preserved)

;       Clear screen routine
;       (adapted from William Barden Book)
CLS:    
        PUSH    AF
        PUSH    BC
        PUSH    HL
        LD      B,128
        LD      HL,#0x3C00
$LOOP:  LD      (HL),B
        INC     HL
        LD      A,H
        CP      0x40
        JR      NZ,$LOOP
        POP     HL
        POP     BC
        POP     AF
        RET 

;       Fast Set Routine
;       (adapted from William Barden Book)
;
;       Input: HL -> Location of table holding X, Y
FSETGR:
        PUSH    AF
        PUSH    BC
        PUSH    DE 
        PUSH    IX 
        PUSH    IY
        PUSH    HL
        POP     IX
        LD      D,0
        LD      E,(IX+1)    ; Y is at (IX+1)
        SLA     E
        LD      HL,#FSETGR
        ADD     HL,DE
        LD      BC,TABLEA
        ADD     HL,BC
        PUSH    HL
        POP     IY
        LD      A,(IY+0)
        AND     0xE0
        LD      L,A 
        LD      H,(IY+1)
        LD      E,(IX+0)    ; X is at (IX+0)
        LD      D,0 
        SRL     E 
        ADD     HL,DE 
        LD      A,(IY+0)
        AND     0x1F
        BIT     0,(IX+0)
        JR      Z,$AHEAD
        SLA     A 
$AHEAD: LD      B,(HL)
        OR      B
        LD      (HL),A 
        POP     IY
        POP     IX
        POP     DE
        POP     BC
        POP     AF
        RET
TABLEA  .equ    .-FSETGR
        .word   0x3c00+1
        .word   0x3c00+4
        .word   0x3c00+16
        .word   0x3c40+1
        .word   0x3c40+4
        .word   0x3c40+16
        .word   0x3c80+1
        .word   0x3c80+4
        .word   0x3c80+16
        .word   0x3cc0+1
        .word   0x3cc0+4
        .word   0x3cc0+16
        .word   0x3d00+1
        .word   0x3d00+4
        .word   0x3d00+16
        .word   0x3d40+1
        .word   0x3d40+4
        .word   0x3d40+16
        .word   0x3d80+1
        .word   0x3d80+4
        .word   0x3d80+16
        .word   0x3dc0+1
        .word   0x3dc0+4
        .word   0x3dc0+16
        .word   0x3e00+1
        .word   0x3e00+4
        .word   0x3e00+16
        .word   0x3e40+1
        .word   0x3e40+4
        .word   0x3e40+16
        .word   0x3e80+1
        .word   0x3e80+4
        .word   0x3e80+16
        .word   0x3ec0+1
        .word   0x3ec0+4
        .word   0x3ec0+16
        .word   0x3f00+1
        .word   0x3f00+4
        .word   0x3f00+16
        .word   0x3f40+1
        .word   0x3f40+4
        .word   0x3f40+16
        .word   0x3f80+1
        .word   0x3f80+4
        .word   0x3f80+16
        .word   0x3fc0+1
        .word   0x3fc0+4
        .word   0x3fc0+16

;   Time Delay routine
;       (adapted from William Barden Book)
; 
;   INPUT: HL -> milliseconds
;TIMEDL:
;        PUSH    BC
;        PUSH    DE
;        LD      DE,1
;$dly1:  LD      B,134
;$dly2:  DJNZ    $dly2
;        SBC     HL,DE
;        JR      NZ,$dly1
;        POP     DE
;        POP     BC
;        RET

;        Initialize RAMBO Board
WRITERBO:
        PUSH    AF
        PUSH    BC
        LD      A,0x40     ; Inc on Write, Address 0x000000
        LD      C,0xD0
        OUT     (C),A 
        LD      A,0x00 
        LD      C,0xD2
        OUT     (C),A 
        LD      C,0xD3
        OUT     (C),A
        POP     BC
        POP     AF
        RET

;       Main starts here

START2:
        CALL    CLS             ; clear the screen
        CALL    WRITERBO        ; initialize RAMBO

        LD      A,0
        OUT     (0xE0),A
        OUT     (0xE4),A
        LD      A,0x10          ; Enable EXTIOSEL, No video wait
        OUT     (0xEC),A

        LD      HL,MOVIE        ; Init to data start
        LD      DE,(MOVIE)      ; Read number of frames
        INC     HL
        INC     HL
        LD      (NFRAMES),DE

        LD      A,(HL)          ; Read the first frame type
        INC     HL
        CP      'E
        JR      Z,ANIMATE       ; all done - go to ANIMATE

        CP      'F              ; mono frames
        JR      Z,MONO          ; go do that

STEREO:
        LD      A,1
        LD      (MTYPE),A 

        CP      'L              ; stereo frame L
        JR      Z,LEFT

RIGHT:
        LD      A,1             ; stereo frame R
        LD      (SIDE),A 
        JP      AHEAD

LEFT:   LD      A,0
        LD      (SIDE),A
        JP      AHEAD

MONO:   LD      A,0
        LD      (MTYPE),A
        JR      AHEAD

;       Read a Frame

NFRAME:
        LD      A,(HL)          ; read frame code
        INC     HL
        CP      'E
        JR      Z,ANIMATE
AHEAD:  
;        LD      (0x3C00),A      ; MARK THIS FRAME
;        LD      (0x3C3F),A      ; MARK THIS FRAME
;        LD      (0x3FC0),A      ; MARK THIS FRAME
;        LD      (0x3FFF),A      ; MARK THIS FRAME

        LD      A,(HL)          ; read number of lines
        INC     HL
        LD      (NLINES),A 

        LD      B,A
NLINE:
        CALL    DOLINE
        DJNZ    NLINE
        
;       Save a Frame to RAMBO

SAVFRM:
        PUSH    HL
        PUSH    BC
        LD      HL,0x3C00
        LD      C,0xD1
        LD      B,0x00
        OTIR    
        OTIR    
        OTIR    
        OTIR    
        POP     BC
        POP     HL

        CALL    CLS

        JR      NFRAME

;       TBD - Run animation
        
ANIMATE:
        LD      A,(SIDE)
        CP      0x01
        JR      NZ,LFIRST

        LD      A,0xAA
        LD      (BUF),A
        JR      READRBO

LFIRST:
        LD      A,0x55
        LD      (BUF),A

READRBO:
        LD      A,0x20     ; Inc on Read, Address 0x000000
        LD      C,0xD0
        OUT     (C),A 
        LD      A,0x00 
        LD      C,0xD2
        OUT     (C),A 
        LD      C,0xD3
        OUT     (C),A
      
        LD      DE,(NFRAMES)    ; Frame Counter

LODFRM:
        ; get ready for next frame
        LD      B,0
        LD      C,0xD1
        LD      HL,0x3C00
        LD      A,(BUF)
        RRCA 
        LD      (BUF),A

        ; wait for end of vblank
        ; (VDRV goes from 1->0)
LOOP3:  IN      A,(0xFF)
        BIT     6,A
        JP      NZ,LOOP3

        ; wait for start of vblank
        ; (VDRV goes from 0->1)
LOOP4:  IN      A,(0xFF)
        BIT     6,A
        JP      Z,LOOP4

        ; switch to next frame
        LD      A,(BUF)
;        AND     0x03
        OUT     (0xFF),A

        ; transfer 1K from RAMBO to screen
        ; HL, Band C are set already
        INIR
        INIR
        INIR
        INIR

        DEC     DE
        LD      A,D 
        OR      E
        JR      NZ,LODFRM

        JR      READRBO

;       draw one line on the screen
DOLINE:
        LD      A,(HL)
        INC     HL
        LD      (X1),A

        LD      A,(HL)
        INC     HL
        LD      (Y1),A

        LD      A,(HL)
        INC     HL
        LD      (X2),A

        LD      A,(HL)
        INC     HL
        LD      (Y2),A

;       draw a line on the screen

;       for now, we will draw the end points first
;        PUSH    HL
;        LD      HL,#X1
;        CALL    FSETGR
;        LD      HL,#X2
;        CALL    FSETGR
;        POP     HL

        CALL    BRES 

        RET

; Bresenham line drawing algorithm

BRES:
        PUSH    AF
        PUSH    BC
        PUSH    DE
        PUSH    HL
        PUSH    IX

        LD      HL,#X1
        PUSH    HL
        POP     IX

        LD      A,(IX+2)   ; X2
        CP      (IX+0)     ; X2-X1
        JR      C,$L3      ; if X2-X1 <= 0, Jump
        JR      Z,$L3
        LD      A,0x01
        LD      (SX),A     ; SX = 1
        LD      A,(IX+2)
        SUB     (IX+0)     ; A = X2-X1
        JR      $L4
$L3:    LD      A,0xff     ; SX = -1
        LD      (SX),A
        LD      A,(IX+0)
        SUB     (IX+2)
$L4:    LD      (DX),A     ; DX = ABS(X2-X1)
        LD      A,0x00
        LD      (DX+1),A   ; DX is sign extended

        LD      A,(IX+3)   ; Y2
        CP      (IX+1)     ; Y2-Y1
        JR      C,$L5      ; if Y2-Y1 <= 0, Jump
        JR      Z,$L5
        LD      A,0x01
        LD      (SY),A     ; SY = 1
        LD      A,(IX+3)
        SUB     (IX+1)     ; A = Y2-Y1
        JR      $L6
$L5:    LD      A,0xff     ; SY = -1
        LD      (SY),A
        LD      A,(IX+1)
        SUB     (IX+3)
$L6:    NEG
        LD      (DY),A     ; DY = -ABS(Y2-Y1)
        LD      A,0xff
        LD      (DY+1),A   ; DY is sign-extended

        LD      HL,(DX)
        LD      DE,(DY)
        ADD     HL,DE
        LD      (ERR),HL   ; ERR = DX + DY

PNEXT:
        PUSH    HL         ; Draw pixel
        LD      HL,#X1
        CALL    FSETGR
        POP     HL
        
        LD      A,(IX+0)    ; Am I done?
        CP      (IX+2)
        JR      NZ,$CONT 
        LD      A,(IX+1)
        CP      (IX+3)
        JR      Z,$EXIT 
$CONT: 
        LD      HL,(ERR)
        SLA     L 
        RL      H          
        LD      (E2),HL     ; E2 = ERR*2

        SCF
        CCF 
        LD      HL,(E2)
        LD      DE,(DY)
        SBC     HL,DE
        BIT     7,H 
        JR      NZ,$L7      ; IF E2 < DY, jump 
        LD      HL,(ERR)
        LD      DE,(DY) 
        ADD     HL,DE 
        LD      (ERR),HL    ; ERR += DY
        LD      A,(X1)
        LD      B,A
        LD      A,(SX)
        ADD     A,B
        LD      (X1),A      ; X1 += SX

$L7:
        SCF
        CCF 
        LD      HL,(DX)
        LD      DE,(E2)
        SBC     HL,DE
        BIT     7,H
        JR      NZ,$L8      ; IF E2 > DX, jump 
        LD      HL,(ERR)
        LD      DE,(DX) 
        ADD     HL,DE 
        LD      (ERR),HL    ; ERR += DX
        LD      A,(Y1)
        LD      B,A
        LD      A,(SY)
        ADD     A,B
        LD      (Y1),A      ; Y1 += SY
$L8:
        JP      PNEXT

$EXIT:
        POP     IX
        POP     HL
        POP     DE
        POP     BC
        POP     AF 
        RET

MOVIE:
    ; MOVIE DATA GOES HERE
