import sys
import csv

try:
    if sys.argv[1] == '-':
        f = sys.stdin.read().splitlines()
    else:
        filename = sys.argv[1]
        f = open(filename, 'r')
    csv = csv.reader(f)
    data = list(csv)
    for row in data:
        print(row)
except Exception as e:
    print("Error Reading from file:")