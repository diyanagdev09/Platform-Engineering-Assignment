
from agent import research
import json


question = input("Enter your research question: ")

report = research(question)

print("\n=== FINAL RESEARCH REPORT ===")
print(json.dumps(report, indent=2, ensure_ascii=False))
