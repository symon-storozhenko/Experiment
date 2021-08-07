import sys
import csv
from csv import DictReader, DictWriter
import datetime
from pathlib import Path

# with open('large_clients_accounts.csv', 'w') as outf_write:
#     writer = DictWriter(outf_write, fieldnames=['client', 'available', 'held', 'total', 'locked'])
#     writer.writeheader()
#     for enum, i in enumerate(range(65536), 1):
#         writer.writerow({'client': f'{enum}', 'available': '4.1', 'held': '1', 'total': '4.1', 'locked': 'false'})


with open('test_csv_files/10k_trxs.csv', 'w') as outf_write:
    writer = DictWriter(outf_write, fieldnames=['type', 'client', 'tx', 'amount'])
    writer.writeheader()
    for enum, i in enumerate(range(10000), 1):
        writer.writerow({'type': "deposit", 'client': f'{enum}', 'tx': f'{enum}', 'amount': '1'})
