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
        print(f'trxs_reader -> {clients_account_dict}')

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
                        # deposit_trx()
                        deposit_amount = float(trx_row[3])
                        client_row.update({'available': f'{available + deposit_amount}',
                                           'total': f'{total + deposit_amount}'})
                        print(f'\ndeposit for client {client_row.get("client")} with'
                              f' ${float(trx_row[3])}')
                        print(client_row)
                        break
                    elif trx_type == 'withdrawal':
                        withdrawal_amount = float(trx_row[3])
                        client_row.update({'available': f'{available - withdrawal_amount}',
                                           'total': f'{total - withdrawal_amount}'})
                        print(f'\nwithdrawal for client {client_row.get("client")}  with '
                              f'${float(trx_row[3])}')
                        print(client_row)
                    elif trx_type == 'dispute':
                        with open(transactions) as dispute_loop:  # open a trxs file again to loop from beginning
                            dispute_reader = csv.reader(dispute_loop)
                            for dispute in dispute_reader:
                                if not dispute or dispute[0] == 'type':
                                    continue
                                if trx_row[2] == dispute[2]:
                                    # dispute_trx()
                                    dispute_amount = float(dispute[3])
                                    client_row.update({'available': f'{available - dispute_amount}',
                                                       'held': f'{held + dispute_amount}'})
                                    print(f'\ndispute for client {client_row.get("client")}:')
                                    print(client_row)
                                    break
                    elif trx_type == 'resolve':
                        with open(transactions) as resolve_loop:  # open a trxs file again to loop from beginning
                            resolve_reader = csv.reader(resolve_loop)
                            for resolve in resolve_reader:
                                if not resolve or resolve[0] == 'type':
                                    continue
                                if trx_row[2] == resolve[2]:
                                    # resolve_trx()
                                    resolve_amount = float(resolve[3])
                                    client_row.update({'available': f'{available + resolve_amount}',
                                                       'held': f'{held - resolve_amount}'})
                                    print(f'\nresolve for client {client_row.get("client")}:')
                                    print(client_row)
                                    break
                    elif trx_type == 'chargeback':
                        with open(transactions) as chargeback_loop:  # open a trxs file again to loop from beginning
                            chargeback_reader = csv.reader(chargeback_loop)
                            for chargeback in chargeback_reader:
                                if not chargeback or chargeback[0] == 'type':
                                    continue
                                if trx_row[2] == chargeback[2]:
                                    # chargeback_trx()
                                    chargeback_amount = float(chargeback[3])
                                    client_row.update({'available': f'{total + chargeback_amount}',
                                                       'held': f'{held - chargeback_amount}',
                                                       'locked': 'true'})
                                    print(f'\nchargeback for client {client_row.get("client")}:')
                                    print(client_row)
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
                print(f'\nNew client deposit for client {client_id_trx_file} with ${float(trx_row[3])}')
                print(clients_account_dict[-1])
            elif not client_exists and trx_type == 'withdrawal':
                if int(client_id_trx_file) > 65535:
                    raise OverflowError('{} contains a client id that exceeds u16 type '
                                        '(max 65535)'.format(transactions))
                clients_account_dict.append({'client': f'{client_id_trx_file}',
                                             'available': f'-{float(trx_row[3])}',
                                             'held': 0.0,
                                             'total': f'-{float(trx_row[3])}',
                                             'locked': 'false'})
                print(f'\nNew client withdrawal for client {client_id_trx_file} with ${float(trx_row[3])}')
                print(clients_account_dict[-1])

    return clients_account_dict


if __name__ == "__main__":
    clients_account_list = payment_engine(trxs_file, clients_accts)
    print("client,available,held,total,locked")
    for i in clients_account_list:
        print(f"{i.get('client')},"
              f"{float(i.get('available')):.4f},"
              f"{float(i.get('held')):.4f},"
              f"{float(i.get('total')):.4f},"
              f"{i.get('locked')}")