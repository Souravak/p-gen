#!/usr/bin/env python3

from pathlib import Path
import random
import string

OUTPUT_FILE = "passwords.txt"
SEPARATORS = ["", "@", "*", "#", ".", "_", "-"]
COMMON_NUMS = [
    "1", "12", "123", "1234", "12345", "555",
    "007", "69", "987", "984", "0984", "623", "6234", "5550984"
]

MIN_LEN = 8
MAX_LEN = 16


def title_case(s):
    return s[:1].upper() + s[1:].lower()


def generate_name_slices(name: str):
    """Generate: s, so, sou, sour, soura, sourav → each in lower/title/upper."""
    name = name.strip()
    slices = []

    for i in range(1, len(name) + 1):
        part = name[:i]
        slices.extend([
            part.lower(),
            title_case(part),
            part.upper()
        ])

    # unique preserving order
    return list(dict.fromkeys(slices))


def phone_substrings(phone):
    """Generate meaningful phone number slices."""
    if not phone:
        return set()

    digits = "".join(ch for ch in phone if ch.isdigit())
    n = len(digits)
    parts = set()

    if n == 0:
        return parts

    # full phone
    parts.add(digits)

    # slices
    for l in range(2, min(6, n) + 1):
        parts.add(digits[:l])
        parts.add(digits[-l:])

    # reversed
    parts.add(digits[::-1])

    return {p for p in parts if 2 <= len(p) <= 10}


def generate_combinations(name, phone):
    name_slices = generate_name_slices(name)
    phone_parts = phone_substrings(phone)

    full_phone = "".join(ch for ch in phone if ch.isdigit()) if phone else None

    results = []
    add = results.append

    # 1) phone alone (filter later)
    if full_phone:
        add(full_phone)

    # 2) name + full phone
    if full_phone:
        for nv in name_slices:
            add(f"{nv}{full_phone}")
            add(f"{nv}@{full_phone}")
            add(f"{nv}.{full_phone}")
            add(f"{full_phone}{nv}")

    # 3) name + phone substrings
    for nv in name_slices:
        for p in phone_parts:
            add(f"{nv}{p}")
            add(f"{nv}@{p}")
            add(f"{nv}#{p}")
            add(f"{nv}.{p}")
            add(f"{p}{nv}")

    # 4) name + number patterns
    token_pool = set(COMMON_NUMS) | phone_parts

    for nv in name_slices:
        for sep in SEPARATORS:
            for tok in token_pool:
                add(f"{nv}{sep}{tok}")
                add(f"{tok}{sep}{nv}")

    # 5) name + auto-sequence numbers
    for nv in name_slices:
        for length in range(1, 6):
            seq = "".join(str((i % 10)) for i in range(1, length + 1))
            add(f"{nv}{seq}")
            add(f"{nv}@{seq}")

    # ----- FINAL FILTER -----
    final = []
    seen = set()

    for item in results:
        if item in seen:
            continue
        if MIN_LEN <= len(item) <= MAX_LEN:
            final.append(item)
            seen.add(item)

    return final


def save_to_file(items, filepath=OUTPUT_FILE):
    with open(filepath, "w", encoding="utf-8") as f:
        for it in items:
            f.write(it + "\n")


def main():
    name = input("Enter name (e.g. sourav): ").strip()
    phone = input("Enter phone number (optional): ").strip()

    combos = generate_combinations(name, phone)
    save_to_file(combos, OUTPUT_FILE)

    print(f"Saved {len(combos)} combinations to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
