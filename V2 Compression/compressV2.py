from collections import Counter

OTHERS = 256  # pseudo-symbol for all rare symbols


def name(s):
    return "Others" if s == OTHERS else repr(chr(s))


def build_huffman(freqs):
    """freqs: {symbol: count} -> {symbol: code} (merge the two smallest)."""
    if len(freqs) == 1:
        return {s: "0" for s in freqs}

    nodes = [(count, [s]) for s, count in freqs.items()]
    nodes.sort(key=lambda x: x[0], reverse=True)      # smallest at the end
    codes = {s: "" for s in freqs}

    while len(nodes) > 1:
        low = nodes.pop()          # smallest
        high = nodes.pop()         # second smallest
        for s in high[1]:
            codes[s] = "0" + codes[s]
        for s in low[1]:
            codes[s] = "1" + codes[s]

        merged = (high[0] + low[0], high[1] + low[1])
        pos = 0
        while pos < len(nodes) and nodes[pos][0] > merged[0]:
            pos += 1
        nodes.insert(pos, merged)
    return codes


def compress(in_path, out_path, min_prob=0.05):
    with open(in_path, "rb") as f:
        data = f.read()
    n = len(data)
    if n == 0:
        with open(out_path, "w") as f:
            f.write("0\n")
        return

    counts = Counter(data)

    # 1) rare symbols (probability < min_prob) -> Others
    rare = {s for s in counts if counts[s] / n < min_prob}
    if len(rare) < 2:                       # one rare symbol needs no escape
        rare = set()

    # 2) rare table: fixed-width index for every rare symbol
    rare_list = sorted(rare)
    rare_width = (len(rare_list) - 1).bit_length() if rare_list else 0
    rare_code = {s: format(i, f"0{rare_width}b") for i, s in enumerate(rare_list)}

    # 3) Huffman table for frequent symbols + Others
    freqs = {s: c for s, c in counts.items() if s not in rare}
    if rare:
        freqs[OTHERS] = sum(counts[s] for s in rare)
    codes = build_huffman(freqs)

    # 4) encode everything into one long bit string
    parts = []
    for s in data:
        if s in rare:
            parts.append(codes[OTHERS] + rare_code[s])   # Others + suffix
        else:
            parts.append(codes[s])
    bits = "".join(parts)

    # 5) pad to a multiple of 8
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding

    # 6) every 8 bits -> one byte -> its decimal value (0..255)
    decimals = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]

    # 7) write the file (plain text)
    with open(out_path, "w") as f:
        f.write(f"{n}\n{padding}\n")
        f.write(f"{len(codes)}\n")
        for s, c in codes.items():
            f.write(f"{s} {c}\n")
        f.write(f"{len(rare_code)}\n")
        for s, c in rare_code.items():
            f.write(f"{s} {c}\n")
        f.write(" ".join(map(str, decimals)) + "\n")

    # 8) report
    print("\nHuffman table:")
    print("  Symbol   Prob     Code")
    for s in sorted(codes, key=lambda x: (len(codes[x]), x)):
        print(f"  {name(s):8} {freqs[s] / n:<8.4f} {codes[s]}")

    if rare_code:
        print("\nRare (Others) table:")
        print("  Symbol   Suffix")
        for s, c in rare_code.items():
            print(f"  {name(s):8} {c}")

    print(f"\nOriginal size    : {n} bytes")
    print(f"Compressed data  : {len(decimals)} bytes (decimal numbers)")
    print(f"Padding          : {padding} bits")
    print("First decimals   :", decimals[:10])