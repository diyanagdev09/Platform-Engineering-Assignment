
from tools import search_wikipedia, search_openalex

query = "retrieval augmented generation"

print("\n--- WIKIPEDIA RESULTS ---")
print(search_wikipedia(query))

print("\n--- OPENALEX RESULTS ---")
print(search_openalex(query))
