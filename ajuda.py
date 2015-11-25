"""
Textos de ajuda ao usuário
"""
from textwrap import fill
textos_crus={
    'welcome' : \
        'O APLICATIVO É BASEADO NA IDENTIFICAÇÃO DA LISTA "DBAR" E DAS LINHAS DO EQUIVALENTE QUE CONTENHAM "EQUIV." NO NOME DE CIRCUITO (CN) QUE ESTÃO CONTIDAS NO ARQUIVO *.ANA QUE O USUÁRIO IRÁ INSERIR.',
    'query_ANA' : \
        'PRESSIONE "ENTER" PARA ESCOLHER O ARQUIVO *.ANA.'        
}
def texto (escolha): return fill(textos_crus[escolha], width = 79)