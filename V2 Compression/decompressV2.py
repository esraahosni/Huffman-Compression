OTHERS = 256  # must match compress.py


def decompress(in_path, out_path):
    with open(in_path, "r") as f:
        lines = f.read().split("\n")

    n = int(lines[0])
    if n == 0:
        open(out_path, "wb").close()
        return

    padding = int(lines[1])

    # Huffman table: code -> symbol
    k = int(lines[2])
    decode = {}
    pos = 3
    for _ in range(k):
        s, c = lines[pos].split()
        decode[c] = int(s)
        pos += 1

    # Rare table: suffix -> symbol
    r = int(lines[pos])
    pos += 1
    rare_decode = {}
    for _ in range(r):
        s, c = lines[pos].split()
        rare_decode[c] = int(s)
        pos += 1
    rare_width = len(next(iter(rare_decode))) if rare_decode else 0

    # decimals -> bytes -> bits
    decimals = [int(x) for x in lines[pos].split()]
    raw = bytes(decimals)
    bits = "".join(format(b, "08b") for b in raw)
    if padding:
        bits = bits[:-padding]

    # walk the bits and match codes
    out = bytearray()
    cur = ""
    i = 0
    while i < len(bits) and len(out) < n:
        cur += bits[i]
        i += 1
        if cur in decode:
            s = decode[cur]
            cur = ""
            if s == OTHERS:
                suffix = bits[i:i + rare_width]
                i += rare_width
                out.append(rare_decode[suffix])
            else:
                out.append(s)

    with open(out_path, "wb") as f:
        f.write(out)