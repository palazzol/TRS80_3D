                              1         .area   CODE1   (ABS)
                              2         
   5300                       3         .org    0x5300
                              4 
   5300                       5 START:
   5300 F3            [ 4]    6         DI
   5301 C3 E5 53      [10]    7         JP      START2
                              8 
                              9 ;       RAM Variables
                             10 
   5304                      11 MTYPE:  .blkb   1       ; movie type, 0=mono, 1=stereo
   5305                      12 SIDE:   .blkb   1       ; left frame first = 0, right frame first = 1
   5306                      13 NFRAMES:.blkw   1       ; number of frames for this movie
   5308                      14 NLINES: .blkb   1       ; number of lines for this frame
                             15 
   5309                      16 X1:     .blkb   1       ; Args for line draw...
   530A                      17 Y1:     .blkb   1       ; (updated by line draw)
   530B                      18 X2:     .blkb   1
   530C                      19 Y2:     .blkb   1
                             20 
   530D                      21 BUF:    .blkb   1       ; buffer for cassout bits 
                             22 
                             23 ; line draw variables
   530E                      24 SX:     .blkb   1       ; increment direction for X
   530F                      25 SY:     .blkb   1       ; increment direction for Y
   5310                      26 DX:     .blkw   1       ; two byte delta X
   5312                      27 DY:     .blkw   1       ; two byte delta Y
   5314                      28 ERR:    .blkw   1       ; Error value
   5316                      29 E2:     .blkw   1       ; Error value * 2
                             30 
                             31 ;
                             32 ;   Read the movie definition
                             33 ;   (All registers preserved)
                             34 
                             35 ;       Clear screen routine
                             36 ;       (adapted from William Barden Book)
   5318                      37 CLS:    
   5318 F5            [11]   38         PUSH    AF
   5319 C5            [11]   39         PUSH    BC
   531A E5            [11]   40         PUSH    HL
   531B 06 80         [ 7]   41         LD      B,128
   531D 21 00 3C      [10]   42         LD      HL,#0x3C00
   5320 70            [ 7]   43 $LOOP:  LD      (HL),B
   5321 23            [ 6]   44         INC     HL
   5322 7C            [ 4]   45         LD      A,H
   5323 FE 40         [ 7]   46         CP      0x40
   5325 20 F9         [12]   47         JR      NZ,$LOOP
   5327 E1            [10]   48         POP     HL
   5328 C1            [10]   49         POP     BC
   5329 F1            [10]   50         POP     AF
   532A C9            [10]   51         RET 
                             52 
                             53 ;       Fast Set Routine
                             54 ;       (adapted from William Barden Book)
                             55 ;
                             56 ;       Input: HL -> Location of table holding X, Y
   532B                      57 FSETGR:
   532B F5            [11]   58         PUSH    AF
   532C C5            [11]   59         PUSH    BC
   532D D5            [11]   60         PUSH    DE 
   532E DD E5         [15]   61         PUSH    IX 
   5330 FD E5         [15]   62         PUSH    IY
   5332 E5            [11]   63         PUSH    HL
   5333 DD E1         [14]   64         POP     IX
   5335 16 00         [ 7]   65         LD      D,0
   5337 DD 5E 01      [19]   66         LD      E,(IX+1)    ; Y is at (IX+1)
   533A CB 23         [ 8]   67         SLA     E
   533C 21 2B 53      [10]   68         LD      HL,#FSETGR
   533F 19            [11]   69         ADD     HL,DE
   5340 01 45 00      [10]   70         LD      BC,TABLEA
   5343 09            [11]   71         ADD     HL,BC
   5344 E5            [11]   72         PUSH    HL
   5345 FD E1         [14]   73         POP     IY
   5347 FD 7E 00      [19]   74         LD      A,(IY+0)
   534A E6 E0         [ 7]   75         AND     0xE0
   534C 6F            [ 4]   76         LD      L,A 
   534D FD 66 01      [19]   77         LD      H,(IY+1)
   5350 DD 5E 00      [19]   78         LD      E,(IX+0)    ; X is at (IX+0)
   5353 16 00         [ 7]   79         LD      D,0 
   5355 CB 3B         [ 8]   80         SRL     E 
   5357 19            [11]   81         ADD     HL,DE 
   5358 FD 7E 00      [19]   82         LD      A,(IY+0)
   535B E6 1F         [ 7]   83         AND     0x1F
   535D DD CB 00 46   [20]   84         BIT     0,(IX+0)
   5361 28 02         [12]   85         JR      Z,$AHEAD
   5363 CB 27         [ 8]   86         SLA     A 
   5365 46            [ 7]   87 $AHEAD: LD      B,(HL)
   5366 B0            [ 4]   88         OR      B
   5367 77            [ 7]   89         LD      (HL),A 
   5368 FD E1         [14]   90         POP     IY
   536A DD E1         [14]   91         POP     IX
   536C D1            [10]   92         POP     DE
   536D C1            [10]   93         POP     BC
   536E F1            [10]   94         POP     AF
   536F C9            [10]   95         RET
                     0045    96 TABLEA  .equ    .-FSETGR
   5370 01 3C                97         .word   0x3c00+1
   5372 04 3C                98         .word   0x3c00+4
   5374 10 3C                99         .word   0x3c00+16
   5376 41 3C               100         .word   0x3c40+1
   5378 44 3C               101         .word   0x3c40+4
   537A 50 3C               102         .word   0x3c40+16
   537C 81 3C               103         .word   0x3c80+1
   537E 84 3C               104         .word   0x3c80+4
   5380 90 3C               105         .word   0x3c80+16
   5382 C1 3C               106         .word   0x3cc0+1
   5384 C4 3C               107         .word   0x3cc0+4
   5386 D0 3C               108         .word   0x3cc0+16
   5388 01 3D               109         .word   0x3d00+1
   538A 04 3D               110         .word   0x3d00+4
   538C 10 3D               111         .word   0x3d00+16
   538E 41 3D               112         .word   0x3d40+1
   5390 44 3D               113         .word   0x3d40+4
   5392 50 3D               114         .word   0x3d40+16
   5394 81 3D               115         .word   0x3d80+1
   5396 84 3D               116         .word   0x3d80+4
   5398 90 3D               117         .word   0x3d80+16
   539A C1 3D               118         .word   0x3dc0+1
   539C C4 3D               119         .word   0x3dc0+4
   539E D0 3D               120         .word   0x3dc0+16
   53A0 01 3E               121         .word   0x3e00+1
   53A2 04 3E               122         .word   0x3e00+4
   53A4 10 3E               123         .word   0x3e00+16
   53A6 41 3E               124         .word   0x3e40+1
   53A8 44 3E               125         .word   0x3e40+4
   53AA 50 3E               126         .word   0x3e40+16
   53AC 81 3E               127         .word   0x3e80+1
   53AE 84 3E               128         .word   0x3e80+4
   53B0 90 3E               129         .word   0x3e80+16
   53B2 C1 3E               130         .word   0x3ec0+1
   53B4 C4 3E               131         .word   0x3ec0+4
   53B6 D0 3E               132         .word   0x3ec0+16
   53B8 01 3F               133         .word   0x3f00+1
   53BA 04 3F               134         .word   0x3f00+4
   53BC 10 3F               135         .word   0x3f00+16
   53BE 41 3F               136         .word   0x3f40+1
   53C0 44 3F               137         .word   0x3f40+4
   53C2 50 3F               138         .word   0x3f40+16
   53C4 81 3F               139         .word   0x3f80+1
   53C6 84 3F               140         .word   0x3f80+4
   53C8 90 3F               141         .word   0x3f80+16
   53CA C1 3F               142         .word   0x3fc0+1
   53CC C4 3F               143         .word   0x3fc0+4
   53CE D0 3F               144         .word   0x3fc0+16
                            145 
                            146 ;   Time Delay routine
                            147 ;       (adapted from William Barden Book)
                            148 ; 
                            149 ;   INPUT: HL -> milliseconds
                            150 ;TIMEDL:
                            151 ;        PUSH    BC
                            152 ;        PUSH    DE
                            153 ;        LD      DE,1
                            154 ;$dly1:  LD      B,134
                            155 ;$dly2:  DJNZ    $dly2
                            156 ;        SBC     HL,DE
                            157 ;        JR      NZ,$dly1
                            158 ;        POP     DE
                            159 ;        POP     BC
                            160 ;        RET
                            161 
                            162 ;        Initialize RAMBO Board
   53D0                     163 WRITERBO:
   53D0 F5            [11]  164         PUSH    AF
   53D1 C5            [11]  165         PUSH    BC
   53D2 3E 40         [ 7]  166         LD      A,0x40     ; Inc on Write, Address 0x000000
   53D4 0E D0         [ 7]  167         LD      C,0xD0
   53D6 ED 79         [12]  168         OUT     (C),A 
   53D8 3E 00         [ 7]  169         LD      A,0x00 
   53DA 0E D2         [ 7]  170         LD      C,0xD2
   53DC ED 79         [12]  171         OUT     (C),A 
   53DE 0E D3         [ 7]  172         LD      C,0xD3
   53E0 ED 79         [12]  173         OUT     (C),A
   53E2 C1            [10]  174         POP     BC
   53E3 F1            [10]  175         POP     AF
   53E4 C9            [10]  176         RET
                            177 
                            178 ;       Main starts here
                            179 
   53E5                     180 START2:
   53E5 CD 18 53      [17]  181         CALL    CLS             ; clear the screen
   53E8 CD D0 53      [17]  182         CALL    WRITERBO        ; initialize RAMBO
                            183 
   53EB 3E 00         [ 7]  184         LD      A,0
   53ED D3 E0         [11]  185         OUT     (0xE0),A
   53EF D3 E4         [11]  186         OUT     (0xE4),A
   53F1 3E 10         [ 7]  187         LD      A,0x10          ; Enable EXTIOSEL, No video wait
   53F3 D3 EC         [11]  188         OUT     (0xEC),A
                            189 
   53F5 21 A7 55      [10]  190         LD      HL,MOVIE        ; Init to data start
   53F8 ED 5B A7 55   [20]  191         LD      DE,(MOVIE)      ; Read number of frames
   53FC 23            [ 6]  192         INC     HL
   53FD 23            [ 6]  193         INC     HL
   53FE ED 53 06 53   [20]  194         LD      (NFRAMES),DE
                            195 
   5402 7E            [ 7]  196         LD      A,(HL)          ; Read the first frame type
   5403 23            [ 6]  197         INC     HL
   5404 FE 45         [ 7]  198         CP      'E
   5406 28 4D         [12]  199         JR      Z,ANIMATE       ; all done - go to ANIMATE
                            200 
   5408 FE 46         [ 7]  201         CP      'F              ; mono frames
   540A 28 19         [12]  202         JR      Z,MONO          ; go do that
                            203 
   540C                     204 STEREO:
   540C 3E 01         [ 7]  205         LD      A,1
   540E 32 04 53      [13]  206         LD      (MTYPE),A 
                            207 
   5411 FE 4C         [ 7]  208         CP      'L              ; stereo frame L
   5413 28 08         [12]  209         JR      Z,LEFT
                            210 
   5415                     211 RIGHT:
   5415 3E 01         [ 7]  212         LD      A,1             ; stereo frame R
   5417 32 05 53      [13]  213         LD      (SIDE),A 
   541A C3 32 54      [10]  214         JP      AHEAD
                            215 
   541D 3E 00         [ 7]  216 LEFT:   LD      A,0
   541F 32 05 53      [13]  217         LD      (SIDE),A
   5422 C3 32 54      [10]  218         JP      AHEAD
                            219 
   5425 3E 00         [ 7]  220 MONO:   LD      A,0
   5427 32 04 53      [13]  221         LD      (MTYPE),A
   542A 18 06         [12]  222         JR      AHEAD
                            223 
                            224 ;       Read a Frame
                            225 
   542C                     226 NFRAME:
   542C 7E            [ 7]  227         LD      A,(HL)          ; read frame code
   542D 23            [ 6]  228         INC     HL
   542E FE 45         [ 7]  229         CP      'E
   5430 28 23         [12]  230         JR      Z,ANIMATE
   5432                     231 AHEAD:  
                            232 ;        LD      (0x3C00),A      ; MARK THIS FRAME
                            233 ;        LD      (0x3C3F),A      ; MARK THIS FRAME
                            234 ;        LD      (0x3FC0),A      ; MARK THIS FRAME
                            235 ;        LD      (0x3FFF),A      ; MARK THIS FRAME
                            236 
   5432 7E            [ 7]  237         LD      A,(HL)          ; read number of lines
   5433 23            [ 6]  238         INC     HL
   5434 32 08 53      [13]  239         LD      (NLINES),A 
                            240 
   5437 47            [ 4]  241         LD      B,A
   5438                     242 NLINE:
   5438 CD AC 54      [17]  243         CALL    DOLINE
   543B 10 FB         [13]  244         DJNZ    NLINE
                            245         
                            246 ;       Save a Frame to RAMBO
                            247 
   543D                     248 SAVFRM:
   543D E5            [11]  249         PUSH    HL
   543E C5            [11]  250         PUSH    BC
   543F 21 00 3C      [10]  251         LD      HL,0x3C00
   5442 0E D1         [ 7]  252         LD      C,0xD1
   5444 06 00         [ 7]  253         LD      B,0x00
   5446 ED B3         [21]  254         OTIR    
   5448 ED B3         [21]  255         OTIR    
   544A ED B3         [21]  256         OTIR    
   544C ED B3         [21]  257         OTIR    
   544E C1            [10]  258         POP     BC
   544F E1            [10]  259         POP     HL
                            260 
   5450 CD 18 53      [17]  261         CALL    CLS
                            262 
   5453 18 D7         [12]  263         JR      NFRAME
                            264 
                            265 ;       TBD - Run animation
                            266         
   5455                     267 ANIMATE:
   5455 3A 05 53      [13]  268         LD      A,(SIDE)
   5458 FE 01         [ 7]  269         CP      0x01
   545A 20 07         [12]  270         JR      NZ,LFIRST
                            271 
   545C 3E AA         [ 7]  272         LD      A,0xAA
   545E 32 0D 53      [13]  273         LD      (BUF),A
   5461 18 05         [12]  274         JR      READRBO
                            275 
   5463                     276 LFIRST:
   5463 3E 55         [ 7]  277         LD      A,0x55
   5465 32 0D 53      [13]  278         LD      (BUF),A
                            279 
   5468                     280 READRBO:
   5468 3E 20         [ 7]  281         LD      A,0x20     ; Inc on Read, Address 0x000000
   546A 0E D0         [ 7]  282         LD      C,0xD0
   546C ED 79         [12]  283         OUT     (C),A 
   546E 3E 00         [ 7]  284         LD      A,0x00 
   5470 0E D2         [ 7]  285         LD      C,0xD2
   5472 ED 79         [12]  286         OUT     (C),A 
   5474 0E D3         [ 7]  287         LD      C,0xD3
   5476 ED 79         [12]  288         OUT     (C),A
                            289       
   5478 ED 5B 06 53   [20]  290         LD      DE,(NFRAMES)    ; Frame Counter
                            291 
   547C                     292 LODFRM:
                            293         ; get ready for next frame
   547C 06 00         [ 7]  294         LD      B,0
   547E 0E D1         [ 7]  295         LD      C,0xD1
   5480 21 00 3C      [10]  296         LD      HL,0x3C00
   5483 3A 0D 53      [13]  297         LD      A,(BUF)
   5486 0F            [ 4]  298         RRCA 
   5487 32 0D 53      [13]  299         LD      (BUF),A
                            300 
                            301         ; wait for end of vblank
                            302         ; (VDRV goes from 1->0)
   548A DB FF         [11]  303 LOOP3:  IN      A,(0xFF)
   548C CB 77         [ 8]  304         BIT     6,A
   548E C2 8A 54      [10]  305         JP      NZ,LOOP3
                            306 
                            307         ; wait for start of vblank
                            308         ; (VDRV goes from 0->1)
   5491 DB FF         [11]  309 LOOP4:  IN      A,(0xFF)
   5493 CB 77         [ 8]  310         BIT     6,A
   5495 CA 91 54      [10]  311         JP      Z,LOOP4
                            312 
                            313         ; switch to next frame
   5498 3A 0D 53      [13]  314         LD      A,(BUF)
                            315 ;        AND     0x03
   549B D3 FF         [11]  316         OUT     (0xFF),A
                            317 
                            318         ; transfer 1K from RAMBO to screen
                            319         ; HL, Band C are set already
   549D ED B2         [21]  320         INIR
   549F ED B2         [21]  321         INIR
   54A1 ED B2         [21]  322         INIR
   54A3 ED B2         [21]  323         INIR
                            324 
   54A5 1B            [ 6]  325         DEC     DE
   54A6 7A            [ 4]  326         LD      A,D 
   54A7 B3            [ 4]  327         OR      E
   54A8 20 D2         [12]  328         JR      NZ,LODFRM
                            329 
   54AA 18 BC         [12]  330         JR      READRBO
                            331 
                            332 ;       draw one line on the screen
   54AC                     333 DOLINE:
   54AC 7E            [ 7]  334         LD      A,(HL)
   54AD 23            [ 6]  335         INC     HL
   54AE 32 09 53      [13]  336         LD      (X1),A
                            337 
   54B1 7E            [ 7]  338         LD      A,(HL)
   54B2 23            [ 6]  339         INC     HL
   54B3 32 0A 53      [13]  340         LD      (Y1),A
                            341 
   54B6 7E            [ 7]  342         LD      A,(HL)
   54B7 23            [ 6]  343         INC     HL
   54B8 32 0B 53      [13]  344         LD      (X2),A
                            345 
   54BB 7E            [ 7]  346         LD      A,(HL)
   54BC 23            [ 6]  347         INC     HL
   54BD 32 0C 53      [13]  348         LD      (Y2),A
                            349 
                            350 ;       draw a line on the screen
                            351 
                            352 ;       for now, we will draw the end points first
                            353 ;        PUSH    HL
                            354 ;        LD      HL,#X1
                            355 ;        CALL    FSETGR
                            356 ;        LD      HL,#X2
                            357 ;        CALL    FSETGR
                            358 ;        POP     HL
                            359 
   54C0 CD C4 54      [17]  360         CALL    BRES 
                            361 
   54C3 C9            [10]  362         RET
                            363 
                            364 ; Bresenham line drawing algorithm
                            365 
   54C4                     366 BRES:
   54C4 F5            [11]  367         PUSH    AF
   54C5 C5            [11]  368         PUSH    BC
   54C6 D5            [11]  369         PUSH    DE
   54C7 E5            [11]  370         PUSH    HL
   54C8 DD E5         [15]  371         PUSH    IX
                            372 
   54CA 21 09 53      [10]  373         LD      HL,#X1
   54CD E5            [11]  374         PUSH    HL
   54CE DD E1         [14]  375         POP     IX
                            376 
   54D0 DD 7E 02      [19]  377         LD      A,(IX+2)   ; X2
   54D3 DD BE 00      [19]  378         CP      (IX+0)     ; X2-X1
   54D6 38 0F         [12]  379         JR      C,$L3      ; if X2-X1 <= 0, Jump
   54D8 28 0D         [12]  380         JR      Z,$L3
   54DA 3E 01         [ 7]  381         LD      A,0x01
   54DC 32 0E 53      [13]  382         LD      (SX),A     ; SX = 1
   54DF DD 7E 02      [19]  383         LD      A,(IX+2)
   54E2 DD 96 00      [19]  384         SUB     (IX+0)     ; A = X2-X1
   54E5 18 0B         [12]  385         JR      $L4
   54E7 3E FF         [ 7]  386 $L3:    LD      A,0xff     ; SX = -1
   54E9 32 0E 53      [13]  387         LD      (SX),A
   54EC DD 7E 00      [19]  388         LD      A,(IX+0)
   54EF DD 96 02      [19]  389         SUB     (IX+2)
   54F2 32 10 53      [13]  390 $L4:    LD      (DX),A     ; DX = ABS(X2-X1)
   54F5 3E 00         [ 7]  391         LD      A,0x00
   54F7 32 11 53      [13]  392         LD      (DX+1),A   ; DX is sign extended
                            393 
   54FA DD 7E 03      [19]  394         LD      A,(IX+3)   ; Y2
   54FD DD BE 01      [19]  395         CP      (IX+1)     ; Y2-Y1
   5500 38 0F         [12]  396         JR      C,$L5      ; if Y2-Y1 <= 0, Jump
   5502 28 0D         [12]  397         JR      Z,$L5
   5504 3E 01         [ 7]  398         LD      A,0x01
   5506 32 0F 53      [13]  399         LD      (SY),A     ; SY = 1
   5509 DD 7E 03      [19]  400         LD      A,(IX+3)
   550C DD 96 01      [19]  401         SUB     (IX+1)     ; A = Y2-Y1
   550F 18 0B         [12]  402         JR      $L6
   5511 3E FF         [ 7]  403 $L5:    LD      A,0xff     ; SY = -1
   5513 32 0F 53      [13]  404         LD      (SY),A
   5516 DD 7E 01      [19]  405         LD      A,(IX+1)
   5519 DD 96 03      [19]  406         SUB     (IX+3)
   551C ED 44         [ 8]  407 $L6:    NEG
   551E 32 12 53      [13]  408         LD      (DY),A     ; DY = -ABS(Y2-Y1)
   5521 3E FF         [ 7]  409         LD      A,0xff
   5523 32 13 53      [13]  410         LD      (DY+1),A   ; DY is sign-extended
                            411 
   5526 2A 10 53      [16]  412         LD      HL,(DX)
   5529 ED 5B 12 53   [20]  413         LD      DE,(DY)
   552D 19            [11]  414         ADD     HL,DE
   552E 22 14 53      [16]  415         LD      (ERR),HL   ; ERR = DX + DY
                            416 
   5531                     417 PNEXT:
   5531 E5            [11]  418         PUSH    HL         ; Draw pixel
   5532 21 09 53      [10]  419         LD      HL,#X1
   5535 CD 2B 53      [17]  420         CALL    FSETGR
   5538 E1            [10]  421         POP     HL
                            422         
   5539 DD 7E 00      [19]  423         LD      A,(IX+0)    ; Am I done?
   553C DD BE 02      [19]  424         CP      (IX+2)
   553F 20 08         [12]  425         JR      NZ,$CONT 
   5541 DD 7E 01      [19]  426         LD      A,(IX+1)
   5544 DD BE 03      [19]  427         CP      (IX+3)
   5547 28 57         [12]  428         JR      Z,$EXIT 
   5549                     429 $CONT: 
   5549 2A 14 53      [16]  430         LD      HL,(ERR)
   554C CB 25         [ 8]  431         SLA     L 
   554E CB 14         [ 8]  432         RL      H          
   5550 22 16 53      [16]  433         LD      (E2),HL     ; E2 = ERR*2
                            434 
   5553 37            [ 4]  435         SCF
   5554 3F            [ 4]  436         CCF 
   5555 2A 16 53      [16]  437         LD      HL,(E2)
   5558 ED 5B 12 53   [20]  438         LD      DE,(DY)
   555C ED 52         [15]  439         SBC     HL,DE
   555E CB 7C         [ 8]  440         BIT     7,H 
   5560 20 16         [12]  441         JR      NZ,$L7      ; IF E2 < DY, jump 
   5562 2A 14 53      [16]  442         LD      HL,(ERR)
   5565 ED 5B 12 53   [20]  443         LD      DE,(DY) 
   5569 19            [11]  444         ADD     HL,DE 
   556A 22 14 53      [16]  445         LD      (ERR),HL    ; ERR += DY
   556D 3A 09 53      [13]  446         LD      A,(X1)
   5570 47            [ 4]  447         LD      B,A
   5571 3A 0E 53      [13]  448         LD      A,(SX)
   5574 80            [ 4]  449         ADD     A,B
   5575 32 09 53      [13]  450         LD      (X1),A      ; X1 += SX
                            451 
   5578                     452 $L7:
   5578 37            [ 4]  453         SCF
   5579 3F            [ 4]  454         CCF 
   557A 2A 10 53      [16]  455         LD      HL,(DX)
   557D ED 5B 16 53   [20]  456         LD      DE,(E2)
   5581 ED 52         [15]  457         SBC     HL,DE
   5583 CB 7C         [ 8]  458         BIT     7,H
   5585 20 16         [12]  459         JR      NZ,$L8      ; IF E2 > DX, jump 
   5587 2A 14 53      [16]  460         LD      HL,(ERR)
   558A ED 5B 10 53   [20]  461         LD      DE,(DX) 
   558E 19            [11]  462         ADD     HL,DE 
   558F 22 14 53      [16]  463         LD      (ERR),HL    ; ERR += DX
   5592 3A 0A 53      [13]  464         LD      A,(Y1)
   5595 47            [ 4]  465         LD      B,A
   5596 3A 0F 53      [13]  466         LD      A,(SY)
   5599 80            [ 4]  467         ADD     A,B
   559A 32 0A 53      [13]  468         LD      (Y1),A      ; Y1 += SY
   559D                     469 $L8:
   559D C3 31 55      [10]  470         JP      PNEXT
                            471 
   55A0                     472 $EXIT:
   55A0 DD E1         [14]  473         POP     IX
   55A2 E1            [10]  474         POP     HL
   55A3 D1            [10]  475         POP     DE
   55A4 C1            [10]  476         POP     BC
   55A5 F1            [10]  477         POP     AF 
   55A6 C9            [10]  478         RET
                            479 
   55A7                     480 MOVIE:
                            481     ; MOVIE DATA GOES HERE
