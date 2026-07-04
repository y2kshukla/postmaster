# Drop `description` from KV tables

## Changes needed

### 1. `src/postmaster/models/request.py` — Remove model field

**Remove line 12** so `KeyValueEntry` becomes:

```python
class KeyValueEntry(BaseModel):
    key: str = ""
    value: str = ""
    enabled: bool = True
```

### 2. `src/postmaster/widgets/kv_table.py` — Remove UI elements

**a) Remove description Input from `KvRow.compose`** (line 19):

```diff
-        yield Input(value=self._entry.description, placeholder="Desc", classes="kv-desc")
```

**b) Remove description read-back in `KvRow.get_entry`** (line 28):

```diff
         self._entry.key = inputs[0].value
         self._entry.value = inputs[1].value
-        self._entry.description = inputs[2].value
         return self._entry
```

**c) Remove "Desc" header label from `KvTable.compose`** (line 52):

```diff
             Label("Key", classes="col-header")
             Label("Value", classes="col-header")
-            Label("Desc", classes="col-header")
             Label("", classes="kv-spacer")
```

### 3. `src/postmaster/theme.tcss` — Remove CSS

**Remove lines 196-199** (the `.kv-desc` block):

```diff
-.kv-desc {
-    width: 15;
-    min-width: 10;
-}
```

## Why safe

- `description` is never used in business logic (engine, URL building, variable resolution)
- Persistence is via Pydantic JSON blobs in SQLite; missing field is fine, extra field is ignored on deserialization
- No migration needed
