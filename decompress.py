import struct

OTHERS = 256


def decompress(in_path, out_path):
    with open(in_path, "rb") as f:
        header_prefix = f.read(10)
        if len(header_prefix) < 10:
            raise ValueError("File is too short to contain a valid header.")
        n, num_codes = struct.unpack(">QH", header_prefix)

        decode_map = {}
        for _ in range(num_codes):
            entry_header = f.read(3)
            s, code_len = struct.unpack(">HB", entry_header)
            
            code_byte_len = (code_len + 7) // 8
            code_bytes = f.read(code_byte_len)
            
            code_int = int.from_bytes(code_bytes, "big")
            code_str = format(code_int, f"0{code_len}b")[-code_len:]
            
            decode_map[code_str] = s

        distinct_len_bytes = f.read(2)
        distinct_len = struct.unpack(">H", distinct_len_bytes)[0]
        distinct = list(f.read(distinct_len))

        payload = f.read()

    width = (len(distinct) - 1).bit_length() if distinct else 0

    # Convert payload bytes back into a stream of bits
    bits = "".join(format(b, "08b") for b in payload)
    bit_len = len(bits)
    bit_idx = 0

    decoded_bytes = bytearray()

    while len(decoded_bytes) < n and bit_idx < bit_len:
        matched = False
        for length in range(1, bit_len - bit_idx + 1):
            prefix = bits[bit_idx : bit_idx + length]
            if prefix in decode_map:
                symbol = decode_map[prefix]
                bit_idx += length
                matched = True
                break
        
        if not matched:
            break

        if symbol == OTHERS:
            if width > 0:
                index_bits = bits[bit_idx : bit_idx + width]
                index = int(index_bits, 2)
                bit_idx += width
                decoded_bytes.append(distinct[index])
        else:
            decoded_bytes.append(symbol)

    with open(out_path, "wb") as f:
        f.write(decoded_bytes)

    print(f"Successfully decompressed {n} bytes to '{out_path}'.")
