import os
import heapq
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, LabelFrame
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

        self.file_path = ""
        
        tk.Label(root, text="📚 Huffman Coding Compression Tool", font=("Arial", 16)).pack()
        
        self.select_button = tk.Button(root, text="📂 Select Text File", command=self.select_file)
        self.select_button.pack()
        self.status_label = tk.Label(root, text="No file selected", font=("Arial", 10))
        self.status_label.pack()
        
        compression_frame = LabelFrame(root, text="Compression Details", padx=5, pady=5)
        compression_frame.pack(padx=10, pady=5, fill="both")
        
        self.codes_text = scrolledtext.ScrolledText(compression_frame, height=10, width=70)
        self.codes_text.pack()
        
        self.compress_button = tk.Button(compression_frame, text="🔒 Compress File", command=self.compress_file, state=tk.DISABLED)
        self.compress_button.pack()
        
        self.result_text = tk.Label(compression_frame, text="Compression details will appear here.", font=("Arial", 10), fg="blue")
        self.result_text.pack()
        
        decompression_frame = LabelFrame(root, text="Decompression Details", padx=5, pady=5)
        decompression_frame.pack(padx=10, pady=5, fill="both")
        
        self.decompress_button = tk.Button(decompression_frame, text="🔓 Decompress File", command=self.decompress_file, state=tk.DISABLED)
        self.decompress_button.pack()
        
        self.decoded_text = scrolledtext.ScrolledText(decompression_frame, height=8, width=70)
        self.decoded_text.pack()
        
        self.match_label = tk.Label(decompression_frame, text="", font=("Arial", 10), fg="red")
        self.match_label.pack()

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.file_path:
            self.status_label.config(text=f"Selected File: {self.file_path}")
            self.compress_button.config(state=tk.NORMAL)

    def compress_file(self):
        with open(self.file_path, "r") as file:
            text = file.read()
        
        frequency = Counter(text)
        root_node = build_huffman_tree(frequency)
        codes = create_codes(root_node)
        encoded_bits = encode(text, codes)
        compressed_file = self.file_path + ".bin"
        meta_file = self.file_path + ".meta"
        
        with open(compressed_file, "wb") as file:
            encoded_bits.tofile(file)
        
        with open(meta_file, "w") as meta:
            json.dump(codes, meta)
        
        original_size = os.path.getsize(self.file_path)
        compressed_size = os.path.getsize(compressed_file)
        
        self.codes_text.delete(1.0, tk.END)
        for char, code in codes.items():
            self.codes_text.insert(tk.END, f"'{char}': {code}\n")
        
        self.result_text.config(text=f"Original: {original_size} bytes | Compressed: {compressed_size} bytes | Ratio: {compressed_size/original_size*100:.2f}%")
        
        self.decompress_button.config(state=tk.NORMAL)

    def decompress_file(self):
        compressed_file = self.file_path + ".bin"
        meta_file = self.file_path + ".meta"
        
        with open(meta_file, "r") as meta:
            codes = json.load(meta)
        
        with open(compressed_file, "rb") as file:
            encoded_bits = bitarray()
            encoded_bits.fromfile(file)
        
        decoded_text = decode(encoded_bits, codes)
        
        with open(self.file_path, "r") as original_file:
            original_text = original_file.read()
        
        match_status = "MATCHES" if decoded_text == original_text else "DOES NOT MATCH"
        
        self.decoded_text.delete(1.0, tk.END)
        self.decoded_text.insert(tk.END, f"{decoded_text}\n")
        self.match_label.config(text=f"Match Status: {match_status}", fg="green" if match_status == "MATCHES" else "red")

# Run GUI Application
if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanGUI(root)
    root.mainloop()
