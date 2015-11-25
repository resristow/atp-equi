"""
Textos de ajuda ao usuário
"""
from textwrap import fill

textos_crus={
    'welcome' : \
        'O APLICATIVO É BASEADO NA IDENTIFICAÇÃO DA LISTA "DBAR" E DAS LINHAS DO EQUIVALENTE QUE CONTENHAM "EQUIV." NO NOME DE CIRCUITO (CN) QUE ESTÃO CONTIDAS NO ARQUIVO *.ANA QUE O USUÁRIO IRÁ INSERIR.',
    'queryArq' : \
        'PRESSIONE "ENTER" PARA ESCOLHER O ARQUIVO.',
    'cabecalho': \
        'NÚMERO NOME TENSÃO',
    'barrasTot': \
        'TOTAL DE BARRAS: ',
    'ATPinput': \
        'CRIE UM ARQUIVO TEXTO COM OS CÓDIGOS PARA ATP (NÃO SE ESQUEÇA DO "TERRA"). SEU ARQUIVO DEVE TER A MESMA SEQUÊNCIA DA LISTA ACIMA.',
    'diff': \
        'AS LISTAS CONTÊM QUANTIDADES DIFERENTES!',
    'igual': \
        'AS LISTAS CONTÊM QUANTIDADES IGUAIS. CONFIRA SE OS CÓDIGOS CORRESPONDEM ENTRE SI.',
    'queryLib': \
        'ESCOLHA UMAS DAS OPÇÕES ABAIXO:\n1 - ACEITAR A LISTA E GERAR ARQUIVO .LIB.\n2 - INSERIR NOVA LISTA.'
}

def texto (escolha, query='print'):
    escolhido = textos_crus[escolha].split(sep='\n')
    if 'print' in query.lower():
        for linha in [fill(n) for n in escolhido]: print(linha)
    if 'list' in query.lower(): 
        return escolhido[0].split()
    if 'string' in query.lower(): return escolhido[0]
    