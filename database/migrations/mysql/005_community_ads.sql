-- Comunidade interativa e campanhas publicitárias para bancos existentes.

USE surfcasting;


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
