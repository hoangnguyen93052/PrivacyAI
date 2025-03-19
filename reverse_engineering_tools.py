import os
import struct
import sys
import argparse
import binascii
from collections import defaultdict

class BinaryAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sections = {}
        self.strings = []

    def analyze(self):
        with open(self.file_path, 'rb') as f:
            data = f.read()
            self.extract_sections(data)
            self.extract_strings(data)

    def extract_sections(self, data):
        # This is a simplified example and only works with ELF binaries
        if data[:4] == b'\x7fELF':
            e_phoff = struct.unpack('I', data[28:32])[0]
            e_phentsize = struct.unpack('H', data[44:46])[0]
            e_phnum = struct.unpack('H', data[46:48])[0]
            for i in range(e_phnum):
                section_header = data[e_phoff + i * e_phentsize:e_phoff + (i + 1) * e_phentsize]
                self.sections[i] = section_header

    def extract_strings(self, data, length=4):
        self.strings = [s.decode('utf-8') for s in self.find_strings(data, length)]

    @staticmethod
    def find_strings(data, length):
        strings = []
        current_string = bytearray()
        for byte in data:
            if 32 <= byte < 127:  # printable ASCII range
                current_string.append(byte)
            else:
                if len(current_string) >= length:
                    strings.append(current_string)
                current_string.clear()
        return strings

    def print_analysis(self):
        print('Sections:')
        for idx, section in self.sections.items():
            print(f'Section {idx}: {section}')

        print('\nExtracted Strings:')
        for s in self.strings:
            print(s)


class HexDumper:
    def __init__(self, file_path):
        self.file_path = file_path

    def dump(self, bytes_per_line=16):
        with open(self.file_path, 'rb') as f:
            offset = 0
            while True:
                chunk = f.read(bytes_per_line)
                if not chunk:
                    break
                hex_str = ' '.join(f'{b:02x}' for b in chunk)
                print(f'{offset:08x}  {hex_str}')
                offset += len(chunk)


def main():
    parser = argparse.ArgumentParser(description='Reverse Engineering Tools')
    parser.add_argument('file', help='Path to the binary file to analyze')
    parser.add_argument('--dump', action='store_true', help='Dump the file in hex')
    parser.add_argument('--analyze', action='store_true', help='Analyze the binary file')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        print(f"Error: {args.file} is not a valid file.")
        sys.exit(1)

    if args.dump:
        dumper = HexDumper(args.file)
        dumper.dump()
    
    if args.analyze:
        analyzer = BinaryAnalyzer(args.file)
        analyzer.analyze()
        analyzer.print_analysis()


if __name__ == "__main__":
    main()