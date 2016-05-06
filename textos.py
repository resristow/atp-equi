"""
Textos de ajuda ao usuário
"""

texto={
    'welcome': 
"""
 ||================================
 ||ATP-EQUI                       || 
 ||Autor: RES Ristow              ||
 ||                               ||
 ||Versão {}                   ||
 ||                               ||
 ||{:0^2}/{:0^2}/{} - {:2}h{:0^2}min          ||
 ||================================

""",

    'cabecalho':
        'NÚMERO NOME TENSÃO',

    'cabecalhoF':
        'NÚMERO NOME ATP-NÓ ATP-FONTE',

    'relaBarra': 
"""O usuário optou por apenas imprimir a relação de barras do arquivo .ANA
(comando 'barras'). O total de barras que possuem equivalentes conectados é {0!s}.
Segue a lista abaixo:\n\n""",

    'relaRncc':
"""O usuário optou por emitir um Relatório de Níveis de Curto-Circuito das barras
com equivalentes conectados e somente com as fontes equivalentes gerando.
O relatório foi gravado em {}.\n\n""",

    'relaArq':
"O arquivo {} foi lido com sucesso!\n\n",

    'relaErroArq':
"""You loose, fella! O arquivo {} não foi encontrado.""",

    'relaSrc':
"""O usuário optou por emitir um arquivo .lib com o cartão ATP /SOURCE com
as fontes equivalentes já modeladas.
O arquivo {} foi gravado com sucesso!\n\n""",

    'relaEqui':
"""O arquivo {} foi gerado com sucesso! Foram encontradas {!s} barras com 
equivalentes conectados, sendo que {!s} são fontes. A lista completa de barras é apresentada abaixo.\n\n""",

    'relaErroMiss':
"""You loose, fella! Alguns nomes de nós do ATP não foram encontrados na plani-
lha. Favor complementar a lista. Seguem abaixo as barras faltantes:\n""",

    'fim':
"O processamento chegou ao fim! Informações em {}."
}    