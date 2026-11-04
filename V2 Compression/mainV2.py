from compressV2 import compress
from decompressV2 import decompress


def main():
    mode = input("Choose mode - (c)ompress or (d)ecompress: ").strip().lower()
    src = input("Input file [test.txt] <relative path for me only>: ").strip().strip('"') or "Data Comp\Huffman\test.txt"

    if mode == "c":
        dst = input("Output compressed file [out.txt]: ").strip() or "out.txt"
        p = input("Minimum probability [0.05]: ").strip()
        compress(src, dst, float(p) if p else 0.05)
    elif mode == "d":
        dst = input("Output file [restored.txt]: ").strip() or "restored.txt"
        decompress(src, dst)
        print("Done.")
    else:
        print("Unknown mode.")


if __name__ == "__main__":
    main()
