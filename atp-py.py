import ajuda
import tkinter
from tkinter import filedialog
import textwrap
from pathlib import Path

import sys



class node():
    """
    Classe para definir os nos/barras do equivalente
    """
    def __init__(self):
        self.numAna = 0
        self.vBase = 0.0
        self.nomeAna = ''
        self.nomeAtp = ''
        self.nomeGerAtp = ''

    def splitIt(self, linha):
        self.numAna = int(linha[0:5])
        try: self.vBase = float(linha[31:35])
        except(ValueError): pass
        self.nomeAna = linha[9:21].strip()



class branch():
    """
    """
    def __init__(self):
        self.nodeFrom = 0
        self.nodeTo = 0
        self.tipo = ''
        self.params = {'r1':0, 'x1':0, 'r0':0, 'x0':0}

    def divideIt(self, linha):
        self.nodeFrom = int(linha[0:5])
        self.nodeTo = int(linha[7:12])
        self.tipo = linha[16]
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





# FUNÇÕES ---------------------------------------------------------------------#

def get_DBAR(arquivo):

    flag = 0
    dbar = []

    dbar.append(node())
    dbar[-1].nomeAna = 'Terra'

    for linha in arquivo:
        if (flag == 3) & ('99999' in linha): 
            flag = 0
            break
        if (flag == 1) and not ('(' in linha[0]):
            flag = flag | 2  
        if flag == 3:
            dbar.append(node())
            dbar[-1].splitIt(linha)
        if 'DBAR' in linha[0:4]: flag = flag | 1

    return dict(zip([node.numAna for node in dbar], dbar))

def get_EQUIV(arquivo):
    flag = 0
    equiv = []
    for linha in arquivo:
        if '998' in linha[65:75]:
            equiv.append(branch())
            equiv[-1].divideIt(linha)
            flag = 1
        if (flag == 1) and ('99999' in linha[0:6]): break
    return equiv

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

def repeteco():
    repATP = set()

    for barra in gerATP.keys():
        if gerATP[barra] in repATP: 
            gerATP[barra] = 'F' + gerATP[barra][:-1]
            repeteco()
        repATP.add(gerATP[barra])


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

    dbar = get_DBAR(arqAna.open('r'))



    # LISTA DE EQUIVALENTES -------------------------------------------------------#

    equivLista = get_EQUIV(arqAna.open('r'))


    # valsOhm = percentOhm(equivLista, dbar[1])

    # IMPRESSAO DE BARRAS QUE POSSUEM EQUIVALENTES

    barrasEquiv = set()

    for n in equivLista: 
        barrasEquiv.add(n.nodeFrom)
        barrasEquiv.add(n.nodeTo)
    barrasEquiv = sorted(barrasEquiv)


    print('{0:>6s} {1:<11s} {2:>6s}'.format(*ajuda.texto('cabecalho', query='list')))
    for barra in barrasEquiv:
        print('{0:>6d} {1:<12s} {2!s:>6}'.format(barra, dbar[barra].nomeAna, dbar[barra].vBase))
    print(' ')
    print(ajuda.texto('barrasTot', query='string'), len(barrasEquiv))

    # INSERÇÃO DA LISTA DE NOMES PARA ATP PELO USUÁRIO ------------------------#

    arqAtp = Path('.\\testes\\nomes atp.txt')

    barrasATP = {0:'      '}
    cont = 1
    for barra in arqAtp.open('r'):
        barrasATP[barrasEquiv[cont]] = barra.strip()
        cont += 1


    #composição de nome auxiliares para geração no ATP

    gerATP = {}

    fontesATP = dict(barrasATP)
    for key in fontesATP.keys(): fontesATP[key] = ''


    for linha in range(len(equivLista[0])):
        if (equivLista[1][linha] == 0) and (equivLista[3][linha] != 9999.99):
            gerATP[linha] = 'F' + barrasATP[equivLista[0][linha]][:-1]
            fontesATP[equivLista[0][linha]] = gerATP[linha]

    repeteco() 



    with open('FONTES.TXT','w') as fontes:
        fontes.write('Lista dos nomes dos nós que possuem fontes\n')
        for barra in gerATP.keys():
            fontes.write(gerATP[barra] + '{0:>6s}'.format(str(dbar[1][equivLista[0][barra]])) + '\n')

    with open('FRONTEIRA.TXT','w') as front:
        front.write('Barras de Fronteira e seus nomes de ATP\n')
        front.write('{0:<9s}{1:<15s}{2:<9s}{3:<5s}\n'.format('NB', 'ANAFAS', 'ATP', 'FONTE'))
        for barra in barrasEquiv:
            front.write('{0:<9s}{1:<15s}{2:<9s}{3:<5s}\n'.format(str(barra), dbar[0][barra], barrasATP[barra], fontesATP[barra]))

    file_EQUI = open('equivalente.lib','w')

    makeEqui()

main()