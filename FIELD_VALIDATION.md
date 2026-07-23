# Field Validation

Platform: Android, Termux, Python 3.14.

| Test | Expected | Observed |
|---|---:|---:|
| Clean case | 0 | 0 |
| Independent bundle | 0 | 0 |
| Content tamper | 1 | 1 |
| Chain reorder | 1 | 1 |
| Restored case | 0 | 0 |

Content tampering produced `HASH_MISMATCH` and `CASE_IDENTITY_MISMATCH`. Chain reordering produced sequence, predecessor, head, and identity mismatch errors. Restoration returned the original package identity.
