from collections import Counter
 
OTHERS = 256  
 
def name(s):
    return "Others" if s == OTHERS else repr(chr(s))
 
 
def to_bits(number, width):
    return format(number, f"0{width}b")       
 
def build_huffman(freqs):
    if len(freqs) == 1:                      
        return {s: "0" for s in freqs}
 
    nodes = [(count, [s]) for s, count in freqs.items()]
    nodes.sort(reverse=True)
    
    codes = {s: "" for s in freqs}
 
    while len(nodes) > 1:
        low = nodes.pop()                    
        high = nodes.pop()                    
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
 
def compress(in_path, out_path, min_prob):
    with open(in_path, "rb") as f:
        data = f.read()
    n = len(data)
    counts = Counter(data)                    
 
    distinct = sorted(counts)
    width = max(1, (len(distinct) - 1).bit_length())
    original = {s: to_bits(i, width) for i, s in enumerate(distinct)}
 
    rare = [s for s in counts if counts[s] / n <= min_prob]
    freqs = {s: counts[s] for s in counts if s not in rare}
    if rare:
        freqs[OTHERS] = sum(counts[s] for s in rare)
 
    codes = build_huffman(freqs)
 
    bits = ""
    for s in data:
        if s in rare:
            bits += codes[OTHERS] + original[s]   
        else:
            bits += codes[s]
 
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding
 
    numbers = []
    for i in range(0, len(bits), 8):
        numbers.append(int(bits[i:i + 8], 2))
    payload = bytes(numbers)
 
    header = f"{n}\n{padding}\n{len(codes)}\n"
    for s in codes:
        header += f"{s} {codes[s]}\n"
    header += f"{len(distinct)}\n"
    header += " ".join(str(s) for s in distinct) + "\n"
 
    with open(out_path, "wb") as f:
        f.write(header.encode("ascii"))
        f.write(payload)
 
    print("\nOriginal code table:")
    print("  Symbol   Original Code")
    for s in distinct:
        print(f"  {name(s):8} {original[s]}")
 
    print("\nHuffman code table:")
    print("  Symbol   Code")
    for s in sorted(codes):
        print(f"  {name(s):8} {codes[s]}")

    original_size = n
    compressed_size = len(header) + len(payload)

    print(f"\nOriginal size   : {original_size} bytes")
    print(f"Compressed size : {compressed_size} bytes")
    print(f"Compressed data : {len(payload)} bytes (without header)")
 
