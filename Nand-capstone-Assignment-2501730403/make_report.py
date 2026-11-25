import base64, os, sys

def b64img(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

mem_img = b64img(r'C:\Users\ravi\Downloads\capstone\screenshots\PartA_Memory_SyntaxOK.png')
box_img = b64img(r'C:\Users\ravi\Downloads\capstone\screenshots\PartC_Box_Working.png')

css = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; font-size: 12pt; color: #1a1a1a; background:#fff; padding:20px; max-width:900px; margin:auto; }
h1 { font-size:20pt; color:#1a237e; border-bottom:3px solid #1a237e; padding-bottom:8px; margin-bottom:10px; }
h2 { font-size:14pt; color:#283593; border-left:4px solid #3949ab; padding-left:10px; margin:22px 0 10px; }
h3 { font-size:12pt; color:#3949ab; margin:14px 0 6px; }
.cover { text-align:center; padding:40px 0 30px; border-bottom:2px solid #ccc; margin-bottom:22px; }
.cover h1 { border:none; font-size:24pt; }
.cover .sub { font-size:12pt; color:#555; margin:5px 0; }
table.info { width:100%; border-collapse:collapse; margin:10px 0 18px; }
table.info td { border:1px solid #bbb; padding:7px 12px; }
table.info td:first-child { font-weight:bold; background:#e8eaf6; width:38%; }
table.data { width:100%; border-collapse:collapse; margin:10px 0 16px; }
table.data th { background:#3949ab; color:#fff; padding:7px 10px; text-align:left; }
table.data td { border:1px solid #bbb; padding:6px 10px; }
table.data tr:nth-child(even) td { background:#f5f5f5; }
code { font-family:Consolas,monospace; background:#f1f3f9; border:1px solid #c5cae9; border-radius:3px; padding:1px 5px; font-size:10.5pt; }
pre { font-family:Consolas,monospace; background:#f1f3f9; border:1px solid #c5cae9; border-radius:4px; padding:10px 14px; font-size:10pt; white-space:pre-wrap; margin:8px 0 14px; line-height:1.5; }
.sc { text-align:center; margin:14px 0; }
.sc img { max-width:92%; border:2px solid #3949ab; border-radius:6px; box-shadow:0 2px 10px rgba(0,0,0,.15); }
.sc p { font-size:10pt; color:#555; margin-top:5px; font-style:italic; }
.badge { display:inline-block; padding:2px 10px; border-radius:12px; font-size:10pt; font-weight:bold; }
.pass { background:#c8e6c9; color:#1b5e20; }
.ok { background:#e3f2fd; color:#0d47a1; }
.ph { background:#fff8e1; border:2px dashed #f9a825; padding:14px; border-radius:6px; margin:10px 0; font-size:10.5pt; color:#5d4037; }
.box { background:#e8eaf6; border-left:4px solid #3949ab; padding:10px 14px; margin:10px 0; border-radius:0 6px 6px 0; }
p { line-height:1.65; margin:6px 0 10px; }
ul,ol { margin:6px 0 10px 22px; line-height:1.65; }
@media print {
  body { padding:0; }
  .ph { border:1px dashed #aaa; }
}
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Capstone Report - Ravi Chauhan (2501730403)</title>
<style>{css}</style>
</head>
<body>

<div class="cover">
  <div class="sub">School of Engineering &amp; Technology &mdash; K.R. Mangalam University</div>
  <div class="sub">Course: Nand to Tetris &ndash; I (ETCNTC301) &nbsp;|&nbsp; Marks: 10 &nbsp;|&nbsp; Individual Project</div>
  <br/>
  <h1>Capstone Project: Make the Computer Draw a Box</h1>
  <br/>
  <div class="sub"><strong>Submitted by:</strong> Ravi Chauhan</div>
  <div class="sub"><strong>University Roll Number:</strong> 2501730403</div>
  <div class="sub"><strong>Personal Number (K):</strong> 03</div>
  <div class="sub"><strong>Date:</strong> November 2026</div>
</div>

<h2>1. Personal Number (K)</h2>
<table class="info">
  <tr><td>University Roll Number</td><td>2501730403</td></tr>
  <tr><td>Personal Number K (last 2 digits)</td><td><strong>03</strong></td></tr>
  <tr><td>K mod 3 &rarr; Assembler Feature</td><td>0 &rarr; Save labels + variables in <code>symbols.txt</code></td></tr>
  <tr><td>K mod 4 &rarr; Box Width</td><td>3 &rarr; 16 &times; (3+1) = <strong>64 pixels</strong> wide (4 words per row)</td></tr>
  <tr><td>Box Starting Row</td><td>K = 3 &rarr; Screen address = SCREEN + 32&times;3 = <strong>16480</strong></td></tr>
  <tr><td>Box Height</td><td><strong>20 rows</strong> (rows 3 to 22)</td></tr>
</table>

<h2>2. Part A &ndash; Hack Computer (HDL)</h2>

<h3>2.1 Memory.hdl</h3>
<p><code>Memory.hdl</code> unifies RAM and memory-mapped I/O into a single 15-bit address space using the top two address bits (<code>address[13..14]</code>):</p>
<ul>
  <li><code>00</code>/<code>01</code> &rarr; <strong>RAM16K</strong> (0x0000&ndash;0x3FFF, main data memory)</li>
  <li><code>10</code> &rarr; <strong>Screen</strong> (0x4000&ndash;0x5FFF, 512&times;256 pixel I/O)</li>
  <li><code>11</code> &rarr; <strong>Keyboard</strong> (0x6000, read-only 16-bit key code)</li>
</ul>
<p>A <code>DMux4Way</code> routes the <code>load</code> signal to the correct chip; a <code>Mux4Way16</code> selects the correct output word.</p>
<pre>CHIP Memory {{
    IN in[16], load, address[15];
    OUT out[16];
    PARTS:
    DMux4Way(in=load, sel=address[13..14], a=loadRamLow, b=loadRamHigh, c=loadScreen, d=unusedKbdLoad);
    Or(a=loadRamLow, b=loadRamHigh, out=loadRam);
    RAM16K(in=in, load=loadRam, address=address[0..13], out=ramOut);
    Screen(in=in, load=loadScreen, address=address[0..12], out=screenOut);
    Keyboard(out=kbdOut);
    Mux4Way16(a=ramOut, b=ramOut, c=screenOut, d=kbdOut, sel=address[13..14], out=out);
}}</pre>

<div class="sc">
  <img src="data:image/png;base64,{mem_img}" alt="Memory.hdl in Web IDE - No syntax errors"/>
  <p>Figure 1: Memory.hdl loaded in Nand2Tetris Web IDE &mdash; <span class="badge ok">HDL code: No syntax errors</span> | Memory.tst loaded with all pins visible</p>
</div>

<div class="ph">
  <strong>&#128247; Screenshot required &mdash; Memory.tst full run</strong><br/>
  Open the Nand2Tetris Hardware Simulator or Web IDE (Project 05, chip Memory), paste Memory.hdl, run Memory.tst at ~60% speed. When the status bar shows <em>"Comparison ended successfully"</em>, take a screenshot (Win+Shift+S) and insert it here (or paste into the report).
</div>

<h3>2.2 CPU.hdl</h3>
<p>The CPU decodes <code>instruction[15]</code>: 0 = A-instruction (load constant into A); 1 = C-instruction (ALU operation). Key design decisions:</p>
<ul>
  <li><strong>A-register:</strong> loads raw instruction on A-instr; ALU output on C-instr when d1=1. Its low 15 bits = <code>addressM</code>.</li>
  <li><strong>D-register:</strong> loads ALU output when d2 (<code>instruction[4]</code>) = 1 on a C-instr.</li>
  <li><strong>ALU:</strong> x=D, y = A or inM (selected by <code>instruction[12]</code>), control = <code>instruction[11..6]</code>. Produces <code>outM</code>, <code>zr</code>, <code>ng</code>.</li>
  <li><strong>PC:</strong> loads A-reg value (jump) if the jump-bit condition matches <code>ng</code>/<code>zr</code>/<code>positive</code>; otherwise increments.</li>
  <li><strong>writeM</strong> = <code>instruction[15] AND instruction[3]</code>.</li>
</ul>

<div class="ph">
  <strong>&#128247; Screenshot required &mdash; CPU.tst full run</strong><br/>
  Switch to chip CPU in the simulator, paste CPU.hdl, run CPU.tst. Insert the "Comparison ended successfully" screenshot here.
</div>

<h3>2.3 Computer.hdl</h3>
<p><code>Computer.hdl</code> connects ROM32K, CPU, and Memory at the top level:</p>
<pre>CHIP Computer {{
    IN reset;
    PARTS:
    ROM32K(address=pc, out=instruction);
    CPU(inM=memOut, instruction=instruction, reset=reset,
        outM=outM, writeM=writeM, addressM=addressM, pc=pc);
    Memory(in=outM, load=writeM, address=addressM, out=memOut);
}}</pre>

<div class="ph">
  <strong>&#128247; Screenshot required &mdash; Computer.tst full run</strong><br/>
  Switch to chip Computer, paste Computer.hdl, run ComputerAdd.tst / ComputerMax.tst / ComputerRect.tst. Insert the passing screenshot here.
</div>

<p><em>Note:</em> Built-in chips used: <code>RAM16K</code>, <code>Screen</code>, <code>Keyboard</code>, <code>ROM32K</code>, <code>ARegister</code>, <code>DRegister</code>, <code>ALU</code>, <code>PC</code>, and mux/demux chips.</p>

<h2>3. Part B &ndash; Two-Pass Python Assembler (assembler.py)</h2>

<h3>3.1 Pass 1 &mdash; Label Processing</h3>
<div class="box">
<ol>
  <li>Read every line; strip <code>//</code> comments and whitespace.</li>
  <li>If the cleaned line is <code>(LABEL)</code>, add it to the symbol table with the current ROM counter. <strong>Do not increment the counter</strong> (labels take no ROM space).</li>
  <li>Otherwise, increment ROM counter by 1.</li>
  <li>Predefined symbols (<code>R0&ndash;R15</code>, <code>SP</code>, <code>LCL</code>, <code>ARG</code>, <code>THIS</code>, <code>THAT</code>, <code>SCREEN=16384</code>, <code>KBD=24576</code>) are pre-loaded.</li>
</ol>
</div>

<h3>3.2 Pass 2 &mdash; Binary Conversion</h3>
<div class="box">
<ol>
  <li>Read instructions again (skip labels and blanks).</li>
  <li><strong>A-instruction</strong> (<code>@value</code>): number &rarr; <code>0</code> + 15-bit binary. Unknown symbol &rarr; assign next RAM address (starting at <strong>16</strong>).</li>
  <li><strong>C-instruction</strong> (<code>dest=comp;jump</code>): look up <code>comp</code> (a-bit + 6 c-bits), <code>dest</code> (3 d-bits), <code>jump</code> (3 j-bits). Output = <code>111 a cccccc ddd jjj</code>.</li>
</ol>
</div>

<h3>3.3 Additional Feature &mdash; K mod 3 = 0 (symbols.txt)</h3>
<p>All user-defined labels (ROM addresses) and variables (RAM addresses) are saved to <code>symbols.txt</code> after each assembly run. Example for Box.asm:</p>
<pre># Hack Assembler Symbol Table (K = 03, K mod 3 = 0)

[LABELS - ROM Addresses]
MAIN_LOOP = 0
KEY_PRESSED = 8
DRAW_BOX = 10
ROW_LOOP = 20
COL_LOOP = 28

[VARIABLES - RAM Addresses starting at 16]
color = 16
rowPtr = 17
rowCount = 18
colPtr = 19
wordCount = 20</pre>

<h3>3.4 Verification Results</h3>
<table class="data">
  <tr><th>Program</th><th>Instructions</th><th>Result</th></tr>
  <tr><td>Add.asm</td><td>6</td><td><span class="badge pass">&#10003; Exact match</span></td></tr>
  <tr><td>Max.asm</td><td>18</td><td><span class="badge pass">&#10003; Exact match</span></td></tr>
  <tr><td>Rect.asm</td><td>31</td><td><span class="badge pass">&#10003; Exact match</span></td></tr>
  <tr><td>Pong.asm</td><td>14</td><td><span class="badge ok">&#10003; Assembled cleanly</span></td></tr>
  <tr><td>Box.asm</td><td>49</td><td><span class="badge pass">&#10003; All 3 unit tests passed</span></td></tr>
</table>
<pre>Ran 3 tests in 0.068s
OK

test_box_hack_draws_and_erases_for_k03 ... ok
test_official_programs_match_expected ... ok
test_symbols_txt_records_labels_and_variables ... ok</pre>

<h2>4. Part C &ndash; Box Program (Box.asm)</h2>

<h3>4.1 Box Dimensions (K = 03)</h3>
<table class="info">
  <tr><td>Starting Row</td><td>K = <strong>3</strong></td></tr>
  <tr><td>Starting Screen Address</td><td>SCREEN + 32&times;3 = 16384 + 96 = <strong>16480</strong></td></tr>
  <tr><td>Box Height</td><td><strong>20 rows</strong> (rows 3 &ndash; 22)</td></tr>
  <tr><td>Words per Row</td><td>(K mod 4) + 1 = 3 + 1 = <strong>4 words</strong></td></tr>
  <tr><td>Box Width</td><td>16 &times; 4 = <strong>64 pixels</strong></td></tr>
</table>

<h3>4.2 Program Logic</h3>
<ul>
  <li><strong>MAIN_LOOP:</strong> Reads <code>RAM[24576]</code> (KBD). Key pressed &rarr; <code>color = -1</code> (black); no key &rarr; <code>color = 0</code> (white).</li>
  <li><strong>DRAW_BOX:</strong> Initialises <code>rowPtr = 16480</code>, <code>rowCount = 20</code>.</li>
  <li><strong>ROW_LOOP &rarr; COL_LOOP:</strong> Writes <code>color</code> into 4 consecutive words per row; advances <code>rowPtr</code> by 32 (one screen row) after each row.</li>
  <li>Loops back to <strong>MAIN_LOOP</strong> endlessly &rarr; real-time keyboard-controlled drawing.</li>
  <li><strong>Why &minus;1 = black:</strong> In 16-bit two's complement, -1 = <code>1111111111111111</code> &mdash; all 16 bits = 1 &rarr; all 16 pixels in the word are black.</li>
</ul>

<h3>4.3 Working Box Screenshot</h3>
<div class="sc">
  <img src="data:image/png;base64,{box_img}" alt="Box.hack running in CPU Emulator - black box at row 3"/>
  <p>Figure 2: Box.hack running in Nand2Tetris CPU Emulator &mdash; <span class="badge pass">64&times;20 black box at row 3 (key 'a' held, Steps: 3,077,133, PC:36, D:65535=&minus;1)</span></p>
</div>

<h2>5. One Mistake Encountered and Fixed</h2>
<div class="box">
<strong>The Error &mdash; PowerShell command on one line:</strong><br/><br/>
<code>cd C:\\Users\\ravi\\.gemini\\antigravity\\scratch\\capstone &nbsp; python assembler.py Box.asm</code><br/><br/>
<strong>Error message:</strong><br/>
<code>Set-Location : A positional parameter cannot be found that accepts argument 'python'.</code>
</div>
<p><strong>Cause:</strong> PowerShell's <code>cd</code> (alias for <code>Set-Location</code>) accepts only one argument &mdash; the path. Writing <code>python</code> and <code>Box.asm</code> after the path on the same line made PowerShell treat them as extra arguments to <code>cd</code> and throw a parameter error.</p>
<p><strong>Fix:</strong> Run the two commands on separate lines (or use a semicolon):</p>
<pre>cd C:\\Users\\ravi\\.gemini\\antigravity\\scratch\\capstone
python assembler.py Box.asm</pre>
<p><strong>Verification:</strong> After the fix, the assembler printed:</p>
<pre>Assembled 49 instructions -&gt; Box.hack
Saved labels and variables -&gt; symbols.txt</pre>
<p>All three unit tests also passed, confirming the fix was correct.</p>

<h2>6. Conclusion</h2>
<p>Building <code>Memory.hdl</code> clarified how RAM, screen, and keyboard are unified through one address bus using multiplexers. Writing <code>CPU.hdl</code> made it clear how a 16-bit instruction encodes both data-flow (which registers to read/write) and control-flow (which ALU operation, whether to jump) in a single word. Connecting them in <code>Computer.hdl</code> showed how a stored-program computer fetches and executes instructions in a continuous cycle.</p>
<p>Writing <code>assembler.py</code> in Python made binary instruction encoding concrete: the two-pass design first resolves all label addresses (enabling forward references), then encodes each instruction. The <code>symbols.txt</code> feature reinforced how the assembler tracks the boundary between ROM addresses (labels) and RAM addresses (variables from address 16 onward).</p>
<p>Writing <code>Box.asm</code> tied everything together: polling the keyboard memory-map at address 24576, writing &minus;1 or 0 to 80 specific screen-memory words (4 per row &times; 20 rows), and looping continuously produced a visually responsive, real-time drawing program entirely in assembly language &mdash; verified in both the Nand2Tetris CPU Emulator and an automated Python simulation of the Hack CPU.</p>

</body>
</html>"""

out = r'C:\Users\ravi\Downloads\capstone\Report_Ravi_Chauhan.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print("HTML report written:", len(html), "chars ->", out)
