from prefect import flow

try:
    from .bronze import PipeBronze
    from .prata import PipePrata
except ImportError:  # pragma: no cover
    from bronze import PipeBronze
    from prata import PipePrata


@flow(
    name="camara_legislaturas_orquestrador",
    description="Executa as camadas Bronze e Prata da pipeline de legislaturas.",
)
def executar_pipeline_legislaturas() -> dict:
    quantidade = PipeBronze().execute()
    snapshot = PipePrata().execute()
    return {"quantidade_bronze": quantidade, "snapshot_prata": snapshot}


if __name__ == "__main__":
    executar_pipeline_legislaturas()
