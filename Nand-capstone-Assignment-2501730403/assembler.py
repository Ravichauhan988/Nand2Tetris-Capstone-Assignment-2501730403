"""Two-pass Hack Assembler for Nand2Tetris Capstone Project.

Student: Ravi Chauhan
Roll No: 2501730403
Personal Number (K): 03
Additional Feature (K mod 3 == 0): Save all labels and variables with their
addresses in "symbols.txt".
"""

from __future__ import annotations

import argparse
from pathlib import Path

# Predefined Hack symbols (RAM addresses 0-15, pointers, and I/O devices)
PREDEFINED_SYMBOLS: dict[str, int] = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    **{f"R{i}": i for i in range(16)},
}

# C-instruction lookup tables: comp -> (a-bit, c1..c6)
COMP_TABLE: dict[str, tuple[str, str]] = {
    "0": ("0", "101010"),
    "1": ("0", "111111"),
    "-1": ("0", "111010"),
    "D": ("0", "001100"),
    "A": ("0", "110000"),
    "!D": ("0", "001101"),
    "!A": ("0", "110001"),
    "-D": ("0", "001111"),
    "-A": ("0", "110011"),
    "D+1": ("0", "011111"),
    "A+1": ("0", "110111"),
    "D-1": ("0", "001110"),
    "A-1": ("0", "110010"),
    "D+A": ("0", "000010"),
    "D-A": ("0", "010011"),
    "A-D": ("0", "000111"),
    "D&A": ("0", "000000"),
    "D|A": ("0", "010101"),
    "M": ("1", "110000"),
    "!M": ("1", "110001"),
    "-M": ("1", "110011"),
    "M+1": ("1", "110111"),
    "M-1": ("1", "110010"),
    "D+M": ("1", "000010"),
    "D-M": ("1", "010011"),
    "M-D": ("1", "000111"),
    "D&M": ("1", "000000"),
    "D|M": ("1", "010101"),
}

DEST_TABLE: dict[str, str] = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

JUMP_TABLE: dict[str, str] = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


def strip_comment_and_whitespace(raw_line: str) -> str:
    """Remove inline '//' comments and all whitespace from a source line."""
    without_comment = raw_line.split("//", 1)[0]
    return "".join(without_comment.split())


def first_pass(lines: list[str]) -> tuple[dict[str, int], dict[str, int]]:
    """Scan lines to record label (LABEL) ROM addresses in the symbol table."""
    symbol_table = dict(PREDEFINED_SYMBOLS)
    labels: dict[str, int] = {}
    rom_address = 0

    for line in lines:
        cleaned = strip_comment_and_whitespace(line)
        if not cleaned:
            continue

        if cleaned.startswith("(") and cleaned.endswith(")"):
            label_name = cleaned[1:-1]
            if not label_name:
                raise ValueError("Empty label declaration '()' encountered.")
            if label_name not in symbol_table:
                symbol_table[label_name] = rom_address
                labels[label_name] = rom_address
        else:
            rom_address += 1

    return symbol_table, labels


def encode_a_instruction(
    symbol: str,
    symbol_table: dict[str, int],
    variables: dict[str, int],
    next_ram_address: int,
) -> tuple[str, int]:
    """Encode an A-instruction (@value or @symbol) into 16-bit binary."""
    if symbol.isdigit():
        value = int(symbol)
        if not (0 <= value <= 32767):
            raise ValueError(f"A-instruction constant out of 15-bit range: @{symbol}")
    else:
        if symbol not in symbol_table:
            symbol_table[symbol] = next_ram_address
            variables[symbol] = next_ram_address
            next_ram_address += 1
        value = symbol_table[symbol]

    return f"0{value:015b}", next_ram_address


def encode_c_instruction(instruction: str) -> str:
    """Encode a C-instruction (dest=comp;jump) into 16-bit binary."""
    dest = ""
    jump = ""
    rest = instruction

    if "=" in rest:
        dest, rest = rest.split("=", 1)
    if ";" in rest:
        comp, jump = rest.split(";", 1)
    else:
        comp = rest

    if comp not in COMP_TABLE:
        raise ValueError(f"Invalid comp mnemonic: '{comp}' in '{instruction}'")
    if dest not in DEST_TABLE:
        raise ValueError(f"Invalid dest mnemonic: '{dest}' in '{instruction}'")
    if jump not in JUMP_TABLE:
        raise ValueError(f"Invalid jump mnemonic: '{jump}' in '{instruction}'")

    a_bit, c_bits = COMP_TABLE[comp]
    return f"111{a_bit}{c_bits}{DEST_TABLE[dest]}{JUMP_TABLE[jump]}"


def second_pass(
    lines: list[str],
    symbol_table: dict[str, int],
) -> tuple[list[str], dict[str, int]]:
    """Translate A- and C-instructions to binary and allocate RAM variables from 16."""
    machine_code: list[str] = []
    variables: dict[str, int] = {}
    next_ram_address = 16

    for line in lines:
        cleaned = strip_comment_and_whitespace(line)
        if not cleaned or (cleaned.startswith("(") and cleaned.endswith(")")):
            continue

        if cleaned.startswith("@"):
            binary, next_ram_address = encode_a_instruction(
                cleaned[1:], symbol_table, variables, next_ram_address
            )
        else:
            binary = encode_c_instruction(cleaned)

        machine_code.append(binary)

    return machine_code, variables


def write_symbols_file(
    symbols_path: Path,
    labels: dict[str, int],
    variables: dict[str, int],
) -> None:
    """Save all labels and variables with their addresses to symbols.txt (K mod 3 == 0)."""
    lines = [
        "# Hack Assembler Symbol Table (K = 03, K mod 3 = 0)",
        "",
        "[LABELS - ROM Addresses]",
    ]
    if labels:
        for name, addr in labels.items():
            lines.append(f"{name} = {addr}")
    else:
        lines.append("(none)")

    lines.extend(["", "[VARIABLES - RAM Addresses starting at 16]"])
    if variables:
        for name, addr in variables.items():
            lines.append(f"{name} = {addr}")
    else:
        lines.append("(none)")

    symbols_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def assemble_file(
    asm_path: Path,
    hack_path: Path | None = None,
    symbols_path: Path | None = None,
) -> tuple[Path, Path, int]:
    """Assemble a .asm file into a .hack file and write symbols.txt."""
    if hack_path is None:
        hack_path = asm_path.with_suffix(".hack")
    if symbols_path is None:
        symbols_path = Path("symbols.txt")

    source_lines = asm_path.read_text(encoding="utf-8").splitlines()

    # Pass 1: build label mappings
    symbol_table, labels = first_pass(source_lines)

    # Pass 2: convert instructions and allocate variables
    binary_instructions, variables = second_pass(source_lines, symbol_table)

    hack_content = "\n".join(binary_instructions) + ("\n" if binary_instructions else "")
    hack_path.write_text(hack_content, encoding="utf-8")
    write_symbols_file(symbols_path, labels, variables)

    return hack_path, symbols_path, len(binary_instructions)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Two-pass Hack Assembler (writes .hack and symbols.txt)."
    )
    parser.add_argument("input_asm", type=Path, help="Path to input .asm file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Optional output .hack file path (defaults to <input>.hack)",
    )
    parser.add_argument(
        "--symbols",
        type=Path,
        default=Path("symbols.txt"),
        help="Path to save labels and variables (default: symbols.txt)",
    )
    args = parser.parse_args()

    out_path, sym_path, count = assemble_file(args.input_asm, args.output, args.symbols)
    print(f"Assembled {count} instructions -> {out_path}")
    print(f"Saved labels and variables -> {sym_path}")


if __name__ == "__main__":
    main()
