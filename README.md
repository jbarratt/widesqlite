# SQLite query performance

Question: How many qps can we get out of sqlite in a variety of scenarios?

Experiment design:

1. Use python to generate a variety of sqlite files that have different characteristics / indexing strategies etc
2. Use go to query them with (presumably) higher performance
3. Expose them as http and test querying that as well

# Initial Cut

Let's try a basic key value of `guid:word`, where the words come from `/usr/share/dict/words`

The only requirement is `click` outside of the standard library.

### Saving a basic k/v database

```
at 09:06:35 ❯ ./sqbench.py save-kv
235886
```

after running, it looks like so:

```
$ sqlite3 simplekv.db 
SQLite version 3.32.3 2020-06-18 14:16:19
Enter ".help" for usage hints.
sqlite> select * from kv where word='tomato';
tomato|28c44c9f-bd84-487b-a135-7b9b5d549a91
```

Running a test with and without the recommended pragmas where every word is queried but in random order:

No pragmas:

```
 ./sqbench.py single-benchmark             
qps: 122386.37393479078
```

With Pragmas:

```
 ./sqbench.py single-benchmark --runpragmas      
qps: 169064.94722680937
```

With multiple processes (4 by default)

``` 
 ./sqbench.py multi-benchmark
qps: 587898.1924036101
```

Multiple processes, turning up to 6:
```
 ./sqbench.py multi-benchmark --processes=6
qps: 743293.8801882617
```