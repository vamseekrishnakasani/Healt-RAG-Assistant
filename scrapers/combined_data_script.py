import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "../data/who_facts.json"), "r", encoding="utf-8") as f1, \
     open(os.path.join(base_dir, "../data/mayo_conditions.json"), "r", encoding="utf-8") as f2:
    who_data = json.load(f1)
    mayo_data = json.load(f2)

combined_data = who_data + mayo_data

with open(os.path.join(base_dir, "../data/combined_health_data.json"), "w", encoding="utf-8") as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=2)