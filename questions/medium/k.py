import os
import json

def main():
    base_path = os.getcwd()  # Change this if needed
    for i in range(1, 65):  # Q1 to Q10
        folder_name = f'question{i}'
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            files = os.listdir(folder_path)
            if len(files) == 1 and files[0] == "config.json":
                config_path = os.path.join(folder_path, "config.json")
                with open(config_path, "r") as file:
                    data = json.load(file)
                    if "conclusion" in data.get("question_text", "").lower():
                        print(folder_name)

if __name__ == "__main__":
    main()
