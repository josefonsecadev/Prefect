"""Executa flows reais sequenciais dentro do ambiente do worker."""
import argparse
import os

import requests


def check_idle():
    response = requests.post(
        os.environ["PREFECT_API_URL"].rstrip("/") + "/flow_runs/filter",
        json={"flow_runs": {"state": {"type": {"any_": ["RUNNING", "PENDING", "CANCELLING", "PAUSED"]}}}},
        timeout=15,
    )
    response.raise_for_status()
    if response.json():
        raise RuntimeError("Há runs ativos; não desligar Prefect")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int)
    parser.add_argument("--check-idle", action="store_true")
    args = parser.parse_args()
    check_idle()
    if args.check_idle:
        return
    if args.year is None:
        parser.error("--year é obrigatório")
    from pipelines.camara_deputados.legislaturas.orquestrador import executar_pipeline_legislaturas
    from pipelines.camara_deputados.deputados.orquestrador import executar_pipeline_deputados
    from pipelines.camara_deputados.despesas.orquestrador import executar_pipeline_despesas
    # Legislaturas é pré-requisito dos dois produtos; os runs não concorrem entre si.
    executar_pipeline_legislaturas()
    executar_pipeline_deputados(ano_inicial=args.year, ano_final=args.year)
    executar_pipeline_despesas(year=args.year)


if __name__ == "__main__":
    main()
