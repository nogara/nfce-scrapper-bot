CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY,
    primeiro_nome TEXT NOT NULL,
    ultimo_nome TEXT NOT NULL,
    nome_usuario TEXT NOT NULL,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj TEXT NOT NULL UNIQUE,
    razao_social TEXT NOT NULL,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notas_fiscais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empresa INTEGER,
    id_usuario INTEGER,
    chave_acesso TEXT NOT NULL,
    numero TEXT NOT NULL,
    serie TEXT NOT NULL,
    protocolo_autorizacao TEXT NOT NULL,
    data_autorizacao TIMESTAMP,
    data_emissao TIMESTAMP,
    tributacao_federal REAL NOT NULL DEFAULT 0.0,
    tributacao_estadual REAL NOT NULL DEFAULT 0.0,
    tributacao_municipal REAL NOT NULL DEFAULT 0.0,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_empresa) REFERENCES empresas(id),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS itens_nota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER,
    id_nota_fiscal INTEGER,
    quantidade REAL DEFAULT 0,
    preco_unitario REAL NOT NULL DEFAULT 0.0,
    unidade_medida TEXT,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_produto) REFERENCES produtos(id),
    FOREIGN KEY (id_nota_fiscal) REFERENCES notas_fiscais(id)
);
