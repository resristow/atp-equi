"""
Textos de ajuda ao usuário
"""
from textwrap import fill

textos_crus={
    'cabecalho':
        'NÚMERO NOME TENSÃO',

    'cabecalhoF':
        'NÚMERO NOME ATP-NÓ ATP-FONTE',

    'relaBarra': 
"""O usuário optou por apenas imprimir a relação de barras do arquivo .ANA
(comando 'barras'). O total de barras que possuem equivalentes conectados é {0!s}.
Segue a lista abaixo:\n\n""",

    'relaErroArq':
"""You loose, fella! O arquivo {} não foi encontrado. O caminho tentado foi
{}.
O resto do processamento nem continuou.\n\n""",

    'relaEqui':
"""O arquivo {} foi gerado com sucesso! Foram encontradas {!s} barras com 
equivalentes conectados. A lista completa de barras é apresentada abaixo.\n\n""",
    'relaErroDiff':
"""You loose, fella! O número de barras com equivalentes conectados do arquivo .ANA é
diferente da quantidade total de barras fornecidas no arquivo com os
nomes de barras para o ATP. A diferença é de {!s} barra(s).
O processamento será interrompido. Verifique os dados.\n"""
}

def texto (escolha, query='string'):
    escolhido = textos_crus[escolha]
    if 'list' in query.lower(): 
        return escolhido.split()
    if 'string' in query.lower(): return escolhido
    