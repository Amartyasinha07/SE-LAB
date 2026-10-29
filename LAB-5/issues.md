# Issues Found and Fixed — `restaurant_order_system.py`

Tools: Pylint 4.1.3, Bandit 1.9.4, Flake8 (Python 3.12).
Line numbers refer to the **original** file. Raw reports are in `reports/before/` and `reports/after/`.

| Metric | Before | After |
|--------|--------|-------|
| Pylint score | 4.81/10 | **10.00/10** |
| Bandit issues | 5 (High 2, Medium 1, Low 2) | **0** |
| Flake8 violations | 9 | **0** |

## Issue table (high and medium severity first)

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | Shell command injection (Bandit B605, High) | Security | 58 | `os.system("echo ... " + filename)` runs a shell with an unsanitised filename. A name such as `x; rm -rf ~` would execute arbitrary commands. It also wrote to stdout outside Python's buffer, so "Ticket sent…" printed **first**, out of order. | Replaced with a plain `print()`. No shell is needed just to show a message. |
| 2 | Weak MD5 hash (Bandit B324, High) | Security | 47 | MD5 is broken (practical collisions) and must not be used to identify tickets. | Switched to `hashlib.sha256`. |
| 3 | Use of `eval` (Bandit B307 Medium / Pylint W0123) | Security | 42 | `eval(promo_expr)` executes any Python string passed in, e.g. `__import__('os').system(...)`. | Replaced the expression string with a numeric `discount_percent` argument, validated to the range 0–100 (otherwise `ValueError`). The bill is computed with plain arithmetic. |
| 4 | Hard-coded secret printed to console | Security (not flagged by tools) | 71, 80 | `pos_terminal_key = "POS_TERMINAL_SECRET_TOKEN_2026"` is stored in source code and then printed in plain text. | The key is read from the `POS_TERMINAL_KEY` environment variable. The program only reports whether a key is configured and never prints the key itself. |
| 5 | Insecure random for PIN (Bandit B311, Low) | Security | 51 | `random.randint` is predictable and unsuitable for a POS PIN. | Used `1000 + secrets.randbelow(9000)` from the `secrets` module (CSPRNG). |
| 6 | Bare `except: pass` (Bandit B110, Pylint W0702, Flake8 E722) | Bug | 26–27 | Swallows every exception, including `KeyboardInterrupt`, and voiding a non-existent table silently "succeeds". | Catch only `KeyError`. Return `False` on failure and `True` on success. |
| 7 | Mutable default argument (Pylint W0102) | Bug | 15 | `order_log=[]` is created once and shared by every call, so log entries leak between unrelated orders. | Default changed to `None`, with a new list created inside the function. |
| 8 | File opened without `with` / encoding (Pylint R1732, W1514) | Bug | 55–57 | If `write` raises, the file handle leaks. The platform-dependent encoding also makes the output non-portable. | `with open(filename, "w", encoding="utf-8") as f:` |
| 9 | Module runs on import | Bug / Design | 83 | A bare `main()` call means that importing the module (for tests or reuse) runs the entire demo and writes files. | Wrapped in `if __name__ == "__main__":`. |
| 10 | Shadowing a global (Pylint W0621) + unused loop var (W0612) | Code Smell | 61, 63 | The parameter `orders` hides the module-level `orders`, and the loop variable `t` is never used. | Parameter renamed to `order_book`. The loop was replaced with `sum(... for details in order_book.values() ...)`. |
| 11 | Unused variables / import (Pylint W0612, W0611; Flake8 F841, F401) | Code Smell | 6, 31, 41 | `import math` and `service_tax = 3.50` were dead code. `base_bill` was only reachable through `eval`. | Removed `math` and `service_tax`. `base_bill` is now used directly in the discount calculation. |
| 12 | `== None` comparison (Pylint C0121, Flake8 E711) | Style / Bug | 32 | `== None` can be overridden by `__eq__`. Identity comparison is correct. | Changed to `is None`. |
| 13 | Simplifiable if / else-after-return (Pylint R1703, R1705) | Style | 34–37 | `if x: return True else: return False` is verbose. | `return not orders[table_id]["is_settled"]` |
| 14 | Non-snake_case function names (Pylint C0103) | Style | 15, 23, 30, 40 | `placeTableOrder`, `voidTableOrder`, `checkTableStatus` and `calculateDiscountedBill` violate PEP 8. | Renamed to `place_table_order`, `void_table_order`, `check_table_status` and `calculate_discounted_bill`, and updated the callers. |
| 15 | Missing docstrings (Pylint C0116) | Style | 15, 23, 30, 40, 46, 50, 54, 61 | Public functions have no documentation. | Added a one-line docstring to each function. |
| 16 | `%`-formatting (Pylint C0209) | Style | 19 | An f-string is clearer. | `f"Created order for {table_id} with {items_count} dishes"` |
| 17 | Line too long (Flake8 E501, Pylint C0301) | Style | 18, 19, 75 | Lines exceeded 79 characters. | Split the dict literal across several lines and shortened the call. |
| 18 | No newline at end of file (Flake8 W292, Pylint C0304) | Style | 83 | The file lacked a trailing newline. | Added one. |
