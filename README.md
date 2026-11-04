# Modified Huffman Compression (with "Others")

A static Huffman compressor written in Python. It is a modified version of the
classic algorithm: symbols with a very low probability are grouped into one
pseudo-symbol called **Others**, which keeps the Huffman table small. The
compressed data is stored as **decimal numbers** (one number per byte), and the
decompressor converts those decimals back to bytes, then to bits, then to the
original text.

---

## Files

| File | Purpose |
|---|---|
| `main.py` | Menu: asks for the mode, file names and minimum probability, then calls the other two files. |
| `compress.py` | Builds the tables, encodes the text, writes the compressed file. |
| `decompress.py` | Reads the compressed file and rebuilds the original. |

Keep the three files in the same folder.

## Requirements

- Python 3.6 or newer
- No external libraries (only the standard library)

## How to run

```
python main.py
```

**Compress**

```
Choose mode - (c)ompress or (d)ecompress: c
Input file: test.txt
Output compressed file [out.txt]:
Minimum probability [0.05]: 0.02
```

**Decompress**

```
Choose mode - (c)ompress or (d)ecompress: d
Input file: out.txt
Output file [restored.txt]:
Done.
```

Pressing Enter on a prompt that shows a default value uses that default.

---

## The algorithm

### Compression

1. **Read the file as bytes** and count how many times each symbol appears.
   Probability of a symbol = its count / total number of symbols.
2. **Find the rare symbols.** Every symbol with probability below
   `min_prob` is rare. If only one symbol is rare, it is not grouped, because a
   single symbol does not need an escape code.
3. **Build the rare table.** The rare symbols are sorted by byte value and each
   gets a fixed-width binary index (the *suffix*).
   The width is `ceil(log2(number of rare symbols))`, so 32 rare symbols need
   5 bits, 4 rare symbols need 2 bits, and so on.
4. **Build the Huffman table.** All rare symbols together form one symbol
   `Others` whose count is the sum of their counts. A Huffman tree is built over
   the frequent symbols plus `Others`:
   - sort by count
   - take the two smallest and merge them (sum of counts)
   - the first of the pair gets a `0` and the second gets a `1`
   - put the merged node back in order and repeat until one node is left
5. **Encode the text.**
   - a frequent symbol is written as its Huffman code
   - a rare symbol is written as `code(Others)` + its suffix
6. **Pad** the bit string with `0` bits until its length is a multiple of 8.
7. **Convert to decimals.** Every 8 bits become one byte, and the value of that
   byte (0-255) is stored as a decimal number.
8. **Write the file** (see the file format below).

### Decompression

1. Read the original length `n`, the padding count, the Huffman table and the
   rare table.
2. Read the decimals and convert each one to a byte, then each byte to 8 bits.
3. Remove the padding bits from the end.
4. Read the bits one at a time. When the collected bits match a Huffman code,
   output that symbol.
   If the code is `Others`, read the next `rare_width` bits, look them up in the
   rare table, and output that symbol.
5. Stop after `n` symbols.

---

## Compressed file format

The compressed file is plain text:

```
156              <- original length n (number of symbols)
7                <- padding: number of zero bits added at the end
13               <- number of rows in the Huffman table
32 10            <- symbol (byte value) and its Huffman code, one row per symbol
101 001
...
256 11001        <- 256 means "Others"
4                <- number of rows in the rare table
100 00           <- rare symbol (byte value) and its suffix
113 01
117 10
119 11
65 60 192 41 ... <- the compressed data as decimal numbers
```

Symbols are stored as byte values: `32` = space, `101` = `e`, `116` = `t`,
`10` = new line, `256` = `Others`.

---

## Example

Input (`test2.txt`):

```
to be or not to be that is the question
to be or not to be that is the answer
the sea is the sea and the rose is the rose
to see the rose is to see the sea
```

Run with minimum probability `0.02`.

**Huffman table**

| Symbol | Probability | Code |
|---|---|---|
| space | 0.2308 | `10` |
| `e` | 0.1538 | `001` |
| `s` | 0.0962 | `111` |
| `t` | 0.1346 | `010` |
| `a` | 0.0449 | `1101` |
| `h` | 0.0641 | `0110` |
| `o` | 0.0897 | `0000` |
| new line | 0.0256 | `11000` |
| `b` | 0.0256 | `01111` |
| `i` | 0.0385 | `00011` |
| `n` | 0.0321 | `01110` |
| `r` | 0.0385 | `00010` |
| Others | 0.0256 | `11001` |

**Rare (Others) table**

| Symbol | Suffix |
|---|---|
| `d` | `00` |
| `q` | `01` |
| `u` | `10` |
| `w` | `11` |

So the letter `q` is written as `11001` (Others) followed by `01` (its suffix).

**Result**

| Item | Value |
|---|---|
| Original size | 156 bytes |
| Compressed data | 67 decimals (67 bytes) |
| Padding | 7 bits |
| First decimals | 65 60 192 41 192 164 19 204 155 84 |

---

## Choosing the minimum probability

`min_prob` controls the balance between the two tables:

- **High value (0.05):** many symbols become rare. The Huffman table is small,
  but each rare symbol costs `code(Others)` + a long suffix. On normal English
  text this is often too high.
- **Low value (0.01 - 0.02):** only truly rare symbols (digits, capitals,
  `q`, `z`, `x`) go into `Others`. The suffix is short and common letters keep
  their own short codes.

Try several values on the same file and compare the compressed size.

## Notes and limitations

- **Size on disk.** The decimals are written as text (`"65 60 192"`), so the
  file on disk is larger than the number of decimals. When reporting the
  compression ratio, compare the original size with the **number of decimals**.
- **Small files.** The tables are stored inside the file, so a very small file
  can come out bigger than the original. The gain shows on longer texts, where
  the tables are paid only once.
- **Random data.** Files where all symbols are about equally likely (random
  bytes, already-compressed files) cannot be compressed by Huffman.
- **Single symbol.** If the file has only one distinct symbol, it gets the
  1-bit code `0`.
- **Empty file.** An empty file is written as a single `0` and restored as an
  empty file.
- **Binary safe.** Files are read and written as bytes, so any file type
  round-trips correctly, not only text.
- **Keep `OTHERS = 256` identical** in `compress.py` and `decompress.py`.
