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


def test_new_clients_are_not_created_with_dispute_resolve_and_chargeback_trxs():
    # type, client, tx, amount
    # dispute, 33, 33, 255
    # resolve, 11, 1133
    # chargeback, 22, 2,
    # Note: clients 11, 22 and 33 do not exist in clients_accounts.csv
    with open(regular_clients_accts) as clients_accts:
        custs_accts_reader = DictReader(clients_accts)
        clients_account_list = list(custs_accts_reader)
        for client_row in clients_account_list:
            assert int(client_row.get('client')) != 11
            assert int(client_row.get('client')) != 22
            assert int(client_row.get('client')) != 33
        new_clients_account_list = payment_engine(trxs_file, regular_clients_accts)
        client_ids = []
        for client_row in new_clients_account_list:
            client_ids.append(int(client_row.get('client')))
        assert 11 not in client_ids
        assert 22 not in client_ids
        assert 33 not in client_ids


@pytest.mark.skip("takes 30 sec to run")
def test_engine_doesnt_crash_with_10k_trx_file_and_65k_clients_accts_file():
    large_clients_accts_list = payment_engine(tenk_trxs, clients_accts_with_65535_rows)
    assert len(large_clients_accts_list) < 65537


def test_available_and_total_funds_increased_after_deposit():
    # available 1.0, total 1.0 + 2.0
    with open(regular_clients_accts) as clients_accts:
        custs_accts_reader = DictReader(clients_accts)
        clients_account_list = list(custs_accts_reader)
        for client_row in clients_account_list:
            if int(client_row.get('client')) == 1:
                assert client_row.get('available') == '1'
                assert client_row.get('total') == '1'
        new_clients_account_list = payment_engine(trxs_file, regular_clients_accts)
        for client_row in new_clients_account_list:
            if int(client_row.get('client')) == 1:
                assert client_row.get('available') == '3.0'
                assert client_row.get('total') == '3.0'
                assert client_row.get('held') == '0'


def test_available_and_total_funds_decreased_after_deposit():
    # available 3.5, total 3, held 1 + 2.0 deposit - 3.0 withdrawal = 2.5, 2.0, 1 held
    with open(regular_clients_accts) as clients_accts:
        custs_accts_reader = DictReader(clients_accts)
        clients_account_list = list(custs_accts_reader)
        for client_row in clients_account_list:
            if int(client_row.get('client')) == 2:
                assert client_row.get('available') == '3.5'
                assert client_row.get('total') == '3'
        new_clients_account_list = payment_engine(trxs_file, regular_clients_accts)
        for client_row in new_clients_account_list:
            if int(client_row.get('client')) == 2:
                assert client_row.get('available') == '2.5'
                assert client_row.get('total') == '2.0'
                assert client_row.get('held') == '1'


def test_dispute():
    # available 5, held 6, total 7 + 500.0 deposit, then dispute this trx:
    # 505, 6, 507 => 5, 506, 507
    new_clients_account_list = payment_engine(trxs_file, regular_clients_accts)
    for client_row in new_clients_account_list:
        if int(client_row.get('client')) == 3:
            assert client_row.get('available') == '5.0'
            assert client_row.get('total') == '507.0'
            assert client_row.get('held') == '506.0'


def test_resolve():
    # available 5, held 6, total 7 + 500.0 deposit, then dispute this trx, then resolve dispute:
    # 505, 6, 507 => 5, 506, 507 => 505, 6, 507
    clients_account_list = payment_engine(trxs_file, regular_clients_accts)
    for client_row in clients_account_list:
        if int(client_row.get('client')) == 71:
            assert client_row.get('available') == '505.0'
            assert client_row.get('held') == '6.0'
            assert client_row.get('total') == '507.0'


def test_resolve_doesnt_occur_if_there_was_no_dispute():
    # avail 2.5, total 2.0, 1 held -> then try to resolve a deposit trx_id 772 (without dispute)
    clients_account_list = payment_engine(trxs_file, regular_clients_accts)
    for client_row in clients_account_list:
        if int(client_row.get('client')) == 2:
            assert client_row.get('available') == '2.5'
            assert client_row.get('total') == '2.0'
            assert client_row.get('held') == '1'


def test_chargeback_and_make_sure_client_id_is_locked():
    # new customer:
    # type,       client, tx,  amount
    # deposit,   72,      773, 500.0
    # dispute,   72,      773,
    # chargeback,72,      773,
    # deposit,   72,      7730, 750.0
    new_clients_account_list = payment_engine(trxs_file, regular_clients_accts)
    for client_row in new_clients_account_list:
        if int(client_row.get('client')) == 72:
            assert client_row.get('available') == '0.0'
            assert client_row.get('held') == '0.0'
            assert client_row.get('total') == '0.0'


def test_negative_balance_calculates_properly():
    # new customer:
    # type,       client, tx,  amount
    # withdrawal, 73,     774, 500.0
    # deposit,    73,     775, 750
    new_clients_account_list = payment_engine(trxs_file, regular_clients_accts)
    for client_row in new_clients_account_list:
        if int(client_row.get('client')) == 73:
            assert client_row.get('available') == '250.0'
            assert client_row.get('held') == '0.0'
            assert client_row.get('total') == '250.0'