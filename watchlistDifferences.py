# Read items from file1.txt
with open('MinerviniWatchlist_9ec38.txt', 'r') as file1:
    items1 = file1.read().strip().split(',')

# Read items from file2.txt
with open('MinerviniWatchlist_cc7b1.txt', 'r') as file2:
    items2 = file2.read().strip().split(',')

# Convert lists to sets for easy comparison
set1 = set(items1)
set2 = set(items2)

# Find items that are not common in both lists
unique_items = list(set1.symmetric_difference(set2))

print("Items not common in both lists:", unique_items)


# Find common items between the sets
common_items = set1.intersection(set2)

# Remove common items from the original lists
updated_items1 = [item for item in items1 if item not in common_items]
updated_items2 = [item for item in items2 if item not in common_items]

# Write the updated lists back to the files
with open('MinerviniWatchlist_9ec38.txt', 'w') as file1:
    file1.write(','.join(updated_items1))

with open('MinerviniWatchlist_cc7b1.txt', 'w') as file2:
    file2.write(','.join(updated_items2))

print("Common items removed and files updated.")