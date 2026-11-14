import duckdb
import os

# Pega a senha do ambiente ou usa a padrão
senha = os.getenv("RUSTFS_SECRET_KEY", "admin123")

print("🔌 Conectando ao DuckDB...")
conn = duckdb.connect()

print("📦 Carregando extensões...")
conn.execute("INSTALL iceberg; LOAD iceberg;")
conn.execute("INSTALL httpfs; LOAD httpfs;")

print("🔑 Criando segredo S3...")
conn.execute(f"""
    CREATE SECRET (
        TYPE s3,
        KEY_ID 'admin',
        SECRET '{senha}',
        ENDPOINT 'localhost:9000',
        USE_SSL false,
        URL_STYLE 'path',
        REGION 'us-east-1'
    );
""")

print("🗂️  Anexando catálogo Iceberg (Nessie)...")
conn.execute("""
    ATTACH 'warehouse' AS lakehouse (
        TYPE iceberg,
        ENDPOINT 'http://localhost:19120/iceberg',
        AUTHORIZATION_TYPE 'none',
        ACCESS_DELEGATION_MODE 'none'
    );
""")

print("\n=== 5 PRIMEIRAS LEGISLATURAS ===\n")
conn.sql("SELECT * FROM lakehouse.prata_camara_deputados.legislaturas LIMIT 5;").show()

print("\n=== TOTAL DE LINHAS ===\n")
conn.sql("SELECT COUNT(*) AS total FROM lakehouse.prata_camara_deputados.legislaturas;").show()

print("\n=== HISTÓRICO DE SNAPSHOTS (TIME TRAVEL) ===\n")
conn.sql("SELECT * FROM iceberg_snapshots(lakehouse.prata_camara_deputados.legislaturas);").show()

print("\n✅ Consulta concluída com sucesso!")