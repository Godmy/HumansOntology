
import re
import json

def parse_line(line):
    """
    Parses a single line to extract id, name, and characteristic.
    """
    # Regex to capture: 1. id, 2. name, 3. min_range, 4. max_range (optional)
    match = re.match(r'^([\d\.]+)\s*(.*?)\s*(?:\((\d+)(?:-(\d+))?\))?$', line)
    if not match:
        return None

    groups = match.groups()
    
    node_id = groups[0]
    name = groups[1].strip()
    min_val = groups[2]
    max_val = groups[3]

    characteristic = None
    if min_val:
        min_val = int(min_val)
        if max_val:
            max_val = int(max_val)
        else:
            max_val = min_val
        characteristic = {"min": min_val, "max": max_val}

    return {
        "id": node_id,
        "name": name,
        "characteristic": characteristic,
        "children": []
    }

def build_tree(nodes):
    """
    Builds a nested tree structure from a flat list of nodes.
    """
    tree = []
    # A dictionary to keep track of nodes at each level
    parent_map = {}

    for node in nodes:
        node_id = node['id']
        # Level is the number of dots in the id
        level = node_id.count('.') -1

        if level == 0:
            tree.append(node)
            parent_map[level] = node
        else:
            parent_level = level - 1
            if parent_level in parent_map:
                parent_map[parent_level]['children'].append(node)
            
            parent_map[level] = node
            
    return tree

def main():
    """
    Main function to parse the source file and generate JSON.
    """
    with open('source.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    nodes = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parsed_node = parse_line(line)
        if parsed_node:
            nodes.append(parsed_node)

    tree = build_tree(nodes)

    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
