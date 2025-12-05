#!/usr/bin/env python3
"""
Generate password-like combinations in the exact style requested.

Now includes:
- sourav
- Sourav
- SOURAV

And all combinations with phone, separators, substrings, numbers, etc.
"""

from pathlib import Path

OUTPUT_FILE = "passwords.txt"

SEPARATORS = ["", "@", "*", "#", ".", "_", "-"]
COMMON_DIGITS = ["1", "12", "123", "1234", "12345", "555", "007", "69", "984", "0984", "623", "6234"]


def title_case(s):
    return s[:1].upper() + s[1:].lower() if s else s


def phone_substrings(phone):
    """Generate useful phone number substrings."""
    if not phone:
        return set()

    digits = "".join(ch for ch in phone if ch.isdigit())
    n = len(digits)

    parts = set()
    parts.add(digits)  # full phone

    # meaningful slices
    if n >= 2:
        parts.add(digits[-2:])
    if n >= 3:
        parts.add(digits[:3])
        parts.add(digits[-3:])
    if n >= 4:
        parts.add(digits[:4])
        parts.add(digits[-4:])
    if n >= 5:
        parts.add(digits[-5:])
    if n >= 6:
        parts.add(digits[:6])
        parts.add(digits[-6:])

    # reversed
    parts.add(digits[::-1])

    return parts


def generate_combinations(name, phone):
    name = name.strip()
    phone = phone.strip() if phone else None

    # name variants: lower, title, upper
    name_variants = []
    for v in [name.lower(), title_case(name), name.upper()]:
        if v not in name_variants:
            name_variants.append(v)

    results = []
    add = results.append

    phone_parts = phone_substrings(phone) if phone else set()

    # 1) full phone direct combos
    if phone:
        full_phone = "".join(ch for ch in phone if ch.isdigit())
        for nv in name_variants:
            add(f"{nv}{full_phone}")
            add(f"{nv}@{full_phone}")
            add(f"{nv}.{full_phone}")
        add(full_phone)  # phone alone

    # 2) name + phone substrings with separators
    token_pool = set(COMMON_DIGITS) | phone_parts

    for nv in name_variants:
        for sep in SEPARATORS:
            for tok in token_pool:
                add(f"{nv}{sep}{tok}")
                # also lowercase version
                add(f"{nv.lower()}{sep}{tok}")

            # reverse ordering (phone first)
            for tok in phone_parts:
                add(f"{tok}{sep}{nv}")
                add(f"{tok}{sep}{nv.lower()}")

    # 3) name + phone substrings (no separator)
    for nv in name_variants:
        for p in phone_parts:
            add(f"{nv}{p}")
            add(f"{nv.lower()}{p}")

    # 4) Name + short numeric sequences
    for nv in name_variants:
        for length in range(1, 6):
            seq = "".join(str((i % 10)) for i in range(1, length + 1))
            add(f"{nv}{seq}")
            add(f"{nv.lower()}{seq}")

            for d in "0123456789":
                add(f"{nv}{d * length}")
                add(f"{nv.lower()}{d * length}")

    # 5) Extra example-style combinations
    for nv in name_variants:
        for sep in ["@", "*", "#", ".", ""]:
            for num in COMMON_DIGITS:
                add(f"{nv}{sep}{num}")
                add(f"{nv.lower()}{sep}{num}")

    # Deduplicate
    final = []
    seen = set()
    for item in results:
        if item not in seen and len(item) > 1:
            seen.add(item)
            final.append(item)

    return final


def save_to_file(items, filepath):
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




# #!/usr/bin/env python3
# """
# Flexible password generator.

# Features (best-effort wide coverage while avoiding infinite output):
# - Case variations (all-uppercase, all-lower, title, mixed where feasible)
# - Leet substitutions
# - Any digits/numeric sequences (ranges and random)
# - Any separator (all punctuation + none)
# - Year-like 4-digit numbers (configurable range)
# - Phone number parts (full, prefixes, suffixes, reversed)
# - Character re-orderings (shuffles, sampled permutations up to configurable size)
# - Prepend/append symbols, repeat symbols
# - Random combinations and sampled bruteforce-style variants
# - Filters results to length > 7
# - Stops when MAX_OUTPUT reached (configurable)

# Usage: run and follow prompts. Adjust constants at top if you want more/less output.
# """
# import itertools
# import random
# import string
# from pathlib import Path
# from collections import deque

# # ---------- CONFIG ----------
# MAX_OUTPUT = 50000        # stop after this many unique passwords (prevents explosion)
# RANDOM_SEED = 42         # deterministic randomness for reproducible runs
# MAX_SAMPLE_PER_COMBO = 2000  # cap per combination block to sample permutations
# MAX_SHUFFLES_PER_BASE = 300  # how many shuffled reorders to try per base variant
# MAX_PERMUTE_LEN = 7      # only permute subsets up to this length (factorial explosion)
# YEARS_RANGE = range(1950, 2031)  # years to include
# RANDOM_NUMBER_MAX = 999999  # random numbers up to this when generating random numeric suffixes
# OUTPUT_FILE = "passwords.txt"
# # ---------------------------

# random.seed(RANDOM_SEED)

# PUNCT = list(string.punctuation) + [""]  # separator choices (include empty)
# SYMBOLS = list(string.punctuation)
# DIGITS = [str(i) for i in range(0, 1000)]  # short numeric tokens
# # extend with some repeated patterns
# DIGITS += [str(i)*n for i in range(1, 10) for n in (2,3,4)]

# # simple leet map (keeps output readable)
# LEET_MAP = {
#     'a': ['@','4'],
#     'b': ['8'],
#     'e': ['3'],
#     'g': ['9','6'],
#     'i': ['1','!','|'],
#     'l': ['1','|'],
#     'o': ['0'],
#     's': ['5','$'],
#     't': ['7'],
#     'z': ['2']
# }

# def leet_variants(s, max_variants=128):
#     """Return a (possibly large) set of leet-substituted variants, capped."""
#     indices = [i for i,ch in enumerate(s) if ch.lower() in LEET_MAP]
#     variants = set([s])
#     for idx in indices:
#         ch = s[idx].lower()
#         replacements = LEET_MAP.get(ch, [])
#         # expand
#         new = set()
#         for v in variants:
#             for r in replacements:
#                 new.add(v[:idx] + r + v[idx+1:])
#         variants |= new
#         if len(variants) > max_variants:
#             break
#     # include some mixed replacements
#     variants_list = list(variants)
#     random.shuffle(variants_list)
#     return set(variants_list[:max_variants])

# def case_variants(s, cap=256):
#     """Generate case variants (upper, lower, title, and sampled mixed cases)."""
#     variants = set([s, s.lower(), s.upper(), s.title()])
#     n = len(s)
#     # If n small, produce all 2^n combos; otherwise sample random mixes
#     if n <= 10:
#         for mask in range(1, 1 << n):
#             chars = []
#             for i, ch in enumerate(s):
#                 if (mask >> i) & 1:
#                     chars.append(ch.upper())
#                 else:
#                     chars.append(ch.lower())
#             variants.add(''.join(chars))
#             if len(variants) >= cap:
#                 break
#     else:
#         # sample random mixed-case strings
#         while len(variants) < cap:
#             chars = [ch.upper() if random.random() < 0.5 else ch.lower() for ch in s]
#             variants.add(''.join(chars))
#     return variants

# def phone_parts(phone):
#     """Return useful phone substrings."""
#     parts = set()
#     digits = ''.join(c for c in (phone or "") if c.isdigit())
#     if not digits:
#         return parts
#     n = len(digits)
#     parts.add(digits)
#     # prefixes/suffixes
#     for l in (2,3,4,5,6):
#         if n >= l:
#             parts.add(digits[:l])
#             parts.add(digits[-l:])
#     # mid and reversed
#     if n >= 3:
#         mid = n//2
#         parts.add(digits[max(0, mid-2):min(n, mid+2)])
#     parts.add(digits[::-1])
#     return parts

# def sampled_permutations(s, max_len=MAX_PERMUTE_LEN, sample_cap=MAX_SAMPLE_PER_COMBO):
#     """
#     Return a sampled set of permutations of characters in s.
#     - Only permute up to max_len characters to avoid factorial explosion.
#     - For longer strings, sample random subsets and shuffle them.
#     """
#     out = set()
#     chars = list(s)
#     n = len(chars)
#     # if short, try all permutations of full length up to cap
#     if n <= max_len:
#         perms = set(''.join(p) for p in itertools.permutations(chars))
#         # also include permutations of subsets of sizes 2..n
#         for k in range(2, min(n, max_len)+1):
#             for comb in itertools.permutations(chars, k):
#                 out.add(''.join(comb))
#             if len(out) > sample_cap:
#                 break
#     else:
#         # sample: choose random subset lengths and shuffle
#         tries = 0
#         while len(out) < sample_cap and tries < sample_cap * 3:
#             k = random.randint(2, max_len)
#             sample = random.sample(chars, k)
#             random.shuffle(sample)
#             out.add(''.join(sample))
#             tries += 1
#     # also include some shuffles of the whole string
#     shuffles = 0
#     while shuffles < MAX_SHUFFLES_PER_BASE and len(out) < sample_cap:
#         shuffled = chars[:]
#         random.shuffle(shuffled)
#         out.add(''.join(shuffled))
#         shuffles += 1
#     return out

# def generate_numbers_any(limit=5000):
#     """Generate a wide variety of numeric tokens: ranges, repeated digits, random numbers."""
#     nums = set()
#     # repeated digits
#     for d in '0123456789':
#         for l in (2,3,4,5,6):
#             nums.add(d * l)
#     # sequence ranges
#     for i in range(0, 1000):
#         nums.add(str(i))
#     # some larger ranges
#     for i in range(10000, 10050):
#         nums.add(str(i))
#     # random samples
#     for _ in range(limit):
#         nums.add(str(random.randint(0, RANDOM_NUMBER_MAX)))
#     return nums

# def year_tokens():
#     return {str(y) for y in YEARS_RANGE}

# def prepend_append_variants(s, symbols=SYMBOLS, max_repeat=3, cap=500):
#     """Return variants with symbols prepended/appended, including repeats."""
#     out = set()
#     out.add(s)
#     for sym in symbols:
#         out.add(sym + s)
#         out.add(s + sym)
#         for r in range(2, max_repeat+1):
#             out.add(sym*r + s)
#             out.add(s + sym*r)
#     # sample some combos with two different symbols
#     combos = 0
#     while combos < cap and len(out) < cap:
#         a = random.choice(symbols)
#         b = random.choice(symbols)
#         out.add(a + s + b)
#         out.add(b + s + a)
#         combos += 1
#     return out

# def generate_all(base, phone=None, max_output=MAX_OUTPUT):
#     """Master generator assembling everything. Yields up to max_output unique items."""
#     seen = set()
#     queue = deque()

#     # base core variants: case + leet
#     case_vars = case_variants(base, cap=512)
#     expanded = set()
#     for cv in case_vars:
#         expanded |= leet_variants(cv, max_variants=128)
#     base_core = set(sorted(expanded))

#     # gather token pools
#     numbers_pool = generate_numbers_any(limit=2000)
#     years_pool = year_tokens()
#     phone_pool = phone_parts(phone)
#     separators = PUNCT

#     # seed queue with straightforward combos
#     for b in base_core:
#         for sep in separators:
#             # attach some numeric tokens and years (sample to avoid huge loops)
#             sampled_nums = random.sample(list(numbers_pool), min(300, len(numbers_pool)))
#             for num in sampled_nums:
#                 queue.append(f"{b}{sep}{num}")
#             sampled_years = random.sample(list(years_pool), min(50, len(years_pool)))
#             for y in sampled_years:
#                 queue.append(f"{b}{sep}{y}")
#             # phone combos
#             for p in phone_pool:
#                 queue.append(f"{b}{sep}{p}")
#                 queue.append(f"{p}{sep}{b}")

#     # permutations / reorderings
#     for b in base_core:
#         perms = sampled_permutations(b, max_len=MAX_PERMUTE_LEN, sample_cap=MAX_SAMPLE_PER_COMBO)
#         for p in perms:
#             # combine with numbers and symbols
#             for sep in random.sample(separators, min(10, len(separators))):
#                 n = random.choice(list(numbers_pool))
#                 queue.append(f"{p}{sep}{n}")
#                 queue.append(f"{n}{sep}{p}")
#             # prepend/append symbols
#             for combo in prepend_append_variants(p, symbols=SYMBOLS, max_repeat=2, cap=40):
#                 queue.append(combo)

#     # random brute-force style attachments
#     for _ in range(2000):
#         b = random.choice(list(base_core))
#         sep = random.choice(separators)
#         num = str(random.randint(0, RANDOM_NUMBER_MAX))
#         # random order of components
#         cand = random.choice([
#             f"{b}{sep}{num}",
#             f"{num}{sep}{b}",
#             f"{sep}{b}{num}",
#             f"{b}{num}{sep}"
#         ])
#         queue.append(cand)

#     # final stage: yield unique items filtered by length > 7
#     while queue and len(seen) < max_output:
#         cand = queue.popleft()
#         if not cand:
#             continue
#         # ensure printable (strip potential nonprintable)
#         cand = ''.join(ch for ch in cand if ch.isprintable())
#         if len(cand) <= 7:
#             continue
#         if cand in seen:
#             continue
#         seen.add(cand)
#         yield cand

#     # If still under max_output, produce random mixes using characters of base + digits + symbols
#     chars_pool = list(set(list(base) + list(string.digits) + SYMBOLS))
#     while len(seen) < max_output:
#         ln = random.randint(8, max(12, len(base) + 6))
#         cand = ''.join(random.choice(chars_pool) for _ in range(ln))
#         if cand not in seen:
#             seen.add(cand)
#             yield cand

# def save_to_file(items_iterable, filepath=OUTPUT_FILE):
#     p = Path(filepath)
#     p.parent.mkdir(parents=True, exist_ok=True)
#     with p.open("w", encoding="utf-8") as f:
#         for it in items_iterable:
#             f.write(it + "\n")

# def main():
#     try:
#         # base = input("Enter base text (required): ").strip()
#         base = 'sourav'
#     except (EOFError, KeyboardInterrupt):
#         return
#     if not base:
#         print("Base text required. Exiting.")
#         return
#     # phone = input("Enter phone number (optional): ").strip() or None
#     phone = '9876543210'
#     # max_out = input(f"Max passwords to generate (default {MAX_OUTPUT}): ").strip()
#     max_out = '50000'
#     try:
#         max_out = int(max_out) if max_out else MAX_OUTPUT
#     except:
#         max_out = MAX_OUTPUT

#     gen = generate_all(base, phone, max_output=max_out)
#     # Save generator to file (streaming)
#     items_written = 0
#     p = Path(OUTPUT_FILE)
#     p.parent.mkdir(parents=True, exist_ok=True)
#     with p.open("w", encoding="utf-8") as f:
#         for pwd in gen:
#             f.write(pwd + "\n")
#             items_written += 1
#     print(f"Generated and saved {items_written} passwords to '{OUTPUT_FILE}'")

# if __name__ == "__main__":
#     main()


