-- ============================================================
-- Schéma de la base de données BattleApp
-- ============================================================

-- Table battlerooms
CREATE TABLE IF NOT EXISTS battlerooms (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT    NOT NULL,
    date              TEXT    NOT NULL DEFAULT (datetime('now')),
    round             INTEGER NOT NULL DEFAULT 0,
    requires_teamlist INTEGER NOT NULL DEFAULT 0,
    closed            INTEGER NOT NULL DEFAULT 0
);

-- Table battle
CREATE TABLE IF NOT EXISTS battle (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    battleroom  INTEGER NOT NULL,
    round       INTEGER NOT NULL DEFAULT 0,
    finished    INTEGER NOT NULL DEFAULT 0,
    content     TEXT    NOT NULL DEFAULT '{}',   -- stocké en JSON (chaîne)
    FOREIGN KEY (battleroom) REFERENCES battlerooms(id) ON DELETE CASCADE
);

-- Table battleroom_players : joueurs inscrits dans une battleroom
-- Un joueur ne peut appartenir qu'à une seule battleroom à la fois (UNIQUE username)
CREATE TABLE IF NOT EXISTS battleroom_players (
    battleroom_id INTEGER NOT NULL,
    username      TEXT    NOT NULL UNIQUE,
    PRIMARY KEY (battleroom_id, username),
    FOREIGN KEY (battleroom_id) REFERENCES battlerooms(id) ON DELETE CASCADE,
    FOREIGN KEY (username)      REFERENCES user(name)
);

-- Table user
CREATE TABLE IF NOT EXISTS user (
    name           TEXT    PRIMARY KEY,          -- clé primaire unique, chaîne
    number_battle  INTEGER NOT NULL DEFAULT 0,
    password_hash  TEXT                          -- NULL = pas de mot de passe défini
);

-- Table battleroom_teamlist : teamlist d'un joueur par battleroom
CREATE TABLE IF NOT EXISTS battleroom_teamlist (
    battleroom_id  INTEGER NOT NULL,
    username       TEXT    NOT NULL,
    teamlist       TEXT    NOT NULL DEFAULT '',
    PRIMARY KEY (battleroom_id, username),
    FOREIGN KEY (battleroom_id) REFERENCES battlerooms(id) ON DELETE CASCADE,
    FOREIGN KEY (username)      REFERENCES user(name)
);
