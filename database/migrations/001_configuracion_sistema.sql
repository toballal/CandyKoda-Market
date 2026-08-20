CREATE TABLE IF NOT EXISTS configuracion_sistema (
    clave VARCHAR(80) PRIMARY KEY,
    valor VARCHAR(255) NOT NULL,
    descripcion VARCHAR(255) NULL,
    actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO configuracion_sistema (clave, valor, descripcion)
VALUES ('market_mantenimiento', '0', 'Bloquea compras en Candy Koda Market');

-- Activar desde CandyKodaAdmin:
-- UPDATE configuracion_sistema SET valor='1' WHERE clave='market_mantenimiento';
-- Desactivar:
-- UPDATE configuracion_sistema SET valor='0' WHERE clave='market_mantenimiento';
