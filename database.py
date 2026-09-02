"""
database.py
-------------
Camada de acesso à base de dados. Abre ligações SQLite e garante que
o esquema (tabelas) existe.
"""

import sqlite3
from pathlib import Path

DB_PATH_DEFAULT = Path(__file__).parent / "next_point.db"
