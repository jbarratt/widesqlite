#!/usr/bin/env python3

import time
import uuid
import click
import random
import sqlite3
from multiprocessing import Pool

KV_PATH = "../simplekv.db"

@click.command()
@click.option('--path', default=KV_PATH)
def save_kv(path):
    """ Generate a simple kv db, where we connect an entry from the words list to a UUID. """
    (cursor, connection) = init_connection(run_pragmas=True, path=path)
    cursor.executescript("""
        DROP TABLE IF EXISTS kv; 
        CREATE TABLE kv (word TEXT, uuid TEXT, PRIMARY KEY (word));
    """)

    words = load_words()
    for word in words:
        cursor.execute("INSERT INTO kv (word, uuid) VALUES  (?, ?)", (word, str(uuid.uuid4())))
    print(cursor.lastrowid)
    cursor.close()

    connection.commit()
    connection.close()

def init_connection(run_pragmas=False, path=KV_PATH):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    pragmas = """
    pragma journal_mode = WAL;
    pragma synchronous = normal;
    pragma temp_store = memory;
    pragma mmap_size = 30000000000;
    """

    if run_pragmas:
        cursor.executescript(pragmas)
    return (cursor, connection)

def load_words():
    # Load up all the words to query and randomize the order to make it sporting
    with open("/usr/share/dict/words", "r") as wordfile:
        words = [x.strip() for x in wordfile.readlines()]
    random.shuffle(words)
    return words

def base_benchmark(run_pragmas=False, times=4):
    """ query the simple kv database as fast as possible.
        if pragmas is true, run them before doing the test
    """

    words = load_words()
    (cursor, connection) = init_connection(run_pragmas)
    for x in range(times):
        for word in words:
            rows = cursor.execute("select uuid from kv where word = ?", (word,)).fetchall()

    processed = len(words)*times
    return processed

@click.command()
@click.option('--processes', default=4)
def multi_benchmark(processes):
    """ Run queries from multiple processes and report on qps """
    start = time.perf_counter()
    inputs = [True] * processes * 2
    pool = Pool(processes)
    processed = sum(pool.map(base_benchmark, inputs))
    pool.close()
    end = time.perf_counter()

    print(f"qps: {processed / (end - start)}")

@click.command()
@click.option('--runpragmas', is_flag=True)
def single_benchmark(runpragmas):
    """ Run queries from a single process and report on qps """
    start = time.perf_counter()
    processed = base_benchmark(run_pragmas=runpragmas)
    end = time.perf_counter()

    print(f"qps: {processed / (end - start)}")

@click.group(help="simple sqlite3 file builder and benchmarker")
def cli():
    pass

cli.add_command(multi_benchmark)
cli.add_command(single_benchmark)
cli.add_command(save_kv)

if __name__ == '__main__':
    cli()