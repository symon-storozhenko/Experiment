import pandas as pd
import numpy as np
import csv
from csv import DictReader, DictWriter
import datetime
from pathlib import Path

with open('large_trxs.csv') as inf, open('client_accounts.csv') as outf, \
        open('clients_accounts.csv', 'w', newline="") as outf_write:
    trxs_reader = csv.reader(inf)
    custs_accts_reader = DictReader(outf)
    output = list(custs_accts_reader)
    catts_read = pd.DataFrame(output)

    # df = pd.DataFrame(output)
    # print(df)
    print("Dict before:")
    # for i in output:
    #     print(i)
    # for e, trx_line in enumerate(trxs_reader):
    #     print(f'line -> {e}')


    for e, trx_line in enumerate(trxs_reader):
        print(f'line -> {e}')
        if trx_line[0] == 'type':
            continue
        for row in output:
            if trx_line[1].lower() == row.get('client'):
                if trx_line[0].lower() == 'deposit':
                    row.update({'client': f'{row["client"]}',
                                'available': f'{float(row["available"]) + float(trx_line[3])}',
                                'total': f'{float(row["total"]) + float(trx_line[3])}'})

                    print(f'\ndeposit for client {row.get("client")}:')
                    print(row)
                elif trx_line[0].lower() == 'withdrawal':
                    row.update({'client': f'{row["client"]}',
                                'available': f'{float(row["available"]) - float(trx_line[3])}',
                                'held': f'{row["held"]}',
                                'total': f'{float(row["total"]) - float(trx_line[3])}',
                                'locked': f'{row["locked"]}'})
                    print(f'\nwithdrawal for client {row.get("client")}:')
                    print(row)
                elif trx_line[0].lower() == 'dispute':
                    for dispute in trxs_reader:
                        if trx_line[2] == dispute[2]:
                            amount = dispute[3]
                            row.update({'client': f'{row["client"]}',
                                        'available': f'{float(row["available"]) - float(amount)}',
                                        'held': f'{float(row["held"]) + float(amount)}'})
                            print(f'\ndispute for client {row.get("client")}:')
                            print(row)
                elif trx_line[0].lower() == 'resolve':
                    for dispute in trxs_reader:
                        if trx_line[2] == dispute[2]:
                            amount = dispute[3]
                            row.update({'client': f'{row["client"]}',
                                        'available': f'{float(row["available"]) + float(amount)}',
                                        'held': f'{float(row["held"]) - float(amount)}'})
                            print(f'\nresolve for client {row.get("client")}:')
                            print(row)
                elif trx_line[0].lower() == 'chargeback':
                    for dispute in trxs_reader:
                        if trx_line[2] == dispute[2]:
                            amount = dispute[3]
                            row.update({'client': f'{row["client"]}',
                                        'available': f'{float(row["total"]) + float(amount)}',
                                        'held': f'{float(row["held"]) - float(amount)}',
                                        'locked': 'true'})
                            print(f'\nchargeback for client {row.get("client")}:')
                            print(row+'\n')
                break

        print("Dicts after:")
        for i in output:
            print(i)

print(f"The value of n is {n:.4f}")
