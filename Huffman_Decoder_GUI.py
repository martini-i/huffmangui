import os
import heapq
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, LabelFrame, ttk
from collections import Counter
import json
from bitarray import bitarray

class Node:
    def __init__(self, freq, char=None, left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

# Build Huffman Tree
def build_huffman_tree(frequency):
    heap = [Node(freq, char) for char, freq in frequency.items()]
    heapq.heapify(heap)
    # Merge nodes until only one node is left
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heap[0]

# Generate Huffman Codes
def create_codes(node, current_code="", codes={}):
    if node.char:
        codes[node.char] = current_code
        return
    create_codes(node.left, current_code + "0", codes)
    create_codes(node.right, current_code + "1", codes)
    return codes

# Encode text
def encode(text, codes):
    return bitarray(''.join(codes[char] for char in text))

# Decode text
def decode(encoded_bits, codes):
    reverse_codes = {code: char for char, code in codes.items()}
    current_code = ""
    decoded_text = ""
    for bit in encoded_bits.to01():
        current_code += bit
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ""
    return decoded_text

# GUI Application Class
class HuffmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Huffman Coding Compression Tool")
        self.root.geometry("700x600")
        # Initialize file path
        self.file_path = ""
        # GUI elements
        tk.Label(root, text="📚 Huffman Coding Compression Tool", font=("Arial", 16)).pack()
        # Select file button
        self.select_button = tk.Button(root, text="📂 Select Text File", command=self.select_file)
        self.select_button.pack()
        self.status_label = tk.Label(root, text="No file selected", font=("Arial", 10))
        self.status_label.pack()
        # Compression and Decompression frames
        compression_frame = LabelFrame(root, text="Compression Details", padx=5, pady=5)
        compression_frame.pack(padx=10, pady=5, fill="both")
        self.codes_text = scrolledtext.ScrolledText(compression_frame, height=10, width=70)
        self.codes_text.pack()
        # Compress button
        self.compress_button = tk.Button(compression_frame, text="🔒 Compress File", command=self.compress_file, state=tk.DISABLED)
        self.compress_button.pack()
        # Compression details
        self.result_text = tk.Label(compression_frame, text="Compression details will appear here.", font=("Arial", 10), fg="blue")
        self.result_text.pack()
        # Progress bar
        self.progress_bar = ttk.Progressbar(compression_frame, orient=tk.HORIZONTAL, length=600, mode='determinate')
        self.progress_bar.pack(pady=5)
        # Decompression frame
        decompression_frame = LabelFrame(root, text="Decompression Details", padx=5, pady=5)
        decompression_frame.pack(padx=10, pady=5, fill="both")
        # Decompress button
        self.decompress_button = tk.Button(decompression_frame, text="🔓 Decompress File", command=self.decompress_file, state=tk.DISABLED)
        self.decompress_button.pack()
        # Decompressed text
        self.decoded_text = scrolledtext.ScrolledText(decompression_frame, height=8, width=70)
        self.decoded_text.pack()
        # Match status label
        self.match_label = tk.Label(decompression_frame, text="", font=("Arial", 10), fg="red")
        self.match_label.pack()
    # Select file
    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.file_path:
            self.status_label.config(text=f"Selected File: {self.file_path}")
            self.compress_button.config(state=tk.NORMAL)
    # Compress file
    def compress_file(self):
        with open(self.file_path, "r") as file:
            text = file.read()
         # Checks for empty
        if not text:
            messagebox.showerror("Error", "Empty file selected.")
            self.compress_button.config(state=tk.DISABLED)
            return
        # Checks for at least 1 character
        if len(text) == 1:
            messagebox.showerror("Error", "File contains only one character.")
            return
        # Build Huffman Tree and generate codes
        frequency = Counter(text)
        root_node = build_huffman_tree(frequency)
        codes = create_codes(root_node)
        encoded_bits = encode(text, codes)
        compressed_file = self.file_path + ".bin"
        meta_file = self.file_path + ".meta"
        # Save compressed file
        with open(compressed_file, "wb") as file:
            encoded_bits.tofile(file)
        # Save metadata
        with open(meta_file, "w") as meta:
            json.dump(codes, meta)
        messagebox.showinfo("Success", f"File compressed to {compressed_file} and metadata saved to {meta_file}")
        # Calculate compression ratio
        original_size = os.path.getsize(self.file_path)
        compressed_size = os.path.getsize(compressed_file)
        # Display compression details
        self.codes_text.delete(1.0, tk.END)
        for char, code in codes.items():
            self.codes_text.insert(tk.END, f"'{char}': {code}\n")
        # Display compression details
        self.result_text.config(text=f"Original: {original_size} bytes | Compressed: {compressed_size} bytes | Ratio: {100 - (compressed_size/original_size)*100:.2f}%")
        # Progress Bar
        for i in range(101):
            self.progress_bar['value'] = i
            self.progress_bar.update()
        # Enable decompress button
        self.decompress_button.config(state=tk.NORMAL)
    # Decompress file
    def decompress_file(self):
        compressed_file = self.file_path + ".bin"
        meta_file = self.file_path + ".meta"
        # Check if compressed file and metadata file exist
        with open(meta_file, "r") as meta:
            codes = json.load(meta)
        # Load compressed file
        with open(compressed_file, "rb") as file:
            encoded_bits = bitarray()
            encoded_bits.fromfile(file)
        # Decode text
        decoded_text = decode(encoded_bits, codes)
        # Load original text
        with open(self.file_path, "r") as original_file:
            original_text = original_file.read()
        # Check if decoded text matches original text
        match_status = "MATCH" if decoded_text == original_text else "DOES NOT MATCH"
        messagebox.showinfo("Success", f"Original text and decoded text {match_status}!")
        # Display decoded text and match status
        self.decoded_text.delete(1.0, tk.END)
        self.decoded_text.insert(tk.END, f"{decoded_text}\n")
        self.match_label.config(text=f"Match Status: {match_status}", fg="green" if match_status == "MATCH" else "red")

# Run GUI Application
if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanGUI(root)
    root.mainloop()
