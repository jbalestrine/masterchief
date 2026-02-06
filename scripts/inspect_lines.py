import sys
path = sys.argv[1]
start = int(sys.argv[2])
end = int(sys.argv[3])
with open(path, 'rb') as f:
    lines = f.read().splitlines()
for i in range(start-1, min(end, len(lines))):
    print(f"{i+1}: {lines[i]!r}")
