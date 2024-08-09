import os
import json

INPUT_DIR = '/Users/johnday/repos/storm/data/output'


def find_json_files(input_dir):
    json_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file == 'url_to_info.json':
                json_files.append(os.path.join(root, file))
    return json_files

def process_file(data_json) -> str:
    url_to_unified_index = data_json['url_to_unified_index']
    url_to_info = data_json['url_to_info']
    # loop through the index and get the references
    refs = []
    for key in url_to_unified_index:
        seq = int(url_to_unified_index[key])
        seq = f'{seq:02}'
        title = url_to_info[key]['title']
        refs.append(f'{seq}. [{title}]("{key}")')
    refs.sort()
    return "\n".join(refs)

def load_and_create_files(json_files):
    for file in json_files:
        with open(file, 'r') as f:
            data = json.load(f)

        new_file_path = os.path.join(os.path.dirname(file), 'references.txt')
        with open(new_file_path, 'w') as new_f:
            new_f.write(process_file(data))


if __name__ == "__main__":
    json_files = find_json_files(INPUT_DIR)
    load_and_create_files(json_files)
