CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    direccion TEXT,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS bodegas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    ubicacion TEXT,
    capacidad_maxima INTEGER
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio FLOAT,
    stock INTEGER,
    categoria_nombre TEXT NO NULL,
    proveedor_nombre TEXT NO NULL,
    bodega_nombre TEXT NO NULL,
    FOREIGN KEY (categoria_nombre) REFERENCES categorias(nombre),
    FOREIGN KEY (proveedor_nombre) REFERENCES proveedores(nombre),
    FOREIGN KEY (bodega_nombre) REFERENCES bodegas(nombre)
);
