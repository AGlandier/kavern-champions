-- ============================================================
-- Schéma de la base de données BattleApp
-- ============================================================

-- Table battlerooms
CREATE TABLE IF NOT EXISTS battlerooms (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL,
    date    TEXT    NOT NULL DEFAULT (datetime('now')),
    round   INTEGER NOT NULL DEFAULT 0
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
CREATE TABLE IF NOT EXISTS battleroom_players (
    battleroom_id INTEGER NOT NULL,
    username      TEXT    NOT NULL,
    PRIMARY KEY (battleroom_id, username),
    FOREIGN KEY (battleroom_id) REFERENCES battlerooms(id) ON DELETE CASCADE,
    FOREIGN KEY (username)      REFERENCES user(name)
);

-- Table user
CREATE TABLE IF NOT EXISTS user (
    name           TEXT    PRIMARY KEY,          -- clé primaire unique, chaîne
    teamlist       TEXT    NOT NULL DEFAULT '',
    number_battle  INTEGER NOT NULL DEFAULT 0,
    password_hash  TEXT                          -- NULL = pas de mot de passe défini
);
