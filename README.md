
### ****PAYMENT_ENGINE.PY****

Download payment_engine.py into the same directory with sample
*clients_accounts.csv* and *transactions.csv* files.

**Then run:**

`python payment_engine.py transactions.csv > clients_accounts.csv `

_Note: the script will overwrite the clients_accounts.csv file. Output to a new .csv file if the overwriting is unwanted_

**Coverage**

The engine covers all transaction types and outputs the result to the stdout.
If *transactions.csv* has a new ****client_id**** that *clients_accounts.csv*
doesn't have, the engine will create a new record, given the 
transaction type is either deposit or withdrawal.

**Efficiency**

The script will stream through the *transactions.csv* file line-by-line, which allows 
to process millions of records without crashing the system.



**Correctness**

The engine was tested against several sample csv files. It catches Overflow errors if trx_id or client_id exceed 
u32 or u16 type bounds respectively.

Around a dozen of positive and negative
unit tests were written to validate each transaction type, 
negative balances and creation of new clients
