import struct

def hex_to_string(hex_value):
    return bytes.fromhex(hex_value).decode('utf-8')

def parse_partition_entry(data, offset):
    partition_entry = data[offset:offset+0x80]
    
    # Check if the entry is empty (00 00 at the beginning)
    if partition_entry[:2] == b'\x00\x00':
        return None, offset
    
    # Parse the fields in the partition entry
    partition_type_guid = partition_entry[0:16].hex()
    unique_partition_guid = partition_entry[16:32].hex()
    first_lba = struct.unpack('<Q', partition_entry[32:40])[0]
    last_lba = struct.unpack('<Q', partition_entry[40:48])[0]
    file_size = (last_lba - first_lba + 1) * 512  # Sector size is typically 512 bytes
    
    # Read 4 bytes from First LBA * sector size + 3 and convert to HEX string
    file_system_hex = data[(first_lba * 512) + 3:(first_lba * 512) + 7].hex()
    
    return {
        'partition_type_guid': partition_type_guid,
        'unique_partition_guid': unique_partition_guid,
        'first_lba': first_lba,
        'last_lba': last_lba,
        'file_size': file_size,
        'file_system_hex': file_system_hex
    }, offset + 0x80

def parse_partition_table(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    partition_entries = []
    offset = 0x400
    
    while True:
        entry, offset = parse_partition_entry(data, offset)
        if entry is None:
            break
        partition_entries.append(entry)
    
    return partition_entries

if __name__ == "__main__":
    filename = "gpt_128.dd"
    print("[Parsing \"", filename, "\"]")
    print("====================")
    partitions = parse_partition_table(filename)
    for idx, partition in enumerate(partitions):
        print(f"Partition {idx+1}:")
        print("Partition Type GUID:", partition['partition_type_guid'])
        print("Unique Partition GUID:", partition['unique_partition_guid'])
        print("First LBA:", partition['first_lba'])
        print("Last LBA:", partition['last_lba'])
        print("File Size:", partition['file_size'], "bytes")
        print("File System (HEX):", hex_to_string(partition['file_system_hex']))
        print("====================")
