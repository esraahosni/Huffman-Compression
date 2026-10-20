import struct
import sys
from collections import Counter

OTHERS = 256


def name(s):
    return "Others" if s == OTHERS else repr(chr(s))


def build_codes(freqs, verbose=True):
    if len(freqs) == 1:
        return {next(iter(freqs)): "0"}

    nodes = [(f, [s]) for s, f in sorted(freqs.items(), key=lambda x: (-x[1], x[0]))]
    codes = {s: "" for s in freqs}
    total = sum(freqs.values())
    step = 0

    while len(nodes) > 1:
        lower = nodes.pop()          
        upper = nodes.pop()         
        for s in upper[1]:
            codes[s] = "0" + codes[s]
        for s in lower[1]:
            codes[s] = "1" + codes[s]
        merged = (upper[0] + lower[0], upper[1] + lower[1])

        i = 0
        while i < len(nodes) and nodes[i][0] > merged[0]:
            i += 1
        nodes.insert(i, merged)

        step += 1
        if verbose:
            def lab(n):
                return "+".join(name(s) for s in n[1]) + f"={n[0]/total:.3f}"
            print(f"  step {step}: merge [{lab(upper)}](0) + [{lab(lower)}](1)")
            print("          list: " + ", ".join(lab(n) for n in nodes))
    return codes


def compress(in_path, out_path, min_prob):
    with open(in_path, "rb") as f:
        data = f.read()
    n = len(data)
    counts = Counter(data)

    distinct = sorted(counts)
    width = (len(distinct) - 1).bit_length() if distinct else 0
    index = {s: i for i, s in enumerate(distinct)}

    rare = {s for s, c in counts.items() if c / n <= min_prob} if n else set()
    freqs = {s: c for s, c in counts.items() if s not in rare}
    if rare:
        freqs[OTHERS] = sum(counts[s] for s in rare)

    print("Building Huffman tree:")
    codes = build_codes(freqs) if freqs else {}

    parts = []
    for b in data:
        if b in rare:
            parts.append(codes[OTHERS])
            if width:
                parts.append(format(index[b], f"0{width}b"))
        else:
            parts.append(codes[b])
    bits = "".join(parts)
    nbits = len(bits)
    bits += "0" * ((-nbits) % 8)
    payload = int(bits, 2).to_bytes(len(bits) // 8, "big") if bits else b""

    header = struct.pack(">QH", n, len(codes))
    for s, c in sorted(codes.items(), key=lambda x: (len(x[1]), x[1])):
        header += struct.pack(">HB", s, len(c))
        header += int(c, 2).to_bytes((len(c) + 7) // 8, "big")
    header += struct.pack(">H", len(distinct)) + bytes(distinct)

    with open(out_path, "wb") as f:
        f.write(header + payload)

    print("\nHuffman table:")
    for s, c in sorted(codes.items(), key=lambda x: (len(x[1]), x[1])):
        print(f"  {name(s):8} {c}")
    if rare:
        print(f"Original code length for 'Others' symbols: {width} bits")
    print(f"\ncompressed data: {nbits} bits ({len(payload)} B) + header {len(header)} B")
    print(f"original: {n} B, compressed file: {len(header) + len(payload)} B")


def main():
    a = sys.argv[1:]
    if len(a) >= 3:                                
        compress(a[0], a[1], float(a[2]))
    else:
        src = input("input file: ").strip()
        dst = input("output file [out.bin]: ").strip() or "out.bin"
        while True:
            try:
                mp = float(input("minimum probability[0.05]: ").strip() or "0.05")
                break
            except ValueError:
                print("Invalid input, please enter a number such as 0.05")
        compress(src, dst, mp)


if __name__ == "__main__":
    main()
