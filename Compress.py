import heapq
import struct
import sys
from collections import Counter

OTHERS = 256 


def build_lengths(freqs):
    if len(freqs) == 1:                      
        return {next(iter(freqs)): 1}
    heap = [(f, i, (s,)) for i, (s, f) in enumerate(sorted(freqs.items()))]
    heapq.heapify(heap)
    lengths = dict.fromkeys(freqs, 0)
    counter = len(heap)
    while len(heap) > 1:                    
        f1, _, g1 = heapq.heappop(heap)
        f2, _, g2 = heapq.heappop(heap)
        for s in g1 + g2:
            lengths[s] += 1                 
        heapq.heappush(heap, (f1 + f2, counter, g1 + g2))
        counter += 1
    return lengths


def canonical_codes(lengths):
    code, prev_len, codes = 0, 0, {}
    for s, l in sorted(lengths.items(), key=lambda x: (x[1], x[0])):
        code <<= (l - prev_len)
        codes[s] = (code, l)
        code += 1
        prev_len = l
    return codes


def name(s):
    return "Others" if s == OTHERS else repr(chr(s))

def compress(in_path, out_path, min_prob):
    with open(in_path, "rb") as f:
        data = f.read()
    n = len(data)
    counts = Counter(data)

    distinct = sorted(counts)
    width = (len(distinct) - 1).bit_length() if distinct else 0
    index = {s: i for i, s in enumerate(distinct)}

    rare_set = {s for s, c in counts.items() if c / n <= min_prob} if n else set()
    freqs = {s: c for s, c in counts.items() if s not in rare_set}
    if rare_set:
        freqs[OTHERS] = sum(counts[s] for s in rare_set)

    lengths = build_lengths(freqs) if freqs else {}
    codes = canonical_codes(lengths)

    parts = []
    for b in data:
        if b in rare_set:
            c, l = codes[OTHERS]
            parts.append(format(c, f"0{l}b"))           
            if width:
                parts.append(format(index[b], f"0{width}b"))  
        else:
            c, l = codes[b]
            parts.append(format(c, f"0{l}b"))
    bits = "".join(parts)
    nbits = len(bits)

    bits += "0" * ((-nbits) % 8)
    payload = int(bits, 2).to_bytes(len(bits) // 8, "big") if bits else b""

    with open(out_path, "wb") as f:
        f.write(struct.pack(">QH", n, len(lengths)))
        for s, l in sorted(lengths.items(), key=lambda x: (x[1], x[0])):
            f.write(struct.pack(">HB", s, l))
        f.write(struct.pack(">H", len(distinct)))
        f.write(bytes(distinct))
        f.write(payload)

    print("Huffman table:")
    for s, (c, l) in sorted(codes.items(), key=lambda x: (x[1][1], x[0])):
        print(f"  {name(s):8} {format(c, f'0{l}b')}")
    if rare_set:
        print(f"Original code length for 'Others' symbols: {width} bits")
    overhead = 10 + 3 * len(lengths) + 2 + len(distinct)
    print(f"compressed data: {nbits} bits ({len(payload)} B) + overhead {overhead} B")
    print(f"original: {n} B, compressed file: {overhead + len(payload)} B")


def main():
    a = sys.argv[1:]
    if len(a) >= 3:
        src, dst, mp = a[0], a[1], float(a[2])
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
