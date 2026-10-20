# Huffman Coding Compression & Decompression Tool

A Python-based file compression and decompression utility implementing **Huffman Coding** with an optimization for rare symbols (`OTHERS` grouping) and custom header serialization.

---

## Project Structure

Your project folder should contain the following files:
* **`compressor.py`** – Handles the Huffman tree creation, rare symbol grouping, code generation, and binary encoding.
* **`decompressor.py`** – Reads the compressed binary file, parses the custom header/table, and decodes the payload back to the original file.
* **`main.py`** – The entry point script that connects both compression and decompression routines via command-line arguments or interactive prompts.

---

## File Format Architecture

The compressed binary output (`.bin`) is structured sequentially as follows:
1. **Header (10 bytes):** 
   - Original file size `n` (`>Q` - 8 bytes)
   - Number of code entries (`>H` - 2 bytes)
2. **Huffman Table (Variable):** 
   - Symbol ID (`>H` - 2 bytes)
   - Code length (`>B` - 1 byte)
   - Packed binary code bytes (Variable length based on code size)
3. **Distinct Metadata (Variable):** 
   - Distinct symbol count (`>H` - 2 bytes)
   - Sorted unique raw bytes array (`distinct_len` bytes)
4. **Payload (Variable):** 
   - Packed Huffman bitstream padded with zeros to the nearest full byte.

---

## How to Run

You can run the script using either **Command Line Arguments** or via **Interactive Mode**.

### 1. Compression Mode
Using command-line arguments:
```bash
python main.py c <input_file> <output_file> [min_prob]
