import ajuda
from pathlib import Path
import argparse
from math import *
import subprocess
import win32api
import win32com.client

# para debugging
import sys


class args_Handler():
    """Classe para administrar os argumentos de entrada do programa em linha de 
    comando."""
    def __init__(self):
        parser = argparse.ArgumentParser(description='Cria um equivalente para o ATP', 
                        prog='ATP-EQUI')
        parser.add_argument('-c', default='es', metavar='Comando', nargs='?', 
                        help='Especifica que operacao deve ser feita [esRb] -Imprime\
                        [e]quivalente.lib, imprime [s]ource.lib, imprime [R]NCC.rel,\
                        lista [b]arras com equivalentes e sai.')
        parser.add_argument('-P', default='', metavar='Path', nargs='*', 
                        help="""Muda o caminho da Pasta de Trabalho. O padrão é 
                        mesma pasta do arquivo de execução do programa.""")
        self.args = parser.parse_args()

    def check_Paths(self, arqPaths):
        """Substitui o caminho da Pasta de Trabalho, se o usuario assim optou
        com o argumento -P na linha de comando."""
        if self.args.P != '':
            for arg_P in self.args.P:
                arg_P = arg_P.split('=')
                if 'cwd' in arg_P[0]:
                    arqPaths['cwd'] = Path(arg_P[1])

                if 'nomes-atp' in arg_P[0]:
                    arqPaths['Atp'] = arqPaths['cwd'] / Path(arg_P[1])

                if 'ana' in arg_P[0]:
                    arqPaths['Ana'] = arqPaths['cwd'] / Path(arg_P[1])

        return arqPaths






class Nodes:
    """Coleção de barras do equivalente.
    As barras/nós são representados pela Classe node. Aqui elas são concentradas
    num dicionário, 'nodes'.
    """
    def __init__(self):
        self.nodes = {}
        self.repATP = set()

    def addNode(self, node):
        self.nodes[node.numAna] = node

    def get_nomeAna(self, numAna):
        return self.nodes[numAna].nomeAna

    def get_vBase(self, numAna):
        return self.nodes[numAna].vBase

    def get_nomeAtp(self, numAna):
        return self.nodes[numAna].nomeAtp

    def get_nomeGerAtp(self, numAna):
        return self.nodes[numAna].nomeGerAtp

    def get_repATP(self):
        return self.repATP

    def alter(self, numAna = 0, dado = '', attr='nomeAna'):
        if dado != '':
            if attr == 'nomeAna': self.nodes[numAna].nomeAna = dado
            if attr == 'Vbase': self.nodes[numAna].Vbase = dado
            if attr == 'nomeAtp': self.nodes[numAna].nomeAtp = dado
            if attr == 'nomeGerAtp': self.nodes[numAna].nomeGerAtp = dado

    def get_all(self):
        return self.nodes.values()

    def check_repGerATP(self):
        repGerATP = set()

        for barra in self.get_all():
            if self.get_nomeGerAtp(barra.numAna) != '':
                if self.get_nomeGerAtp(barra.numAna) in repGerATP: 
                    self.alter(numAna = barra.numAna, attr = 'nomeGerAtp', dado = 'F' + self.get_nomeGerAtp(barra)[:-1])
                    self.check_repGerATP()
                repGerATP.add(self.get_nomeGerAtp(barra.numAna))

    def check_repATP(self):
        tempRep = set()

        for barra in self.get_all():
            if self.get_nomeAtp(barra.numAna) != '':
                if self.get_nomeAtp(barra.numAna) in tempRep:
                    self.repATP.add(self.get_nomeAtp(barra.numAna))
                tempRep.add(self.get_nomeAtp(barra.numAna))



class node:
    """
    Classe interna para definir os nos/barras do equivalente.
    """
    def __init__(self, linha=''):
        self.numAna = 0
        self.vBase = 0.0
        self.nomeAna = ''
        self.nomeAtp = ''
        self.nomeGerAtp = ''
        self.addLinha(linha=linha)

    def addLinha(self, linha):
        "Identifica e separa os valores da linha do DBAR do .ANA"
        if linha != '':
            self.numAna = int(linha[0:5])
            try: self.vBase = float(linha[31:35])
            except(ValueError): pass
            self.nomeAna = linha[9:21].strip()


class Branches:
    def __init__(self):
        self.branches = {}

    def addBranch(self, branch, dbar):
        self.branches[branch.nodes] = branch
        for n in branch.paramsOhm:
            if branch.params[n] == 9999.99:
                branch.paramsOhm[n] = 999999
            else: branch.paramsOhm[n] = branch.params[n] * dbar.get_vBase(branch.nodes[0])**2/10000

    def get_equiNodes(self):
        barrasEquiv = set()

        for n in self.branches.values():
            for no in range(2):
                barrasEquiv.add(n.nodes[no])
        return sorted(barrasEquiv)

    def get_tipo(self, node):
        return self.branches[node].tipo

    def get_all(self): return self.branches.values()


class branch:
    """
    Classe que representa um circuito. Os atributos da classe são:
    nodes: tuple com os nós DE e PARA
    tipo: G(erador), (T)rafo
    params: parâmetros em %
    paramsOhm: parâmetros em Ohms
    Inicialmente o circuito é criado com parâmetros zeros, até ser solicitado a
    inclusão dos valores obtidos do arquivo .ANA (addLinha)
    """
    def __init__(self, linha):
        self.nodes = (0,0)
        self.tipo = ''
        self.params = {'r1':0, 'x1':0, 'r0':0, 'x0':0}
        self.paramsOhm = {'r1':0, 'x1':0, 'r0':0, 'x0':0}
        self.addLinha(linha=linha)

    def addLinha(self, linha):
        "Identifica e separa os valores da linha de equivalente do DLIN do .ANA"
        if linha != '':
            self.nodes = int(linha[0:5]), int(linha[7:12])

            try:
                if '.' in linha[17:23]: self.params['r1'] = float(linha[17:23])
                else: self.params['r1'] = float(linha[17:23])/100
            except(ValueError):self.params['r1'] = 0
            try:
                if '.' in linha[23:29]: self.params['x1'] = float(linha[23:29])
                else: self.params['x1'] = float(linha[23:29])/100
            except(ValueError): self.params['x1'] = 0
            try:
                if '.' in linha[29:35]: self.params['r0'] = float(linha[29:35])
                else: self.params['r0'] = float(linha[29:35])/100
            except(ValueError): self.params['r0'] = 0
            try:
                if '.' in linha[35:41]: self.params['x0'] = float(linha[35:41])
                else: self.params['x0'] = float(linha[35:41])/100
            except(ValueError): self.params['x0'] = 0

            if (self.nodes[1] == 0) and (self.params['r1'] != 9999.99):
                self.tipo = 'G'
            else: self.tipo = linha[16]




# FUNÇÕES ---------------------------------------------------------------------#

def get_DBAR(arquivo, colecao):
    """Obtém todo o conteúdo do código DBAR do arquivo .ANA"""

    flag = 0
    dbar = colecao

    #Acrescenta a barra/nó Terra ao conjunto de barras
    dbar.addNode(node())
    dbar.alter(dado = 'Terra')

    for linha in arquivo:
        if (flag == 3) & ('99999' in linha): 
            flag = 0
            break
        if (flag == 1) and not ('(' in linha[0]):
            flag = flag | 2  
        if flag == 3:
            dbar.addNode(node(linha))
        if 'DBAR' in linha[0:4]: flag = flag | 1

    return dbar

def get_EQUIV(arquivo, colecao, dbar):
    """Obtém todo o conteúdo dos circuitos de equivalentes (marcados com 998) do
    arquivo .ANA."""

    flag = 0
    equiv = colecao
    for linha in arquivo:
        if '998' in linha[65:75]:
            equiv.addBranch(branch(linha), dbar)
            flag = 1
        if (flag == 1) and ('99999' in linha[0:6]): break
    return equiv

def get_ATP(arquivo, dbar, equiv):
    """Faz a leitura do arquivo de texto com os nomes das barras de fronteira 
    para o ATP.
    Esses nomes são acrescentados nas instâncias dos nós.
    Em seguida, é feito uma verificação para ver se não há nomes de nó repeti-
    dos, que é uma desgraça para o ATP.
    Por fim, cria-se uma sequência de nomes de nó com geradores para o ATP."""

    for barra in equiv.get_equiNodes()[1:]:
        nomeATP = arquivo.readline().strip()
        dbar.alter(numAna = barra, dado = nomeATP, attr = 'nomeAtp')
        try: 
            if equiv.get_tipo((barra,0)) == 'G':
                dbar.alter(numAna = barra, dado = 'F' + nomeATP[:-1], attr = 'nomeGerAtp')
        except: pass


    dbar.check_repGerATP() 

    dbar.check_repATP()


def percentOhm(params, vbas):
    "Converte determinada sequência de parâmetros em \% para Ohms"
    paramsOhm = []
    for item in params[3:]:
        paramsOhm.append([])
        for valor in item:
            if valor == 999999:
                paramsOhm[params[3:].index(item)].append('999999')
            else:
                base = vbas[params[0][item.index(valor)]]**2/100
                paramsOhm[params[3:].index(item)].append(str(valor*base/100)[:6])
    return paramsOhm

def make_Equi(arqPaths, equiv, dbar):
    """Funçaõ para compor o arquivo-cartão /BRANCH com extensão .lib, do ATP,
    que irá conter a rede equivalentada pelo Anafas."""

    arquivo = arqPaths['cwd'].resolve() / Path(str(arqPaths['Ana'].stem) + '-equivalentes.lib')
    arquivo = arquivo.open('w')
    numTrf = 1
    
    arquivo.write('/BRANCH\n')

    # Loop 'for' sobre cada circuito equivalente
    for branch in equiv.get_all():
        # Escreve o delimitador superior, com vários '=' e, embaixo, o nome das
        #barras DE e PARA
        arquivo.write('C ' + 77*'=' + '\n' + 'C =====' + 
            dbar.get_nomeAna(branch.nodes[0]) + ' - ' + 
            dbar.get_nomeAna(branch.nodes[1]) + '\n')

        # Compões a lista com o nome do nó DE para cada uma das 3 fases
        nodeFrom = [str(dbar.get_nomeAtp(branch.nodes[0]))+'A',
                    str(dbar.get_nomeAtp(branch.nodes[0]))+'B',
                    str(dbar.get_nomeAtp(branch.nodes[0]))+'C']

        # A seguir, é feita a composição da lista com o nome do nó PARA, a de-
        #pender do tipo de elemento que se deseja representar no ATP


        # Se for um 'Gerador':
        if branch.tipo == 'G':
            nodeTo = [str(dbar.get_nomeGerAtp(branch.nodes[0]))+'A',
                    str(dbar.get_nomeGerAtp(branch.nodes[0]))+'B',
                    str(dbar.get_nomeGerAtp(branch.nodes[0]))+'C']

        # Se for um 'Shunt':
        elif branch.nodes[1] == 0:
            nodeTo = [' '*6 for n in range(3)]

        # Se for um 'Trafo':
        elif branch.tipo == 'T':
             nodeTo = [str(numTrf)+'TIEA',
                        str(numTrf)+'TIEB',
                        str(numTrf)+'TIEC']

        # Se for uma 'LT':
        else:
            nodeTo = [str(dbar.get_nomeAtp(branch.nodes[1]))+'A',
                    str(dbar.get_nomeAtp(branch.nodes[1]))+'B',
                    str(dbar.get_nomeAtp(branch.nodes[1]))+'C'] 

        # A seguir, é feita a escrita dos dados do circuito no arquivo-cartão.

        arquivo.write('51{}{:6}'.format(nodeFrom[0],nodeTo[0]) + 12*' ' + 
            '{0!s:<.6}'.format(branch.paramsOhm['r0']) + 6*' ' +
            '{0!s:<.12}'.format(branch.paramsOhm['x0']) + '\n')
        arquivo.write('52{}{:6}'.format(nodeFrom[1],nodeTo[1]) + 12*' ' + 
            '{0!s:<.6}'.format(branch.paramsOhm['r1']) + 6*' ' +
            '{0!s:<.12}'.format(branch.paramsOhm['x1']) + '\n')
        arquivo.write('53' + nodeFrom[2] + nodeTo[2] + '\n')

        # Se for um transformador, é colocado um transformador ideal para fazer
        #a relação de tensão entre as duas barras. A impedância da ligação já é
        #escrita na etapa acima.

        if branch.tipo == 'T':


            arquivo.write('  TRANSFORMER' + 25*' ' + 'ATIE'+
                '{0:<2s}'.format(str(numTrf))+'1.E6\n')
            arquivo.write(' '*12 + '9999' + '\n')
            arquivo.write(' 1'+'{0:<6s}'.format(str(numTrf)+'TIEA') + ' '*18 +
                         '.00001.00001'+str(dbar.get_vBase(branch.nodes[0])) + '\n')
            arquivo.write(' 2'+ dbar.get_nomeAtp(branch.nodes[1]) +'A' + ' '*18 +
                         '.00001.00001'+str(dbar.get_vBase(branch.nodes[1]))+ '\n')

            arquivo.write('  TRANSFORMER ATIE'+'{0:<2s}'.format(str(numTrf)) + 
                        ' '*18 + '{0:<6s}'.format('BTIE'+str(numTrf))+'\n')
            arquivo.write(' 1'+'{0:<6s}'.format(str(numTrf) + 'TIEB') + '\n')
            arquivo.write(' 2'+dbar.get_nomeAtp(branch.nodes[1])+'B' + '\n')

            arquivo.write('  TRANSFORMER ATIE'+'{0:<2s}'.format(str(numTrf)) + 
                        ' '*18 + '{0:<6s}'.format('CTIE'+str(numTrf))+'\n')
            arquivo.write(' 1'+'{0:<6s}'.format(str(numTrf) + 'TIEC') + '\n')
            arquivo.write(' 2'+dbar.get_nomeAtp(branch.nodes[1])+'C' + '\n')

            numTrf += 1

def make_Source(arqPaths, dbar):
    """Escreve um arquivo-cartão /SOURCE no formato .lib com as fontes do siste-
    equivalente."""
    arquivo = arqPaths['cwd'].resolve() / Path(str(arqPaths['Ana'].stem) + '-source.lib')
    arquivo = arquivo.open('w')
    arquivo.write('/SOURCE\nC < n 1><>< Ampl.  >< Freq.  ><Phase/T0><   A1   ><   T1   >< TSTART >< TSTOP  >\n')
    for barra in dbar.get_all():
        if barra.nomeGerAtp != '':
            arquivo.write('14{:5}A  {!s:10.10}{:10d}'.format(barra.nomeGerAtp, 
                str(barra.vBase*sqrt(2/3)*1000), 60) + 30*' ' + 
                '{:10d}{:10d}'.format(-1,100) + '\n')
            arquivo.write('14{:5}B  {!s:10.10}{:10d}{:10d}'.format(barra.nomeGerAtp, 
                barra.vBase*sqrt(2/3)*1000, 60, -120) + 20*' ' + 
                '{:10d}{:10d}'.format(-1,100) + '\n')
            arquivo.write('14{:5}C  {!s:10.10}{:10d}{:10d}'.format(barra.nomeGerAtp, 
                barra.vBase*sqrt(2/3)*1000, 60, -240) + 20*' ' + 
                '{:10d}{:10d}'.format(-1,100) + '\n')

def make_Rncc(arqPaths, equiv):
    """Roda o Anafas para obter o Relatório de Níveis de Curto-Circuito do sis-
    tema equivalentado. Só estão ligadas as barras de fronteira.
    Cria-se arquivos-fantoche dummy* para poder rodar o Anafas em modo
    Batch.
    """
    dummyAna = arqPaths['cwd'] / Path('dummy-' + arqPaths['Ana'].name)
    dummyInp = arqPaths['cwd'] / Path('dummy.inp')
    dummyBar = arqPaths['cwd'] / Path('dummy.bar')
    dummyRel = arqPaths['cwd'] / Path(str(arqPaths['Ana'].resolve().stem) + '-rncc.rel')
    dummyBat = arqPaths['cwd'] / Path('dummy.bat')

    arqAna = arqPaths['Ana'].open('r')

    # Obtém as barras que possuem equivalentes (chamadas de barras de fronteira)
    equiNodes = equiv.get_equiNodes()[1:]


    #Escreve o arquivo .ANA somente com as barras de fronteira

    with dummyAna.open('w') as dumana:
        flag = 0
        for linha in arqAna.readlines():
            if '998' in linha[69:72]: flag = 0
            if 'dmut' in linha.lower(): flag = 2
            if 'dare' in linha.lower(): flag = 0
            if 'dbar' in linha.lower(): flag = 3

            if flag == 1: dumana.write('('+linha)
            elif flag == 2: pass
            elif flag == 3:
                try:
                    if (int(linha[:5]) in equiNodes) or \
                    (int(linha[:5]) == 99999): dumana.write(linha)
                    else: dumana.write('('+linha)
                except: dumana.write(linha)
            else: dumana.write(linha)

            if ('dcir' in linha.lower()) or ('dlin' in linha.lower()): flag  = 1

    # Escreve o arquivo .BAR com as barras para se rodar o RNCC

    with dummyBar.open('w') as dumbar:
        dumbar.write('ANAFAS.BAR\nbla bla\n')
        for barra in equiNodes:
            dumbar.write(str(barra)+'\n')

    # Escreve o arquivo batch .INP

    with dummyInp.open('w') as duminp:
        duminp.write('dcte\nruni ka\n9999\n\n')
        duminp.write('arqv dado\n')
        duminp.write(str(dummyAna.resolve()) + '\n\n')
        duminp.write('arqv cbal\n')
        duminp.write(str(dummyBar.resolve()) + '\n\n')
        duminp.write('arqv said\n')
        duminp.write(str(dummyRel.absolute()) + '\n\n')
        duminp.write('rela conj rncc\n\nFIM')

    # Escreve o arquivo .BAT para poder executar o Anafas em modo batch

    with dummyBat.open('w') as dumbat:
        dumbat.write('cd /d c:\\cepel\\anafas 6.5\n\nSTART anafas.exe -WIN ' + 
            '"' + str(dummyInp.resolve()) + '"')

    # Roda o arquivo .bat    

    shell = win32com.client.Dispatch("WScript.Shell")
    shell.Run(str(dummyBat))
    while not shell.AppActivate("Anafas"): pass
    win32api.Sleep(500)
    shell.SendKeys("s")

    # Elimina todos os arquivos temporários que foram usados para esse processo

    subprocess.call('rm {}/dum* {}/DUM*'.format(str(arqPaths['cwd']),
        str(arqPaths['cwd'])))


def make_Rela(relaBuffer, arqPaths):
    """Função para escrever o relatório. Ela é chamada toda vez que o buffer 
    relaBuffer é escrito. O que será escrito no relatório dependerá do que está 
    no buffer.
    O buffer é um tuple com uma string para selecionar o texto e um número 
    arbitrário de elementos, de forma a fornecer a essa função as informações
    necessárias para escrever o relatório.
    relaBuffer = 'str' + *args
    O conjunto dos possíveis buffers é:
    'Ana' + binário indicando o sucesso da leitura do arquivo - Referente à lei-
    tura do arquivo .ANA com os dados de curto-circuito saídos do Anafas/SAPRE.
    'rncc' - Referente à emissão de Relatório de Níveis de Curto-circuito pelo
    Anafas
    'barras' - Referente à opção do usuário de apenas emitir as barras de fron-
    teira do equivalente .ANA.
    'atp' + binário indicando sucesso da leitura do arquivo - Referente à 
    leitura do arquivo de texto com os nomes de barras de fronteira a serem uti-
    lizadas no ATP.
    'diff' + diferença no número de barras entre o arquivo .ANA e o de texto com
    os nomes de barras de fronteira do ATP.
    'src' - Referente a requisição de um cartão /SOURCE para o ATP com as fontes
    das barras de fronteira.
    'equi' + conjunto de barras equivalentes + conjunto de circuitos equivalen-
    tes - Referente à impressão no relatório dos dados de barras do equivalente.

    Essa função chama o arquivo ajuda.py, que possui os textos padrão para escre
    ver no relatório.
    """

    rela = arqPaths['Ana'].parent / Path(arqPaths['Ana'].stem + '-relatorio.rel')
    
    if 'Ana' in relaBuffer[0]:
        #Compõe o nome do arquivo de relatório a partir do nome do arquino .ANA
        rela = rela.open('w')
        
        if not relaBuffer[1]:
            rela.write(ajuda.texto('relaErroArq').format(arqPaths['Ana'].absolute()))
        else: rela.write(ajuda.texto('relaArq').format(arqPaths['Ana'].resolve()))
    else: rela = rela.open('a') 

    if 'rncc' in relaBuffer[0]:
        rela.write(ajuda.texto('relaRncc').format(arqPaths['cwd'].resolve() / Path(str(arqPaths['Ana'].resolve().stem) + '-rncc.rel')))

    if 'barras' in relaBuffer[0]:
        barrasEquiv = relaBuffer[2].get_equiNodes()[1:]
        rela.write(ajuda.texto('relaBarra').format(len(barrasEquiv)))

        rela.write('{0:^6s} {1:<11s} {2:^6s}\n'\
            .format(*ajuda.texto('cabecalho', query='list')))
        for barra in barrasEquiv:
            rela.write('{0:^6d} {1:<12s} {2!s:^6}\n'.format(barra, relaBuffer[1].get_nomeAna(barra), relaBuffer[1].get_vBase(barra)))

    if 'atp' in relaBuffer[0]:
        if not relaBuffer[1]:
            rela.write(ajuda.texto('relaErroArq').format(arqPaths['Atp'], Path.cwd()/arqPaths['Atp']))
        else: rela.write(ajuda.texto('relaArq').format(arqPaths['Atp'].name))

    if 'diff' in relaBuffer[0]:
        rela.write(ajuda.texto('relaErroDiff').format(relaBuffer[1]))

    if 'src' in relaBuffer[0]:
        rela.write(ajuda.texto('relaSrc').format(arqPaths['cwd'].resolve() / Path(str(arqPaths['Ana'].stem) + '-source.lib')))

    if 'equi' in relaBuffer[0]:
        fontes = set()
        for barra in relaBuffer[2].get_equiNodes():
            fontes.add(relaBuffer[1].get_nomeGerAtp(barra))
        rela.write(ajuda.texto('relaEqui').format(Path.cwd()/arqPaths['cwd'].resolve() / Path(str(arqPaths['Ana'].stem) + '-equivalentes.lib'), len(relaBuffer[2].get_equiNodes()), len(fontes)-1))
        rela.write('{:^6}{:^15}{:^10}{:^10}\n'.format(*ajuda.texto('cabecalhoF', query='list')))
        for barra in relaBuffer[2].get_equiNodes():
            rela.write('{:^6d}{:^15}{:^11}{:^11}\n'.format(barra, relaBuffer[1].get_nomeAna(barra), relaBuffer[1].get_nomeAtp(barra), relaBuffer[1].get_nomeGerAtp(barra)))
        






class relaWatcher():
    """Classe Descritor para monitorar o andamento do relatório, com o uso da
    função Property.
    Quando se altera o valor do buffer bufferRela, ele já chama a função que
    escreve o relatório. Assim, a escrita do relatório é dinâmica."""

    def __init__(self, make_Rela, arqPaths):
        self.make_Rela = make_Rela
        self.arqPaths = arqPaths

    def setter(self, value):
        self._relaBuffer = value
        self.make_Rela(self._relaBuffer, self.arqPaths)
        self._relaBuffer = 0

    def setter2(self, value):
        if not value:
            sys.exit()

    relaBuffer = property(fset=setter)
    runTime = property(fset=setter2)




def main():

    print('Programa iniciou')

    #Definição da estrutura do dicionário com os caminhos para os arquivos de
    #entrada e saída

    arqPaths = {'Ana' : '',
                'Atp' : '',
                'cwd' : ''}

    #Instancia a classe que trata dos argumentos de linha de comando
    argumnt = args_Handler()

    #Verifica e busca os caminhos de arquivo fornecidos se o usuário assim optou
    #na linha de comando com o argumento -P
    arqPaths = argumnt.check_Paths(arqPaths)

    # Inclui os caminhos-padrão na lista, caso o usuário não tenha mudado. E
    #muda o diretório de trabalho para o que o usuário optou.
    if not arqPaths['cwd']: arqPaths['cwd'] = Path.cwd()
    if not arqPaths['Ana']: arqPaths['Ana'] = arqPaths['cwd'] / Path('equi.ana')
    if not arqPaths['Atp']: arqPaths['Atp'] = arqPaths['cwd'] / Path('nomesatp.txt')

    #Grava o tipo de operação requisitada pelo usuário com o comando -c
    comando = argumnt.args.c

    #Instancia a classe de monitoramento do status do relatório. Conforme os
    # processos vão avançando, o relatório vai sendo escrito.
    relaWatch = relaWatcher(make_Rela, arqPaths)


    # Verifica a existência do arquivo .ANA
    try:
        arqPaths['Ana'].resolve()
    except(FileNotFoundError):
        relaWatch.relaBuffer = ('Ana',0)
        relaWatch.runTime = 0

    # Inicia a execução das operações e obtenção de dados


    # Obtém a lista de barras de fronteira e os circuitos equivalentes 
    #conectados a elas do arquivo .ANA
    dbar = get_DBAR(arqPaths['Ana'].open('r'), Nodes())
    equiv = get_EQUIV(arqPaths['Ana'].open('r'), Branches(), dbar)

    relaWatch.relaBuffer = ('Ana',1)

    # A seguir é feita a seleção do modo de operação do programa, de acordo com
    #os argumentos que o usuário entrou na linha de comando.

    if 'R' in comando:
        make_Rncc(arqPaths, equiv)
        relaWatch.relaBuffer = ('rncc',)

    if 'b' in comando:
        relaWatch.relaBuffer = ('barras', dbar, equiv)  

    else:
        try:
            get_ATP(arqPaths['Atp'].open('r'), dbar, equiv)
            diff = abs(len(arqPaths['Atp'].open('r').readlines()) - len(equiv.get_equiNodes()[1:]))
            relaWatch.relaBuffer = ('atp', 1)
            if diff > 0:
                relaWatch.relaBuffer = ('diff', diff)
                relaWatch.runTime = 0
        except(FileNotFoundError): 
            relaWatch.relaBuffer = ('atp', 0)
            relaWatch.runTime = 0


    if 's' in comando:
        make_Source(arqPaths, dbar)
        relaWatch.relaBuffer = ('src',)

    if 'e' in comando:
        make_Equi(arqPaths, equiv, dbar)
        relaWatch.relaBuffer = ('equi', dbar, equiv)

    # FIM DA EXECUÇÃO
    relaWatch.relaBuffer = ('fim',)

    # print(ajuda.texto('fim').format(arqPaths['Rela']))



main()