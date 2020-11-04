ALTER TABLE tasks
    ADD uuid_user BINARY(16);

ALTER TABLE tasks
    ADD FOREIGN KEY (uuid_user) REFERENCES users(uuid) ON DELETE CASCADE;
