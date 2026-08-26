CREATE SCHEMA IF NOT EXISTS geren2;

DROP TABLE IF EXISTS geren2.venta CASCADE;
DROP TABLE IF EXISTS geren2.cliente CASCADE;
DROP TABLE IF EXISTS geren2.genero CASCADE;
DROP TABLE IF EXISTS geren2.metodo_pago CASCADE;
DROP TABLE IF EXISTS geren2.navegador CASCADE;


CREATE TABLE IF NOT EXISTS geren2.genero (
  id_genero INT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS geren2.metodo_pago (
  id_metodo_pago INT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS geren2.navegador (
  id_navegador INT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS geren2.cliente (
  id_cliente INT PRIMARY KEY,
  edad INT NOT NULL CHECK (edad >= 0 AND edad <= 120),
  id_genero INT NOT NULL,
  FOREIGN KEY (id_genero) REFERENCES geren2.genero(id_genero)
);

CREATE TABLE IF NOT EXISTS geren2.venta (
  id_venta SERIAL PRIMARY KEY,
  id_cliente INT NOT NULL,
  venta_total DECIMAL(10,2) NOT NULL,
  num_compra INT NOT NULL,
  fecha_compra DATE NOT NULL,
  monto_compra DECIMAL(10,2) NOT NULL,
  id_metodo_pago INT NOT NULL,
  tiempo INT NOT NULL,
  id_navegador INT NOT NULL,
  boletin SMALLINT NOT NULL CHECK (boletin IN (0, 1)),
  vale SMALLINT NOT NULL CHECK (vale IN (0, 1)),
  FOREIGN KEY (id_cliente) REFERENCES geren2.cliente(id_cliente),
  FOREIGN KEY (id_metodo_pago) REFERENCES geren2.metodo_pago(id_metodo_pago),
  FOREIGN KEY (id_navegador) REFERENCES geren2.navegador(id_navegador)
);

-- Crear índices
CREATE INDEX idx_cliente_genero ON geren2.cliente(id_genero);
CREATE INDEX idx_venta_fecha ON geren2.venta(fecha_compra);
CREATE INDEX idx_venta_cliente ON geren2.venta(id_cliente);
CREATE INDEX idx_venta_metodo ON geren2.venta(id_metodo_pago);
CREATE INDEX idx_venta_navegador ON geren2.venta(id_navegador);

-- Insertar datos de referencia
INSERT INTO geren2.genero (id_genero, nombre) VALUES
  (0, 'Masculino'),
  (1, 'Femenino');

INSERT INTO geren2.metodo_pago (id_metodo_pago, nombre) VALUES
  (0, 'Efectivo'),
  (1, 'Tarjeta Crédito'),
  (2, 'Tarjeta Débito');

INSERT INTO geren2.navegador (id_navegador, nombre) VALUES
  (0, 'Tienda Física'),
  (1, 'Navegador 1'),
  (2, 'Navegador 2'),
  (3, 'Navegador 3'),
  (4, 'Navegador 4');