-- Surfcasting Região dos Lagos
-- Esquema inicial compatível com MySQL 8.0+

CREATE DATABASE IF NOT EXISTS surfcasting
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE surfcasting;

CREATE TABLE IF NOT EXISTS roles (
    id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) NOT NULL,
    name VARCHAR(60) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_roles_code UNIQUE (code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS permissions (
    id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(80) NOT NULL,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT uq_permissions_code UNIQUE (code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id TINYINT UNSIGNED NOT NULL,
    permission_id SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    CONSTRAINT fk_role_permissions_role
        FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_permission
        FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    role_id TINYINT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    username VARCHAR(60) NOT NULL,
    email VARCHAR(254) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500) NULL,
    bio VARCHAR(500) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified_at DATETIME NULL,
    last_login_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE RESTRICT,
    INDEX idx_users_role_active (role_id, is_active)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS praias (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(180) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL DEFAULT 'RJ',
    description TEXT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    location POINT SRID 4326 NOT NULL,
    sea_bearing_deg DECIMAL(5, 2) NOT NULL COMMENT 'Direção da areia para o mar, 0 a <360 graus',
    beach_profile ENUM('TOMBO', 'INTERMEDIARIA', 'RASA', 'ABRIGADA') NOT NULL,
    accessibility_summary VARCHAR(500) NULL,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at DATETIME NULL,
    deleted_by BIGINT UNSIGNED NULL,
    created_by BIGINT UNSIGNED NOT NULL,
    updated_by BIGINT UNSIGNED NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_praias_slug UNIQUE (slug),
    CONSTRAINT chk_praias_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_praias_longitude CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT chk_praias_sea_bearing CHECK (sea_bearing_deg >= 0 AND sea_bearing_deg < 360),
    CONSTRAINT fk_praias_created_by
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT fk_praias_updated_by
        FOREIGN KEY (updated_by) REFERENCES users (id) ON DELETE SET NULL,
    CONSTRAINT fk_praias_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users (id) ON DELETE SET NULL,
    SPATIAL INDEX spx_praias_location (location),
    INDEX idx_praias_city_published (city, is_published, deleted_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pontos_pesca (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    praia_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(180) NOT NULL,
    point_type ENUM('BURACO', 'COROA_AREIA', 'CANAL_RETORNO', 'ESTRUTURA', 'OUTRO') NOT NULL,
    description TEXT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    location POINT SRID 4326 NOT NULL,
    accessibility ENUM('FACIL', 'MODERADA', 'DIFICIL', 'RESTRITA') NOT NULL DEFAULT 'MODERADA',
    access_notes VARCHAR(500) NULL,
    risk_notes VARCHAR(500) NULL,
    verified_at DATETIME NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_pontos_praia_slug UNIQUE (praia_id, slug),
    CONSTRAINT chk_pontos_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_pontos_longitude CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT fk_pontos_praia
        FOREIGN KEY (praia_id) REFERENCES praias (id) ON DELETE RESTRICT,
    CONSTRAINT fk_pontos_created_by
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE RESTRICT,
    SPATIAL INDEX spx_pontos_location (location),
    INDEX idx_pontos_praia_type_active (praia_id, point_type, is_active)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS posts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    author_id BIGINT UNSIGNED NOT NULL,
    title VARCHAR(220) NOT NULL,
    slug VARCHAR(240) NOT NULL,
    excerpt VARCHAR(500) NULL,
    content LONGTEXT NOT NULL,
    content_type ENUM('ARTIGO', 'TUTORIAL', 'VIDEO', 'EQUIPAMENTO') NOT NULL,
    status ENUM('RASCUNHO', 'EM_REVISAO', 'PUBLICADO', 'ARQUIVADO') NOT NULL DEFAULT 'RASCUNHO',
    featured_image_url VARCHAR(500) NULL,
    video_url VARCHAR(500) NULL,
    seo_title VARCHAR(70) NULL,
    seo_description VARCHAR(160) NULL,
    published_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_posts_slug UNIQUE (slug),
    CONSTRAINT fk_posts_author
        FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE RESTRICT,
    INDEX idx_posts_status_published (status, published_at),
    INDEX idx_posts_author_status (author_id, status),
    FULLTEXT INDEX ftx_posts_search (title, excerpt, content)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS equipment_specifications (
    post_id BIGINT UNSIGNED PRIMARY KEY,
    rod_length_m DECIMAL(4, 2) NULL,
    rod_construction VARCHAR(80) NULL,
    reel_size INT UNSIGNED NULL,
    main_line_material VARCHAR(80) NULL,
    main_line_diameter_mm DECIMAL(4, 3) NULL,
    shock_leader_type VARCHAR(100) NULL,
    casting_weight_min_g INT UNSIGNED NULL,
    casting_weight_max_g INT UNSIGNED NULL,
    extra_specs JSON NULL,
    CONSTRAINT fk_equipment_specifications_post
        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
    CONSTRAINT chk_equipment_casting_weight
        CHECK (
            casting_weight_min_g IS NULL
            OR casting_weight_max_g IS NULL
            OR casting_weight_max_g >= casting_weight_min_g
        )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS media_assets (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uploaded_by BIGINT UNSIGNED NOT NULL,
    kind ENUM('IMAGE', 'VIDEO') NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    stored_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    original_size_bytes BIGINT UNSIGNED NOT NULL,
    size_bytes BIGINT UNSIGNED NOT NULL,
    width INT UNSIGNED NULL,
    height INT UNSIGNED NULL,
    duration_seconds INT UNSIGNED NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_media_assets_stored_name UNIQUE (stored_name),
    CONSTRAINT fk_media_assets_uploaded_by
        FOREIGN KEY (uploaded_by) REFERENCES users (id) ON DELETE RESTRICT,
    INDEX idx_media_assets_kind_created (kind, created_at)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS community_threads (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    author_id BIGINT UNSIGNED NOT NULL,
    beach_id BIGINT UNSIGNED NULL,
    title VARCHAR(160) NOT NULL,
    content TEXT NOT NULL,
    category ENUM('RELATO', 'DUVIDA', 'CAPTURA', 'EQUIPAMENTO') NOT NULL,
    status ENUM('PUBLICADO', 'OCULTO', 'ARQUIVADO') NOT NULL DEFAULT 'PUBLICADO',
    media_url VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_community_threads_author
        FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT fk_community_threads_beach
        FOREIGN KEY (beach_id) REFERENCES praias (id) ON DELETE SET NULL,
    INDEX idx_community_threads_status_updated (status, updated_at),
    INDEX idx_community_threads_beach_category (beach_id, category),
    FULLTEXT INDEX ftx_community_threads_search (title, content)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS community_comments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    thread_id BIGINT UNSIGNED NOT NULL,
    author_id BIGINT UNSIGNED NOT NULL,
    content TEXT NOT NULL,
    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_community_comments_thread
        FOREIGN KEY (thread_id) REFERENCES community_threads (id) ON DELETE CASCADE,
    CONSTRAINT fk_community_comments_author
        FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE RESTRICT,
    INDEX idx_community_comments_thread_hidden (thread_id, is_hidden, created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS community_reactions (
    thread_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (thread_id, user_id),
    CONSTRAINT fk_community_reactions_thread
        FOREIGN KEY (thread_id) REFERENCES community_threads (id) ON DELETE CASCADE,
    CONSTRAINT fk_community_reactions_user
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    INDEX idx_community_reactions_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ad_campaigns (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    created_by_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    placement ENUM('HOME_TOPO', 'HOME_CONTEUDO', 'ACADEMIA', 'MAPA') NOT NULL,
    title VARCHAR(120) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(180) NOT NULL,
    starts_at DATETIME NOT NULL,
    ends_at DATETIME NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ad_campaigns_created_by
        FOREIGN KEY (created_by_id) REFERENCES users (id) ON DELETE RESTRICT,
    CONSTRAINT chk_ad_campaign_period CHECK (ends_at > starts_at),
    INDEX idx_ad_campaigns_public (placement, is_active, starts_at, ends_at)
) ENGINE=InnoDB;

INSERT INTO roles (code, name) VALUES
    ('ADMIN', 'Administrador'),
    ('AUTHOR', 'Autor'),
    ('USER', 'Usuário comum')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO permissions (code, description) VALUES
    ('admin.full_access', 'Acesso integral ao backoffice'),
    ('content.create', 'Criar conteúdo'),
    ('content.publish', 'Publicar conteúdo'),
    ('content.manage_own', 'Gerenciar o próprio conteúdo'),
    ('community.interact', 'Interagir na comunidade')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p
WHERE
    r.code = 'ADMIN'
    OR (r.code = 'AUTHOR' AND p.code IN ('content.create', 'content.manage_own', 'community.interact'))
    OR (r.code = 'USER' AND p.code = 'community.interact');
