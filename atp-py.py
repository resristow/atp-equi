import ajuda
import tkinter
from tkinter import filedialog
import textwrap
from pathlib import Path

import sys

rela = Path('RELATORIO_SAIDA.txt').open('w')

class Nodes:
    "Coleção de barras do equivalente"
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
        return self.nodes

    def check_repGerATP(self):
        repGerATP = set()

        for barra in self.get_all().keys():
            if self.get_nomeGerAtp(barra) != '':
                if self.get_nomeGerAtp(barra) in repGerATP: 
                    self.alter(numAna = barra, attr = 'nomeGerAtp', dado = 'F' + self.get_nomeGerAtp(barra)[:-1])
                    self.check_repGerATP()
                repGerATP.add(self.get_nomeGerAtp(barra))

    def check_repATP(self):
        tempRep = set()

        for barra in self.get_all().keys():
            if self.get_nomeAtp(barra) != '':
                if self.get_nomeAtp(barra) in tempRep:
                    self.repATP.add(self.get_nomeAtp(barra))
                tempRep.add(self.get_nomeAtp(barra))



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

    def addBranch(self, branch):
        self.branches[branch.nodes] = branch

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
    """
    def __init__(self, linha):
        self.nodes = (0,0)
        self.tipo = ''
        self.params = {'r1':0, 'x1':0, 'r0':0, 'x0':0}
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

            if (self.nodes[1] == 0) and (int(self.params['r1']) != 9999):
                self.tipo = 'G'
            else: self.tipo = linha[16]




# FUNÇÕES ---------------------------------------------------------------------#

def get_DBAR(arquivo, colecao):

    flag = 0
    dbar = colecao


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

def get_EQUIV(arquivo, colecao):
    flag = 0
    equiv = colecao
    for linha in arquivo:
        if '998' in linha[65:75]:
            equiv.addBranch(branch(linha))
            flag = 1
        if (flag == 1) and ('99999' in linha[0:6]): break
    return equiv

def get_ATP(arquivo, dbar, equiv, barrasEquiv):


    for barra in barrasEquiv:
        nomeATP = arquivo.readline().strip()
        dbar.alter(numAna = barra, dado = nomeATP, attr = 'nomeAtp')
        try: 
            if equiv.get_tipo((barra,0)) == 'G':
                dbar.alter(numAna = barra, dado = 'F' + nomeATP[:-1], attr = 'nomeGerAtp')
        except: pass


    dbar.check_repGerATP() 

    dbar.check_repATP()


def percentOhm(params, vbas):
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

def makeEqui():
    file_EQUI.write('/BRANCH\n')
    numTrf = 0

    for linha in range(len(equivLista[0])):

        tipo = 'geral'
        if equivLista[2][linha] == 'T':
            tipo = 'trafo'
            numTrf += 1
        elif linha in gerATP.keys(): tipo = 'gerador'

        writeEqui(linha, numTrf, tipo)

        

def writeEqui(linha, numTrf, tipo = 'geral'):

    if tipo == 'geral':
        file_EQUI.write('C =====' + dbar[0][equivLista[0][linha]] + ' - ' + dbar[0][equivLista[1][linha]] + '\n')
        if equivLista[1][linha] != 0:
            file_EQUI.write('51' + barrasATP[equivLista[0][linha]] + 'A' + barrasATP[equivLista[1][linha]] + 'A' + 12*' ' \
                + '{0:<6s}'.format(valsOhm[2][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[3][linha]) + '\n')
            file_EQUI.write('52' + barrasATP[equivLista[0][linha]] + 'B' + barrasATP[equivLista[1][linha]] + 'B' + 12*' ' \
                + '{0:<6s}'.format(valsOhm[0][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[1][linha]) + '\n')
            file_EQUI.write('53' + barrasATP[equivLista[0][linha]] + 'C' + barrasATP[equivLista[1][linha]] + 'C\n')
        else: 
            file_EQUI.write('51' + barrasATP[equivLista[0][linha]] + 'A' + barrasATP[equivLista[1][linha]] + 12*' ' \
                + '{0:<6s}'.format(valsOhm[2][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[3][linha]) + '\n')
            file_EQUI.write('52' + barrasATP[equivLista[0][linha]] + 'B' + barrasATP[equivLista[1][linha]] + 12*' ' \
                + '{0:<6s}'.format(valsOhm[0][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[1][linha]) + '\n')
            file_EQUI.write('53' + barrasATP[equivLista[0][linha]] + 'C' + barrasATP[equivLista[1][linha]] + '\n')

    elif tipo == 'gerador':
        file_EQUI.write('C =====' + dbar[0][equivLista[0][linha]] + ' - ' + dbar[0][equivLista[1][linha]] + '\n')

        file_EQUI.write('51' + gerATP[linha] + 'A' + barrasATP[equivLista[0][linha]] + 'A' + 12*' ' \
            + '{0:<6s}'.format(valsOhm[2][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[3][linha]) + '\n')
        file_EQUI.write('52' + gerATP[linha] + 'B' + barrasATP[equivLista[0][linha]] + 'B' + 12*' ' \
            + '{0:<6s}'.format(valsOhm[0][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[1][linha]) + '\n')
        file_EQUI.write('53' + gerATP[linha] + 'C' + barrasATP[equivLista[0][linha]] + 'C\n')

        

    elif tipo == 'trafo':
        file_EQUI.write('C =====' + dbar[0][equivLista[0][linha]] + ' - ' + dbar[0][equivLista[1][linha]] + '\n')
        file_EQUI.write('51' + barrasATP[equivLista[0][linha]] + 'A' + '{0:<6s}'.format(str(numTrf) + 'TIEA') + 12*' ' \
            + '{0:<6s}'.format(valsOhm[2][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[3][linha]) + '\n')
        file_EQUI.write('52' + barrasATP[equivLista[0][linha]] + 'B' + '{0:<6s}'.format(str(numTrf) + 'TIEB') + 12*' ' \
            + '{0:<6s}'.format(valsOhm[0][linha]) + 6*' ' + '{0:<12s}'.format(valsOhm[1][linha]) + '\n')
        file_EQUI.write('53' + barrasATP[equivLista[0][linha]] + 'C' + '{0:<6s}'.format(str(numTrf) + 'TIEC') + '\n')
        file_EQUI.write('  TRANSFORMER                         ATIE'+'{0:<2s}'.format(str(numTrf))+'1.E6\n')
        file_EQUI.write(' '*12 + '9999' + '\n')
        file_EQUI.write(' 1'+'{0:<6s}'.format(str(numTrf) + 'TIEA') + ' '*19 + '.0001 .0001'+str(dbar[1][equivLista[0][linha]])+ '\n')
        file_EQUI.write(' 2'+barrasATP[equivLista[1][linha]]+'A' + ' '*19 + '.0001 .0001'+str(dbar[1][equivLista[1][linha]])+ '\n')
        file_EQUI.write('  TRANSFORMER ATIE'+'{0:<4s}'.format(str(numTrf))+ ' '*16 + 'BTIE'+'{0:<2s}'.format(str(numTrf))+'\n')
        file_EQUI.write(' 1'+'{0:<6s}'.format(str(numTrf) + 'TIEB') + '\n')
        file_EQUI.write(' 2'+barrasATP[equivLista[1][linha]]+'B' + '\n')
        file_EQUI.write('  TRANSFORMER ATIE'+'{0:<4s}'.format(str(numTrf))+ ' '*16 + 'CTIE'+'{0:<2s}'.format(str(numTrf))+'\n')
        file_EQUI.write(' 1'+'{0:<6s}'.format(str(numTrf) + 'TIEC') + '\n')
        file_EQUI.write(' 2'+barrasATP[equivLista[1][linha]]+'C' + '\n')

    file_EQUI.write('C ' + 77*'=' + '\n')




def main():


    # LEITURA DO ARQUIVO ORIGINAL -------------------------------------------------#

    # ajuda.texto('welcome')
    # ajuda.texto('queryArq')
    # ANA = input()
    # while ANA != '':
    #     ajuda.texto('queryArq')
    #     ANA = input()
    # else:
    #     root_ANA = Tk()
    #     root_ANA.withdraw()
        # file_ANA = open(filedialog.askopenfilename(),'r')
        # root_ANA.destroy()


    arqAna = Path('./Testes/equi.ana')
        
    # LISTA DE BARRAS --------------------------------------------------#


    dbar = get_DBAR(arqAna.open('r'), Nodes())


    # LISTA DE EQUIVALENTES -------------------------------------------------------#

    equiv = get_EQUIV(arqAna.open('r'), Branches())

    barrasEquiv = equiv.get_equiNodes()[1:]


    get_ATP(Path('./testes/nomes atp.txt').open('r'), dbar, equiv, barrasEquiv)    

    # valsOhm = percentOhm(equivLista, dbar[1])

    ExecOK = 0

    relaNotOk = """
O arquivo ATP não chegou a ser lido. Para auxiliar o usuário a elaborar a 
lista com os nomes, segue abaixo a relação de barras que possuem equivalentes
conectados:
"""

    relaAna = """
Leitura do arquivo .ANA de equivalentes feita com sucesso. O total de barras 
que possuem circuitos equivalentes conectados é {}.
""".format(len(barrasEquiv))

    relaATPok = """
Leitura do arquivo com os nomes de nó para o ATP feita com sucesso. Não há 
barras repetidas. A lista de número de barra e nome do .ANA e seus respec-
tivos nomes do ATP é dada abaixo:
"""

    relaATPnotOk = """
Leitura do arquivo com os nomes de nó para o ATP feita com sucesso. Foram
detectadas {} barras repetidas. São elas: {} . A lista de número de
barra e nome do .ANA e seus respectivos nomes do ATP é dada abaixo:
""".format(len(dbar.get_repATP()), dbar.get_repATP())




    rela.write(relaAna)
    if ExecOK == 0:
        rela.write(relaNotOk + '{0:>6s} {1:<11s} {2:>6s}\n'\
            .format(*ajuda.texto('cabecalho', query='list')))
        for barra in barrasEquiv:
            rela.write('{0:>6d} {1:<12s} {2!s:>6}\n'.format(barra, dbar.get_nomeAna(barra), dbar.get_vBase(barra)))
    if len(dbar.get_repATP()) == 0: rela.write(relaATPok)
    else:
        rela.write(relaATPnotOk)
    for barra in barrasEquiv:
        rela.write('{0:>6d}{1:<12s}{2:>6}{3:>6} \n'.format(barra, dbar.get_nomeAna(barra), dbar.get_nomeAtp(barra), dbar.get_nomeGerAtp(barra)))

    # INSERÇÃO DA LISTA DE NOMES PARA ATP PELO USUÁRIO ------------------------#




    sys.exit()


    file_EQUI = open('equivalente.lib','w')

    makeEqui()

main()