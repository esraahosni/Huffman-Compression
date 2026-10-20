import sys
from compress import compress
from decompress import decompress


def main():
    a = sys.argv[1:]
    if len(a) >= 2:
        mode = a[0].lower()
        if mode == "c":
            src = a[1]
            dst = a[2] if len(a) > 2 else "out.bin"
            mp = float(a[3]) if len(a) > 3 else 0.05
            compress(src, dst, mp)
        elif mode == "d":
            src = a[1]
            dst = a[2] if len(a) > 2 else "restored.txt"
            decompress(src, dst)
        else:
            print("Unknown mode! Use 'c' for compress or 'd' for decompress.")
            print("Usage: python main.py c <input> <output> [min_prob]")
            print("       python main.py d <input> <output>")
    else:
        choice = input("Choose mode - (c)ompress or (d)ecompress: ").strip().lower()
        if choice == "d":
            src = input("Compressed input file [out.bin]: ").strip() or "out.bin"
            dst = input("Output restored file [restored.txt]: ").strip() or "restored.txt"
            decompress(src, dst)
        else:
            src = input("Input file to compress: ").strip()
            dst = input("Output compressed file [out.bin]: ").strip() or "out.bin"
            while True:
                try:
                    mp = float(input("Minimum probability [0.05]: ").strip() or "0.05")
                    break
                except ValueError:
                    print("Invalid input, please enter a number such as 0.05")
            compress(src, dst, mp)


if __name__ == "__main__":
    main()
