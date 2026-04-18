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
    content     TEXT    NOT NULL DEFAULT '{}',   -- stocké en JSON (chaîne)
    FOREIGN KEY (battleroom) REFERENCES battlerooms(id) ON DELETE CASCADE
);

-- Table user
CREATE TABLE IF NOT EXISTS user (
    name           TEXT    PRIMARY KEY,          -- clé primaire unique, chaîne
    teamlist       TEXT    NOT NULL DEFAULT '',
    number_battle  INTEGER NOT NULL DEFAULT 0,
    password_hash  TEXT                          -- NULL = pas de mot de passe défini
);
