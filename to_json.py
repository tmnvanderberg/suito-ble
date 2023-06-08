import re
import json

def is_type(str,type):
        return str.startswith(type) or str.startswith(type.lower())

def parse_input_file(file_path):
    data = []
    
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]

    i = 0
    primary_service = []
    characteristic = []
    while i < len(lines):
        if primary_service != []:
            data.append(primary_service) # store previous

        if is_type(lines[i], "Primary Service"):
            primary_service = {
                'type': 'primary service',
                'path': lines[i+1],
                'uuid': lines[i+2],
                'description': lines[i+3],
                'characteristics': []
            }
            i += 4
            while i < len(lines) and not is_type(lines[i], "Primary Service"):
                if is_type(lines[i], "Characteristic"):
                    characteristic = {
                        'type': 'characteristic',
                        'path': lines[i+1],
                        'uuid': lines[i+2],
                        'description': lines[i+3]
                    }
                    primary_service['characteristics'].append(characteristic)
                    i += 4
                    if is_type(lines[i], "Descriptor"): # single descriptor MAY follow characteristic
                        descriptor = {
                            'type': 'descriptor',
                            'path': lines[i+1],
                            'uuid': lines[i+2],
                            'description': lines[i+3]
                        }
                        characteristic['descriptor'] = descriptor
                        i += 4

    data.append(primary_service)
    return data

def convert_to_json(data):
    return json.dumps(data, indent=4)

file_path = 'input.txt'
data = parse_input_file(file_path)
json_data = convert_to_json(data)
with open('output.json', 'w') as file:
    json.dump(data, file, indent=4)
