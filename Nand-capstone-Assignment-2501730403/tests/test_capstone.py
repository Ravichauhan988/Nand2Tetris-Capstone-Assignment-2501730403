"""Automated verification tests for Hack Assembler and Box.hack (K = 03)."""

from pathlib import Path
import sys
import tempfile
import unittest

CAPSTONE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CAPSTONE_DIR))

import assembler  # noqa: E402


def run_hack_cpu(
    rom: list[str],
    cycles: int,
    kbd_value: int = 0,
    ram: dict[int, int] | None = None,
) -> tuple[dict[int, int], int, int, int]:
    """Minimal 16-bit Hack CPU/Memory simulator to verify assembled .hack binaries."""
    if ram is None:
        ram = {}
    ram[24576] = kbd_value
    a_reg = 0
    d_reg = 0
    pc = 0

    def to_signed(val: int) -> int:
        val &= 0xFFFF
        return val - 0x10000 if val & 0x8000 else val

    for _ in range(cycles):
        if pc < 0 or pc >= len(rom):
            break
        instr = rom[pc]
        if instr[0] == "0":
            a_reg = int(instr[1:], 2)
            pc += 1
            continue

        # C-instruction: 111 a c1c2c3c4c5c6 d1d2d3 j1j2j3
        a_bit = instr[3]
        c_bits = instr[4:10]
        d_bits = instr[10:13]
        j_bits = instr[13:16]

        x = d_reg
        y = ram.get(a_reg, 0) if a_bit == "1" else a_reg
        sx, sy = to_signed(x), to_signed(y)

        alu_map = {
            "101010": 0,
            "111111": 1,
            "111010": -1,
            "001100": sx,
            "110000": sy,
            "001101": ~sx,
            "110001": ~sy,
            "001111": -sx,
            "110011": -sy,
            "011111": sx + 1,
            "110111": sy + 1,
            "001110": sx - 1,
            "110010": sy - 1,
            "000010": sx + sy,
            "010011": sx - sy,
            "000111": sy - sx,
            "000000": sx & sy,
            "010101": sx | sy,
        }
        out = alu_map[c_bits] & 0xFFFF
        sout = to_signed(out)

        old_a = a_reg
        if d_bits[2] == "1":  # M
            ram[old_a] = out
        if d_bits[1] == "1":  # D
            d_reg = out
        if d_bits[0] == "1":  # A
            a_reg = out

        jump = (
            (j_bits[0] == "1" and sout < 0)
            or (j_bits[1] == "1" and sout == 0)
            or (j_bits[2] == "1" and sout > 0)
        )
        pc = old_a if jump else pc + 1

    return ram, a_reg, d_reg, pc


class TestAssemblerAndBox(unittest.TestCase):
    def test_official_programs_match_expected(self) -> None:
        programs_dir = CAPSTONE_DIR / "programs"
        expected_dir = CAPSTONE_DIR / "tests" / "expected"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            for name in ("Add", "Max", "Rect"):
                out_hack = tmp / f"{name}.hack"
                sym_file = tmp / f"{name}_symbols.txt"
                assembler.assemble_file(programs_dir / f"{name}.asm", out_hack, sym_file)

                actual = out_hack.read_text(encoding="utf-8").splitlines()
                expected = (expected_dir / f"{name}.hack").read_text(encoding="utf-8").splitlines()
                self.assertEqual(actual, expected, f"Mismatch in {name}.hack")

    def test_symbols_txt_records_labels_and_variables(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            out_hack = tmp / "Box.hack"
            sym_file = tmp / "symbols.txt"
            assembler.assemble_file(CAPSTONE_DIR / "Box.asm", out_hack, sym_file)

            text = sym_file.read_text(encoding="utf-8")
            for expected_entry in (
                "MAIN_LOOP = 0",
                "KEY_PRESSED = 8",
                "DRAW_BOX = 10",
                "ROW_LOOP = 20",
                "COL_LOOP = 28",
                "color = 16",
                "rowPtr = 17",
                "rowCount = 18",
                "colPtr = 19",
                "wordCount = 20",
            ):
                self.assertIn(expected_entry, text)

    def test_box_hack_draws_and_erases_for_k03(self) -> None:
        # Re-assemble Box.asm freshly to ensure Box.hack is in sync
        out_hack, _, _ = assembler.assemble_file(
            CAPSTONE_DIR / "Box.asm",
            CAPSTONE_DIR / "Box.hack",
            CAPSTONE_DIR / "symbols.txt",
        )
        rom = out_hack.read_text(encoding="utf-8").splitlines()
        ram: dict[int, int] = {}

        # Step 1: Key released initially -> box area should stay 0
        ram, _, _, _ = run_hack_cpu(rom, cycles=2000, kbd_value=0, ram=ram)
        for r in range(3, 23):
            for c in range(4):
                self.assertEqual(ram.get(16384 + 32 * r + c, 0), 0)

        # Step 2: Key pressed (ASCII 'A' = 65) -> 20 rows (3..22), 4 words/row (64 px) black (0xFFFF)
        ram, _, _, _ = run_hack_cpu(rom, cycles=3000, kbd_value=65, ram=ram)
        expected_box_addrs = {
            16384 + 32 * r + c for r in range(3, 23) for c in range(4)
        }
        for addr in expected_box_addrs:
            self.assertEqual(ram.get(addr, 0), 0xFFFF, f"Screen word {addr} not black")

        # Verify boundary pixels outside box were NOT modified
        self.assertEqual(ram.get(16384 + 32 * 2, 0), 0)      # Row 2 (above box)
        self.assertEqual(ram.get(16384 + 32 * 23, 0), 0)     # Row 23 (below box)
        self.assertEqual(ram.get(16384 + 32 * 3 + 4, 0), 0)  # Col 4 (right of 64px box)

        # Step 3: Key released -> box erased back to 0
        ram, _, _, _ = run_hack_cpu(rom, cycles=3000, kbd_value=0, ram=ram)
        for addr in expected_box_addrs:
            self.assertEqual(ram.get(addr, 0), 0, f"Screen word {addr} not cleared")


if __name__ == "__main__":
    unittest.main()
