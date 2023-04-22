# SQLiteStorage

> ⚠ The code is not ready yet for use!
> You can contribute.

Simple aiogram FSM storage, stores all data in SQLite database

Intended to replace MemoryStorage for simple cases where you want to keep states between bot restarts.

Implements just [basic BaseStorage methods](https://docs.aiogram.dev/en/dev-3.x/dispatcher/finite_state_machine/storages.html#aiogram.fsm.storage.base.BaseStorage) such as:

- set_state()
- get_state()
- set_data()
- get_data()
- update_data()
- close()

Tests are based on [original aiogram tests](https://github.com/aiogram/aiogram/blob/master/tests/test_contrib/test_fsm_storage/test_storage.py).
