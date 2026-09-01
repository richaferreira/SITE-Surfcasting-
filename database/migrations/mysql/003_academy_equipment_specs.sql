-- Migração incremental da Academia Long Cast para bancos existentes.

USE surfcasting;

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
