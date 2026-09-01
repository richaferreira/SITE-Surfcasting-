-- Migração incremental para instalações que já executaram 001_initial_schema.sql.
-- Não é executada pelo bootstrap de novos volumes; aplique uma única vez em bancos existentes.

USE surfcasting;

ALTER TABLE praias
    ADD COLUMN deleted_at DATETIME NULL AFTER is_published,
    ADD COLUMN deleted_by BIGINT UNSIGNED NULL AFTER deleted_at,
    ADD CONSTRAINT fk_praias_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE pontos_pesca
    DROP FOREIGN KEY fk_pontos_praia,
    ADD CONSTRAINT fk_pontos_praia
        FOREIGN KEY (praia_id) REFERENCES praias (id) ON DELETE RESTRICT;

