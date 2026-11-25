// Box.asm - Nand2Tetris Capstone Project (Part C)
// Student: Ravi Chauhan | Roll No: 2501730403 | K = 03
//
// Specifications for K = 3:
//   - Starting row  = K = 3  -> Screen offset = 32 * 3 = 96 (SCREEN + 96 = 16480)
//   - Box height    = 20 rows (rows 3 to 22)
//   - Box width     = 16 * ((3 mod 4) + 1) = 64 pixels (4 words per row, left edge)
//   - Behaviour     = Draw black box (-1) while any key is pressed; erase (0) on release.

(MAIN_LOOP)
    @KBD
    D=M             // Read keyboard register (0 when no key is pressed)
    @KEY_PRESSED
    D;JNE           // Jump if any key is currently pressed

    @color
    M=0             // No key pressed -> erase box (white = 0)
    @DRAW_BOX
    0;JMP

(KEY_PRESSED)
    @color
    M=-1            // Key pressed -> draw box (black = -1, all 16 bits = 1)

(DRAW_BOX)
    // Start at SCREEN (16384) + 32 * K = 16384 + 96 = 16480 (row 3, left edge)
    @SCREEN
    D=A
    @96
    D=D+A
    @rowPtr
    M=D             // rowPtr points to the first word of the current row

    @20
    D=A
    @rowCount
    M=D             // rowCount counts down 20 rows

(ROW_LOOP)
    @rowPtr
    D=M
    @colPtr
    M=D             // colPtr starts at the left edge of the current row

    @4
    D=A
    @wordCount
    M=D             // wordCount = 4 words per row (4 * 16 = 64 pixels wide)

(COL_LOOP)
    @color
    D=M             // Load fill value (-1 or 0)
    @colPtr
    A=M
    M=D             // Write 16 pixels to Screen memory

    @colPtr
    M=M+1           // Advance to next 16-pixel word in this row

    @wordCount
    MD=M-1
    @COL_LOOP
    D;JGT           // Continue until all 4 words in the row are written

    // Move rowPtr down by 1 screen row (32 words per row)
    @32
    D=A
    @rowPtr
    M=D+M

    @rowCount
    MD=M-1
    @ROW_LOOP
    D;JGT           // Continue until all 20 rows are processed

    @MAIN_LOOP
    0;JMP           // Poll keyboard continuously
