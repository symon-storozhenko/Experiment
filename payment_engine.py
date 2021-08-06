import sys
import csv
from csv import DictReader, DictWriter
import datetime
from pathlib import Path

with open('transactions.csv') as inf, open('client_accounts.csv') as outf:
    trxs_reader = csv.reader(inf)
    custs_accts_reader = DictReader(outf)
    output = list(custs_accts_reader)

    for e, trx_line in enumerate(trxs_reader):
        if trx_line[0] == 'type':
            continue
        for row in output:
            if trx_line[1].lower() == row.get('client'):
                if row.get('locked').lower() == 'true':
                    break
                if trx_line[0].lower() == 'deposit':
                    row.update({'client': f'{row["client"]}',
                                'available': f'{float(row["available"]) + float(trx_line[3])}',
                                'total': f'{float(row["total"]) + float(trx_line[3])}'})

                    print(f'\ndeposit for client {row.get("client")} with ${float(trx_line[3])}')
                    print(row)
                    break
                elif trx_line[0].lower() == 'withdrawal':
                    row.update({'client': f'{row["client"]}',
                                'available': f'{float(row["available"]) - float(trx_line[3])}',
                                'held': f'{row["held"]}',
                                'total': f'{float(row["total"]) - float(trx_line[3])}',
                                'locked': f'{row["locked"]}'})
                    print(f'\nwithdrawal for client {row.get("client")}:')
                    print(row)
                elif trx_line[0].lower() == 'dispute':
                    with open('transactions.csv') as dispute_loop:
                        dispute_reader = csv.reader(dispute_loop)
                        for dispute in dispute_reader:
                            if trx_line[2] == dispute[2]:
                                amount = dispute[3]
                                row.update({'client': f'{row["client"]}',
                                            'available': f'{float(row["available"]) - float(amount)}',
                                            'held': f'{float(row["held"]) + float(amount)}'})
                                print(f'\ndispute for client {row.get("client")}:')
                                print(row)
                                break
                elif trx_line[0].lower() == 'resolve':
                    with open('transactions.csv') as resolve_loop:
                        resolve_reader = csv.reader(resolve_loop)
                        for resolve in resolve_reader:
                            if trx_line[2] == resolve[2]:
                                amount = resolve[3]
                                row.update({'client': f'{row["client"]}',
                                            'available': f'{float(row["available"]) + float(amount)}',
                                            'held': f'{float(row["held"]) - float(amount)}'})
                                print(f'\nresolve for client {row.get("client")}:')
                                print(row)
                                break
                elif trx_line[0].lower() == 'chargeback':
                    with open('transactions.csv') as chargeback_loop:
                        chargeback_reader = csv.reader(chargeback_loop)
                        for chargeback in chargeback_reader:
                            if trx_line[2] == chargeback[2]:
                                amount = chargeback[3]
                                row.update({'client': f'{row["client"]}',
                                            'available': f'{float(row["total"]) + float(amount)}',
                                            'held': f'{float(row["held"]) - float(amount)}',
                                            'locked': 'true'})
                                print(f'\nchargeback for client {row.get("client")}:')
                                print(row)
                                break
                else:
                    output.append({'client': f'{trx_line[1]}',
                                   'available': f'{trx_line[3]}',
                                   'held': '0',
                                   'total': f'{trx_line[3]}',
                                   'locked': 'false'})

    print("client,available,held,total,locked")
    for i in output:
        print(f"{i.get('client')},"
              f"{float(i.get('available')):.4f},"
              f"{float(i.get('held')):.4f},"
              f"{float(i.get('total')):.4f},"
              f"{i.get('locked')}")

print(f"The value of n is {8.098976:g}")
