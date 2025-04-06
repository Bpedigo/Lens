import os
from pathlib import Path



class PromptHandler:
    def __init__(self):
        self.prompts_dir = Path("prompts")
        self.prompts_dir.mkdir(exist_ok=True)

    def read_file(self, filename):
        try:
            with open(self.prompts_dir / filename, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return ""

    def read_file_to_array(self, filename):
        try:
            with open(self.prompts_dir / filename, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return [p.strip() for p in content.split("--------") if p.strip()]
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return []

    # Example usage
    # blocks = read_file_to_array("example.txt")
    # for index, block in enumerate(blocks):
    #     print(f"Block {index}:\n{block}\n")

