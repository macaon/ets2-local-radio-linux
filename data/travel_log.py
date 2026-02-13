#!/usr/bin/env python3
"""
SQLite travel log for ETS2 Truck Companion
"""

import sqlite3
import time
import threading


class TravelLog:
    """Persistent travel log using SQLite"""

    def __init__(self, db_path):
        self.db_path = str(db_path)
        self._local = threading.local()
        self._session_id = None
        self._current_job_id = None
        self._init_db()

    def _get_conn(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        """Create tables if they don't exist"""
        conn = self._get_conn()
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                city TEXT,
                country TEXT,
                x REAL, z REAL,
                signal_strength REAL
            );

            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY,
                started_at REAL,
                completed_at REAL,
                cargo TEXT,
                source_city TEXT, source_company TEXT,
                dest_city TEXT, dest_company TEXT,
                distance_km INTEGER,
                income INTEGER,
                cargo_damage REAL
            );

            CREATE TABLE IF NOT EXISTS fines (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                amount INTEGER,
                city TEXT, country TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                started_at REAL,
                ended_at REAL,
                distance_km REAL,
                cities_visited INTEGER,
                countries_visited INTEGER,
                jobs_completed INTEGER,
                fines_total INTEGER
            );
        ''')
        conn.commit()

    def record_visit(self, city, country, x, z, signal):
        conn = self._get_conn()
        conn.execute(
            'INSERT INTO visits (timestamp, city, country, x, z, signal_strength) VALUES (?,?,?,?,?,?)',
            (time.time(), city, country, x, z, signal)
        )
        conn.commit()

    def record_job_start(self, cargo, src_city, src_comp, dst_city, dst_comp, distance, income):
        conn = self._get_conn()
        cursor = conn.execute(
            'INSERT INTO jobs (started_at, cargo, source_city, source_company, dest_city, dest_company, distance_km, income) '
            'VALUES (?,?,?,?,?,?,?,?)',
            (time.time(), cargo, src_city, src_comp, dst_city, dst_comp, distance, income)
        )
        self._current_job_id = cursor.lastrowid
        conn.commit()

    def record_job_complete(self, cargo_damage):
        conn = self._get_conn()
        if self._current_job_id:
            conn.execute(
                'UPDATE jobs SET completed_at=?, cargo_damage=? WHERE id=?',
                (time.time(), cargo_damage, self._current_job_id)
            )
            conn.commit()
            self._current_job_id = None

    def record_fine(self, amount, city, country):
        conn = self._get_conn()
        conn.execute(
            'INSERT INTO fines (timestamp, amount, city, country) VALUES (?,?,?,?)',
            (time.time(), amount, city, country)
        )
        conn.commit()

    def start_session(self):
        conn = self._get_conn()
        cursor = conn.execute(
            'INSERT INTO sessions (started_at) VALUES (?)',
            (time.time(),)
        )
        self._session_id = cursor.lastrowid
        conn.commit()

    def end_session(self, stats):
        if not self._session_id:
            return
        conn = self._get_conn()
        conn.execute(
            'UPDATE sessions SET ended_at=?, distance_km=?, cities_visited=?, '
            'countries_visited=?, jobs_completed=?, fines_total=? WHERE id=?',
            (
                time.time(),
                stats.get('total_distance', 0),
                stats.get('cities_visited', 0),
                stats.get('countries_visited', 0),
                stats.get('jobs_completed', 0),
                stats.get('total_fines', 0),
                self._session_id,
            )
        )
        conn.commit()

    def get_stats(self):
        conn = self._get_conn()
        cities = conn.execute('SELECT COUNT(DISTINCT city) FROM visits').fetchone()[0]
        countries = conn.execute('SELECT COUNT(DISTINCT country) FROM visits').fetchone()[0]
        jobs = conn.execute('SELECT COUNT(*) FROM jobs WHERE completed_at IS NOT NULL').fetchone()[0]
        income = conn.execute('SELECT COALESCE(SUM(income),0) FROM jobs WHERE completed_at IS NOT NULL').fetchone()[0]
        fines = conn.execute('SELECT COALESCE(SUM(amount),0) FROM fines').fetchone()[0]

        # Total distance is approximated from job distances
        distance = conn.execute(
            'SELECT COALESCE(SUM(distance_km),0) FROM jobs WHERE completed_at IS NOT NULL'
        ).fetchone()[0]

        return {
            'total_distance': distance,
            'cities_visited': cities,
            'countries_visited': countries,
            'jobs_completed': jobs,
            'total_income': income,
            'total_fines': fines,
        }

    def get_recent_visits(self, limit=50):
        conn = self._get_conn()
        rows = conn.execute(
            'SELECT city, country, timestamp, signal_strength FROM visits ORDER BY id DESC LIMIT ?',
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_job_history(self, limit=20):
        conn = self._get_conn()
        rows = conn.execute(
            'SELECT cargo, source_city, source_company, dest_city, dest_company, '
            'distance_km, income, cargo_damage, started_at, completed_at '
            'FROM jobs WHERE completed_at IS NOT NULL ORDER BY id DESC LIMIT ?',
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
