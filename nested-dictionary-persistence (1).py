import json
import os

FILENAME = "nested_dictionary.json"

def load_data():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(FILENAME, 'w') as file:
        json.dump(data, file, indent=2)

def add_item(data, key):
    if key not in data:
        data[key] = {'next': [], 'text': []}
    
    choice = input(f"Add to 'next' or 'text' for key '{key}'? (n/t): ").lower()
    if choice == 'n':
        item = input("Enter item for 'next' list: ")
        data[key]['next'].append(item)
        if item not in data:
            data[item] = {'next': [], 'text': []}
    elif choice == 't':
        item = input("Enter item for 'text' list: ")
        data[key]['text'].append(item)
    else:
        print("Invalid choice. No item added.")

def show_key_info(data):
    key = input("Enter the key to display: ")
    if key in data:
        print(f"\nInformation for key '{key}':")
        print(json.dumps(data[key], indent=2))
    else:
        print(f"Key '{key}' not found in the data structure.")

def display_summary(data):
    print("\nCurrent keys in the data structure:")
    for key in data:
        next_count = len(data[key]['next'])
        text_count = len(data[key]['text'])
        print(f"- {key}: {next_count} next item(s), {text_count} text item(s)")

def main():
    data = load_data()
    
    while True:
        display_summary(data)
        
        action = input("\nEnter 'a' to add an item, 's' to show key info, 'q' to quit: ").lower()
        if action == 'q':
            break
        elif action == 'a':
            key = input("Enter the key: ")
            add_item(data, key)
        elif action == 's':
            show_key_info(data)
        else:
            print("Invalid action. Please try again.")
    
    save_data(data)
    print("Data saved. Goodbye!")

if __name__ == "__main__":
    main()
