-- Surfcasting Região dos Lagos
-- Recursos complementares de comunidade, favoritos, telemetria e auditoria.

USE surfcasting;

CREATE TABLE IF NOT EXISTS post_comments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id BIGINT UNSIGNED NOT NULL,
    author_id BIGINT UNSIGNED NOT NULL,
    content TEXT NOT NULL,
    status ENUM('PUBLICADO', 'OCULTO', 'REMOVIDO') NOT NULL DEFAULT 'PUBLICADO',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_post_comments_post FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
    CONSTRAINT fk_post_comments_author FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE,
    INDEX idx_comments_post_status_created (post_id, status, created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS post_likes (
    post_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, user_id),
    CONSTRAINT fk_post_likes_post FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
    CONSTRAINT fk_post_likes_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS catches (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    praia_id BIGINT UNSIGNED NULL,
    species_name VARCHAR(120) NOT NULL,
    bait VARCHAR(120) NULL,
    technique VARCHAR(120) NULL,
    weight_kg DECIMAL(7, 3) NULL,
    length_cm DECIMAL(7, 2) NULL,
    image_url VARCHAR(500) NULL,
    notes VARCHAR(1000) NULL,
    caught_at DATETIME NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_catches_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_catches_praia FOREIGN KEY (praia_id) REFERENCES praias (id) ON DELETE SET NULL,
    INDEX idx_catches_public_caught (is_public, caught_at),
    INDEX idx_catches_praia_species (praia_id, species_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS praia_favorites (
    user_id BIGINT UNSIGNED NOT NULL,
    praia_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, praia_id),
    CONSTRAINT fk_favorites_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_favorites_praia FOREIGN KEY (praia_id) REFERENCES praias (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS telemetry_snapshots (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    praia_id BIGINT UNSIGNED NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    score TINYINT UNSIGNED NULL,
    wind_speed_mps DECIMAL(7, 3) NULL,
    wind_direction_deg DECIMAL(7, 3) NULL,
    tide_trend VARCHAR(40) NULL,
    wave_height_m DECIMAL(7, 3) NULL,
    wave_period_s DECIMAL(7, 3) NULL,
    water_temperature_c DECIMAL(7, 3) NULL,
    pressure_hpa DECIMAL(8, 2) NULL,
    source VARCHAR(80) NOT NULL DEFAULT 'aggregated',
    captured_at DATETIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_telemetry_praia FOREIGN KEY (praia_id) REFERENCES praias (id) ON DELETE SET NULL,
    INDEX idx_telemetry_praia_captured (praia_id, captured_at),
    INDEX idx_telemetry_coordinates_captured (latitude, longitude, captured_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(80) NOT NULL,
    entity_id VARCHAR(80) NULL,
    metadata_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
    INDEX idx_audit_created (created_at),
    INDEX idx_audit_entity (entity_type, entity_id)
) ENGINE=InnoDB;
