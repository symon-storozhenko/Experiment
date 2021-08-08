import sys
import csv
from csv import DictReader

clients_accts = 'client_accounts.csv'
trxs_file = 'transactions.csv'


def payment_engine(transactions, clients_accounts):
    with open(transactions) as inf, open(clients_accounts) as outf:
        trxs_reader = csv.reader(inf)
        custs_accts_reader = DictReader(outf)
        clients_account_dict = list(custs_accts_reader)  # load clients_accounts.csv into a list of dicts

        for record in clients_account_dict:
            if int(record.get('client')) > 65535:
                raise OverflowError('{} contains client id(s) that exceeds u16 type '
                                    '(max 65535)'.format(clients_accounts))

        for e, trx_row in enumerate(trxs_reader):
            if not trx_row or trx_row[0] == 'type':
                continue
            if int(trx_row[2]) > 4294967295:
                raise OverflowError('{} contains trx id(s) that exceeds u32 type'
                                    ' (max 4294967295)'.format(transactions))
            client_exists = False
            trx_type = trx_row[0].lower()
            client_id_trx_file = int(trx_row[1])
            tx_id = int(trx_row[2])
            # type,       client,tx,  amount -- Some visual aid with trx_row list and indexes
            # ['deposit', '5',  '33', '5']
            for client_row in clients_account_dict:
                client_id_accts_file = int(client_row.get('client'))
                available = float(client_row.get('available'))
                held = float(client_row.get('held'))
                total = float(client_row.get('total'))
                if client_id_trx_file == client_id_accts_file:
                    client_exists = True
                    if client_row.get('locked').lower() == 'true':
                        break
                    if trx_type == 'deposit':
                        deposit_amount = float(trx_row[3])
                        client_row.update({'available': f'{available + deposit_amount}',
                                           'total': f'{total + deposit_amount}'})
                        break
                    elif trx_type == 'withdrawal':
                        withdrawal_amount = float(trx_row[3])
                        client_row.update({'available': f'{available - withdrawal_amount}',
                                           'total': f'{total - withdrawal_amount}'})
                    elif trx_type == 'dispute':
                        with open(transactions) as dispute_loop:  # open a trxs file again to loop from beginning
                            dispute_reader = csv.reader(dispute_loop)
                            for dispute in dispute_reader:
                                if not dispute or dispute[0] == 'type':
                                    continue
                                if trx_row[2] == dispute[2]:
                                    dispute_amount = float(dispute[3])
                                    client_row.update({'available': f'{available - dispute_amount}',
                                                       'held': f'{held + dispute_amount}'})
                                    break
                    elif trx_type == 'resolve':
                        with open(transactions) as resolve_loop:  # open a trxs file again to loop from beginning
                            resolve_reader = csv.reader(resolve_loop)
                            under_dispute = False
                            resolve_amount = 0
                            for resolve in resolve_reader:
                                if not resolve or resolve[0].lower() == 'type':
                                    continue
                                if trx_row[2] == resolve[2] and resolve[0].lower() == 'deposit' or \
                                        resolve[0].lower() == 'withdrawal':
                                    under_dispute = True
                                    resolve_amount = float(resolve[3])
                                if under_dispute and trx_row[2] == resolve[2] and resolve[0].lower() == 'dispute':
                                    client_row.update({'available': f'{available + resolve_amount}',
                                                       'held': f'{held - resolve_amount}'})
                                    break
                    elif trx_type == 'chargeback':
                        with open(transactions) as chargeback_loop:  # open a trxs file again to loop from beginning
                            chargeback_reader = csv.reader(chargeback_loop)
                            chargeback_under_dispute = False
                            chargeback_amount = 0
                            for chargeback in chargeback_reader:
                                if not chargeback or chargeback[0].lower() == 'type':
                                    continue
                                if trx_row[2] == chargeback[2] and chargeback[0].lower() == 'deposit' or \
                                        chargeback[0].lower() == 'withdrawal':
                                    chargeback_under_dispute = True
                                    chargeback_amount = float(chargeback[3])
                                if chargeback_under_dispute and trx_row[2] == chargeback[2] \
                                        and chargeback[0].lower() == 'dispute':
                                    client_row.update({'total': f'{total - chargeback_amount}',
                                                       'held': f'{held - chargeback_amount}',
                                                       'locked': 'true'})
                                    break
            if not client_exists and trx_type == 'deposit':
                if int(client_id_trx_file) > 65535:
                    raise OverflowError('{} contains a client id that exceeds u16 type '
                                        '(max 65535)'.format(transactions))
                clients_account_dict.append({'client': f'{client_id_trx_file}',
                                             'available': f'{float(trx_row[3])}',
                                             'held': 0.0,
                                             'total': f'{float(trx_row[3])}',
                                             'locked': 'false'})
            elif not client_exists and trx_type == 'withdrawal':
                if int(client_id_trx_file) > 65535:
                    raise OverflowError('{} contains a client id that exceeds u16 type '
                                        '(max 65535)'.format(transactions))
                clients_account_dict.append({'client': f'{client_id_trx_file}',
                                             'available': f'-{float(trx_row[3])}',
                                             'held': '0.0',
                                             'total': f'-{float(trx_row[3])}',
                                             'locked': 'false'})
    return clients_account_dict

if __name__ == "__main__":
    # Change sys.argv[1] to trx.csv file name (or path) if you want to run from IDE runner
    clients_account_list = payment_engine(transactions=sys.argv[1], clients_accounts=clients_accts)
    print("client,available,held,total,locked")
    for i in clients_account_list:
        print(f"{i.get('client')},"
              f"{float(i.get('available')):.4f},"
              f"{float(i.get('held')):.4f},"
              f"{float(i.get('total')):.4f},"
              f"{i.get('locked')}")