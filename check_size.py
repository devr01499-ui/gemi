import os

total_size = 0
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith(('.py', '.txt', '.json', '.md')):
            total_size += os.path.getsize(os.path.join(root, file))

print(f'Total size of deployable files: {total_size / (1024*1024):.2f} MB')
