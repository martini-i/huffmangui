import os
import heapq
from collections import Counter

class Node:
    def __init__(self, freq, char=None, left=None, right=None): #node class for building huffman tree
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

# function to build Huffman Tree
def build_huffman_tree(text):
    frequency = Counter(text) # count frequency of each character
    heap = [Node(freq, char) for char, freq in frequency.items()] # create a node for each character
    heapq.heapify(heap) # create a min heap

    while len(heap) > 1: # merge nodes until only one node is left
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)

    return heap[0]

# recursive function to generate Huffman Code
def create_codes(node, current_code="", codes={}):
    if node.char:
        codes[node.char] = current_code
        return
    create_codes(node.left, current_code + "0", codes)
    create_codes(node.right, current_code + "1", codes)
    return codes

# encode text using Huffman Codes
def encode(text, codes):
    return ''.join(codes[char] for char in text)

# decode Huffman encoded text
def decode(encoded_text, codes):
    reverse_codes = {code: char for char, code in codes.items()}
    current_code = ""
    decoded_text = ""
    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ""
    return decoded_text

# # test case
# text = "Huffman coding is a lossless data compression algorithm. It is used in various applications including file compression formats like ZIP. The algorithm follows a greedy approach by assigning variable-length codes to characters, ensuring optimal encoding efficiency."
# print("Original text:", text)

# # print encoded text
# root = build_huffman_tree(text)
# codes = create_codes(root)
# encoded_text = encode(text, codes)

# #print each character and its code
# for char, code in codes.items():
#     print(f"{char}: {code}")

# # print decoded text
# decoded_text = decode(encoded_text, codes)
# print("Decoded text:", decoded_text)

# GUI Implementation