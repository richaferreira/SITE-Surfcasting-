USE surfcasting;

CREATE TABLE IF NOT EXISTS account_tokens (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    token_hash CHAR(64) NOT NULL,
    purpose ENUM('VERIFY_EMAIL', 'RESET_PASSWORD') NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_account_tokens_hash UNIQUE (token_hash),
    CONSTRAINT fk_account_tokens_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_account_tokens_lookup (purpose, token_hash, expires_at, used_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS community_reports (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    reporter_id BIGINT UNSIGNED NOT NULL,
    post_id BIGINT UNSIGNED NULL,
    comment_id BIGINT UNSIGNED NULL,
    reason ENUM('SPAM', 'ABUSO', 'CONTEUDO_IMPROPRIO', 'DESINFORMACAO', 'OUTRO') NOT NULL,
    details VARCHAR(1000) NULL,
    status ENUM('ABERTO', 'EM_ANALISE', 'RESOLVIDO', 'DESCARTADO') NOT NULL DEFAULT 'ABERTO',
    reviewed_by BIGINT UNSIGNED NULL,
    reviewed_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_reporter FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_reports_post FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    CONSTRAINT fk_reports_comment FOREIGN KEY (comment_id) REFERENCES post_comments(id) ON DELETE CASCADE,
    CONSTRAINT fk_reports_reviewer FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT chk_reports_target CHECK ((post_id IS NOT NULL) <> (comment_id IS NOT NULL)),
    INDEX idx_reports_status_created (status, created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    notification_type VARCHAR(60) NOT NULL,
    title VARCHAR(180) NOT NULL,
    message VARCHAR(500) NOT NULL,
    action_url VARCHAR(500) NULL,
    read_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notifications_user_read (user_id, read_at, created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS media_assets (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    owner_id BIGINT UNSIGNED NOT NULL,
    media_type ENUM('IMAGE') NOT NULL DEFAULT 'IMAGE',
    original_name VARCHAR(255) NOT NULL,
    stored_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT UNSIGNED NOT NULL,
    public_url VARCHAR(600) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_media_stored_name UNIQUE (stored_name),
    CONSTRAINT fk_media_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_media_owner_created (owner_id, created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS analytics_events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NULL,
    session_id VARCHAR(80) NULL,
    event_name VARCHAR(80) NOT NULL,
    page_path VARCHAR(500) NULL,
    beach_slug VARCHAR(180) NULL,
    metadata_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_analytics_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_analytics_event_created (event_name, created_at),
    INDEX idx_analytics_beach_created (beach_slug, created_at)
) ENGINE=InnoDB;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS accepted_terms_at DATETIME NULL,
    ADD COLUMN IF NOT EXISTS accepted_privacy_at DATETIME NULL;
