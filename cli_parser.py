import sys
import csv
from csv import DictReader, DictWriter
import datetime
from pathlib import Path

list_of_dict = []
try:
    filename = sys.argv[1]
    with open(filename, mode='r', encoding='utf-8-sig') as read_obj:
        dict_reader = DictReader(read_obj)
        list_of_dict = list(dict_reader)
except FileNotFoundError as e:
    print(f"{datetime.datetime.now()} - {filename} file not found")


# Iterate over the dicts
for i in list_of_dict:
    print(f'with function -> {i}')
    if i['type'] == 'deposit':
        print('deposit!! YAy!')

# output = sys.argv[3]
path = Path.home() / "testo.csv"
with open(path, mode='w', encoding='utf-8-sig') as cust_accts:
    # d = DictWriter(cust_accts)
    pass
