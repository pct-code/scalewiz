--
-- File generated with SQLiteStudio v3.3.3 on Wed Jun 30 07:22:45 2021
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: projects
CREATE TABLE projects (
    id   INTEGER PRIMARY KEY,
    name TEXT    NOT NULL
);


-- Table: readings
CREATE TABLE readings (
    id      INTEGER PRIMARY KEY,
    test_id INTEGER REFERENCES tests (id) ON DELETE CASCADE
                                          ON UPDATE CASCADE
                    NOT NULL
);


-- Table: reports
CREATE TABLE reports (
    id      INTEGER PRIMARY KEY,
    test_id         REFERENCES tests (id) ON DELETE CASCADE
                                          ON UPDATE CASCADE
);


-- Table: tests
CREATE TABLE tests (
    id         INTEGER PRIMARY KEY,
    project_id         REFERENCES projects (id) ON DELETE CASCADE
                                                ON UPDATE CASCADE
                       NOT NULL,
    name       TEXT    NOT NULL
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
