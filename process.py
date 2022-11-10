# pylint: disable=missing-module-docstring
import re
import numpy as np
import pandas as pd

def get_tamanho_motor(modelo: str) -> str:
    """"engine size from 'modelo' variable"""

    pattern = r"\d{1}\.\d{1}"
    match = re.findall(pattern, modelo)
    if len(match) > 0:
        return match[0]
    return np.NaN


def cambio_tipo(modelo: str) -> str:
    """convert description into binary"""
    pattern = r".*(Aut).*"
    match = re.findall(pattern, modelo)
    if len(match) > 0:
        return "automatic"
    return "manual"


def process_data(in_path, out_path=None):
    # read data
    data = pd.read_csv(in_path)

    # unpack details
    tamanho_motor = pd.DataFrame(
        data['modelo'].map(get_tamanho_motor)
    ).rename(columns={'modelo': 'tamanho_motor'})

    cambio = pd.DataFrame(
        data['modelo'].map(cambio_tipo)
    ).rename(columns={'modelo': 'cambio'})

    ano_modelo = pd.DataFrame(
        data['ano_modelo'].map(
            lambda x: [x.split()[0], ''.join(x.split()[1:])]
        ).to_list()
    )[[0, 1]]
    ano_modelo.rename(columns={0: 'ano', 1: 'combustivel'}, inplace=True)
    ano_modelo['ano'].replace("Zero", "2023", inplace=True)
    ano_modelo['combustivel'].replace("KMaGasolina", "Gasolina", inplace=True)
    ano_modelo['combustivel'].replace("KMaDiesel", "Diesel", inplace=True)

    # merge and deal with NaN
    main = pd.concat(
        [
            data[['marca', 'modelo']],
            ano_modelo[['combustivel']],
            cambio,
            tamanho_motor,
            ano_modelo[['ano']],
            data[['preco_medio']]
        ],
        axis=1
    )
    main.dropna(inplace=True)

    # correct types
    main[['ano']] = main[['ano']].astype("int")
    main[['tamanho_motor']] = main[['tamanho_motor']].astype("float")
    # prices to float
    main['preco_medio'].replace(
        regex={r'(R\$\s)': '', r'\.': '', r'\,': '.'},
        inplace=True
    )
    main[['preco_medio']] = main[['preco_medio']].astype("float")

    # unpack age
    main['idade'] = 2023 - main['ano']

    # export
    if out_path is not None:
        main.to_parquet(out_path)
    return main
    # create dummy table
