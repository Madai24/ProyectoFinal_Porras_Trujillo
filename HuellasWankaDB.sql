USE HuellasWankaDB;
GO

-- 1. Tabla de Roles (Ciudadano, Junta Vecinal, Administrador)
CREATE TABLE Roles (
    IdRol INT IDENTITY(1,1) PRIMARY KEY,
    NombreRol VARCHAR(50) NOT NULL UNIQUE,
    Descripcion VARCHAR(200) NULL
);

-- 2. Tabla de Usuarios
CREATE TABLE Usuarios (
    IdUsuario INT IDENTITY(1,1) PRIMARY KEY,
    IdRol INT NOT NULL,
    Nombres VARCHAR(100) NOT NULL,
    Apellidos VARCHAR(100) NOT NULL,
    Correo VARCHAR(150) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL, -- Almacenar hash seguro (ej. bcrypt)
    Telefono VARCHAR(15) NULL,
    FechaRegistro DATETIME DEFAULT GETDATE(),
    Activo BIT DEFAULT 1,
    CONSTRAINT FK_Usuarios_Roles FOREIGN KEY (IdRol) REFERENCES Roles(IdRol)
);

-- 3. Tabla de Distritos (Huancayo, El Tambo, Chilca)
CREATE TABLE Distritos (
    IdDistrito INT IDENTITY(1,1) PRIMARY KEY,
    NombreDistrito VARCHAR(100) NOT NULL UNIQUE
);

-- 4. Tabla de Tipos de Residuos
CREATE TABLE TiposResiduo (
    IdTipoResiduo INT IDENTITY(1,1) PRIMARY KEY,
    NombreTipo VARCHAR(100) NOT NULL UNIQUE,
    Descripcion VARCHAR(255) NULL
);

-- 5. Tabla de Estados de Atención
CREATE TABLE EstadosAtencion (
    IdEstado INT IDENTITY(1,1) PRIMARY KEY,
    NombreEstado VARCHAR(50) NOT NULL UNIQUE -- Pendiente de Atención, En Proceso, Recuperado
);

-- 6. Tabla de Cuadrillas de Limpieza / Brigadas
CREATE TABLE Cuadrillas (
    IdCuadrilla INT IDENTITY(1,1) PRIMARY KEY,
    NombreCuadrilla VARCHAR(100) NOT NULL,
    Responsable VARCHAR(150) NULL,
    TelefonoContacto VARCHAR(15) NULL,
    Activa BIT DEFAULT 1
);

-- 7. Tabla Central de Reportes Ciudadanos
CREATE TABLE Reportes (
    IdReporte INT IDENTITY(1,1) PRIMARY KEY,
    IdUsuario INT NULL, -- Permite reportes de usuarios registrados o anónimos si se desea
    IdDistrito INT NOT NULL,
    IdTipoResiduo INT NOT NULL,
    IdEstado INT NOT NULL DEFAULT 1, -- Por defecto 'Pendiente de Atención'
    IdCuadrilla INT NULL, -- Se asigna cuando pasa a 'En Proceso'
    Direccion VARCHAR(255) NOT NULL,
    ReferenciaVisual VARCHAR(255) NULL,
    Latitud DECIMAL(10, 8) NULL, -- Para geolocalización
    Longitud DECIMAL(11, 8) NULL,
    NivelUrgencia VARCHAR(20) NOT NULL CHECK (NivelUrgencia IN ('Baja', 'Media', 'Urgente')),
    ToneladasEstimadas DECIMAL(6, 2) DEFAULT 0.00, -- Para las métricas del portal de inicio
    FechaReporte DATETIME DEFAULT GETDATE(),
    FechaActualizacion DATETIME NULL,
    Activo BIT DEFAULT 1, -- Para borrado lógico de reportes duplicados/inválidos
    CONSTRAINT FK_Reportes_Usuarios FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario),
    CONSTRAINT FK_Reportes_Distritos FOREIGN KEY (IdDistrito) REFERENCES Distritos(IdDistrito),
    CONSTRAINT FK_Reportes_TiposResiduo FOREIGN KEY (IdTipoResiduo) REFERENCES TiposResiduo(IdTipoResiduo),
    CONSTRAINT FK_Reportes_Estados FOREIGN KEY (IdEstado) REFERENCES EstadosAtencion(IdEstado),
    CONSTRAINT FK_Reportes_Cuadrillas FOREIGN KEY (IdCuadrilla) REFERENCES Cuadrillas(IdCuadrilla)
);

-- 8. Tabla de Evidencias Fotográficas (Rutas de archivos JPG/PNG)
CREATE TABLE Evidencias (
    IdEvidencia INT IDENTITY(1,1) PRIMARY KEY,
    IdReporte INT NOT NULL,
    RutaArchivo VARCHAR(500) NOT NULL,
    TipoEvidencia VARCHAR(20) DEFAULT 'Reporte' CHECK (TipoEvidencia IN ('Reporte', 'Limpieza')), -- Foto inicial o foto tras limpiar
    FechaSubida DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Evidencias_Reportes FOREIGN KEY (IdReporte) REFERENCES Reportes(IdReporte) ON DELETE CASCADE
);
GO

-- =====================================================================
-- DATOS INICIALES (catalogos). Se pueden ejecutar varias veces: solo
-- insertan las filas que aun no existen.
-- =====================================================================

-- Roles
INSERT INTO Roles (NombreRol, Descripcion)
SELECT v.NombreRol, v.Descripcion
FROM (VALUES
    ('Ciudadano',     'Usuario que reporta puntos criticos de basura'),
    ('Junta Vecinal', 'Representante vecinal que da seguimiento a reportes'),
    ('Administrador', 'Gestiona reportes, estados y cuadrillas')
) AS v(NombreRol, Descripcion)
WHERE NOT EXISTS (SELECT 1 FROM Roles r WHERE r.NombreRol = v.NombreRol);
GO

-- Estados de atencion (el orden importa: IdEstado = 1 es el valor por defecto de Reportes)
IF NOT EXISTS (SELECT 1 FROM EstadosAtencion WHERE NombreEstado = 'Pendiente de Atención')
    INSERT INTO EstadosAtencion (NombreEstado) VALUES ('Pendiente de Atención');
IF NOT EXISTS (SELECT 1 FROM EstadosAtencion WHERE NombreEstado = 'En Proceso')
    INSERT INTO EstadosAtencion (NombreEstado) VALUES ('En Proceso');
IF NOT EXISTS (SELECT 1 FROM EstadosAtencion WHERE NombreEstado = 'Recuperado')
    INSERT INTO EstadosAtencion (NombreEstado) VALUES ('Recuperado');
GO

-- Tipos de residuo
INSERT INTO TiposResiduo (NombreTipo, Descripcion)
SELECT v.NombreTipo, v.Descripcion
FROM (VALUES
    ('Residuos domésticos', 'Basura común de hogares'),
    ('Desmonte',            'Escombros y material de construcción'),
    ('Residuos orgánicos',  'Restos de comida y vegetación'),
    ('Residuos peligrosos', 'Residuos hospitalarios o químicos')
) AS v(NombreTipo, Descripcion)
WHERE NOT EXISTS (SELECT 1 FROM TiposResiduo t WHERE t.NombreTipo = v.NombreTipo);
GO

-- Distritos de la provincia de Huancayo
INSERT INTO Distritos (NombreDistrito)
SELECT v.NombreDistrito
FROM (VALUES
    ('Huancayo'), ('Carhuacallanga'), ('Chacapampa'), ('Chicche'), ('Chilca'),
    ('Chongos Alto'), ('Chupuro'), ('Colca'), ('Cullhuas'), ('El Tambo'),
    ('Huacrapuquio'), ('Hualhuas'), ('Huancán'), ('Huasicancha'), ('Huayucachi'),
    ('Ingenio'), ('Pariahuanca'), ('Pilcomayo'), ('Pucará'), ('Quichuay'),
    ('Quilcas'), ('San Agustín de Cajas'), ('San Jerónimo de Tunán'),
    ('Santo Domingo de Acobamba'), ('Saño'), ('Sapallanga'), ('Sicaya'), ('Viques')
) AS v(NombreDistrito)
WHERE NOT EXISTS (SELECT 1 FROM Distritos d WHERE d.NombreDistrito = v.NombreDistrito);
GO
