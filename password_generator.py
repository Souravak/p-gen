#!/usr/bin/env python3
"""Generate password-like variations from a base text and optional phone number.

Writes results to `passwords.txt` by default. Supports `--base` and `--phone`
for non-interactive use (useful for testing).
"""
import argparse


def clean_phone(phone: str) -> str:
    return "".join(ch for ch in phone if ch.isdigit())


def generate_variations(base: str, phone: str | None = None, symbols: list | None = None) -> set:
    base = (base or "").strip()
    if not base:
        return set()

    suffix_numbers = [
        "1",
        "12",
        "123",
        "1234",
        "12345",
        "123456",
        "1234567",
        "007",
        "21",
        "2023",
        "987",
        "9876",
    ]
    # default symbols include empty (no symbol) plus common ones
    symbols = ["", "@", "_", "!", "#", "$"]
    if symbols is not None:
        # allow caller to override symbols; ensure empty string is present
        if "" not in symbols:
            symbols = [""] + symbols

    results: set = set()

    # Base + symbol + numeric suffixes
    for sym in symbols:
        for num in suffix_numbers:
            cand = f"{base}{sym}{num}"
            if len(cand) > 7:
                results.add(cand)

    # Common short patterns
    common = ["123", "1234", "2020", "2021", "2022", "2023", "!", "@", "_"]
    for c in common:
        cand = f"{base}{c}"
        if len(cand) > 7:
            results.add(cand)

    # Year combos
    years = [str(y) for y in range(1990, 2026)]
    for y in years:
        cand = f"{base}{y}"
        if len(cand) > 7:
            results.add(cand)

    # Combine with phone fragments if provided
    if phone:
        p = clean_phone(phone)
        if p:
            variants = {p, p[-4:], p[-3:], p[:3], p[:4]} if p else set()
            for v in variants:
                if not v:
                    continue
                for sym in symbols:
                    cand1 = f"{base}{sym}{v}"
                    cand2 = f"{v}{sym}{base}"
                    if len(cand1) > 7:
                        results.add(cand1)
                    if len(cand2) > 7:
                        results.add(cand2)

            # Mix suffix numbers and a short phone fragment
            for num in suffix_numbers:
                frag = p[-2:] if len(p) >= 2 else p
                for sym in symbols:
                    cand = f"{base}{sym}{num}{frag}"
                    if len(cand) > 7:
                        results.add(cand)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate password-like variations from text and optional phone."
    )
    parser.add_argument("--base", "-b", help="Base text (e.g., name). If omitted, will prompt.")
    parser.add_argument("--phone", "-p", help="Phone number (digits only, optional). If omitted, will prompt.")
    parser.add_argument("--out", "-o", help="Output file", default="passwords.txt")
    parser.add_argument("--symbols", "-s", help="Symbols to use (e.g. '@*&#'). Include without spaces to override defaults.")
    parser.add_argument("--include-prefixes", action="store_true", help="Also generate for short prefixes (first 3 chars, e.g. 'sou')")
    args = parser.parse_args()

    if args.base:
        base = args.base
    else:
        base = input("Enter base text (e.g., name): ").strip()

    if args.phone is not None:
        phone = args.phone
    else:
        phone = input("Enter phone number (optional, digits only): ").strip()

    # prepare symbols list if provided
    sym_list = None
    if args.symbols:
        # treat the provided string as a sequence of characters to use as symbols
        sym_list = list(args.symbols)

    bases = [base]
    if args.include_prefixes and len(base) >= 3:
        short = base[:3]
        if short not in bases:
            bases.insert(0, short)

    # generate for each base/prefix and union results
    all_results: set = set()
    for b in bases:
        all_results.update(generate_variations(b, phone, symbols=sym_list))

    results = all_results
    if not results:
        print("No candidates generated. Provide a longer base text.")
        return

    sorted_res = sorted(results, key=lambda s: (len(s), s))
    with open(args.out, "w", encoding="utf-8") as f:
        for r in sorted_res:
            f.write(r + "\n")

    print(f"Wrote {len(sorted_res)} passwords to {args.out}")
    print("Sample:")
    for s in sorted_res[:20]:
        print(" ", s)


if __name__ == "__main__":
    main()