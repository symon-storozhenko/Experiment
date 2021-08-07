from csv import DictReader

import pytest
from payment_engine import payment_engine

trxs_file = 'test_csv_files/transactions.csv'
regular_clients_accts = 'test_csv_files/client_accounts.csv'
clients_accts_with_id_65536 = 'test_csv_files/client_accounts_with_id_65536.csv'
trx_file_with_trx_id_4294967296 = 'test_csv_files/trxs_with_trx_id_4294967296.csv'
trx_file_with_client_id_65536 = 'test_csv_files/trxs_with_client_id_65536.csv'
tenk_trxs = 'test_csv_files/10k_trxs.csv'
clients_accts_with_65535_rows = 'test_csv_files/65k_clients_accounts.csv'


def test_overflowerror_raised_for_u16_in_clients_accts_file():
    with pytest.raises(OverflowError):
        payment_engine(trxs_file, clients_accts_with_id_65536)


def test_overflowerror_raised_for_u32_trx_id_in_trxs_file():
    with pytest.raises(OverflowError):
        payment_engine(trx_file_with_trx_id_4294967296, regular_clients_accts)


def test_overflowerror_raised_for_u16_client_id_in_trxs_file():
    with pytest.raises(OverflowError):
        payment_engine(trx_file_with_client_id_65536, regular_clients_accts)


def test_new_clients_are_created_with_deposit_n_withdrawal_trxs():
    with open(regular_clients_accts) as clients_accts:
        custs_accts_reader = DictReader(clients_accts)
        clients_account_list = list(custs_accts_reader)
        for client_row in clients_account_list:
            assert int(client_row.get('client')) != 4
            assert int(client_row.get('client')) != 5
        new_clients_account_list = payment_engine(trxs_file, regular_clients_accts)
        client_ids = []
        for client_row in new_clients_account_list:
            client_ids.append(int(client_row.get('client')))
        assert 4 in client_ids
        assert 5 in client_ids


def test_engine_doesnt_crash_with_10k_trx_file_and_65k_clients_accts_file():
    large_clients_accts_list = payment_engine(tenk_trxs, clients_accts_with_65535_rows)
    assert len(large_clients_accts_list) < 65537


