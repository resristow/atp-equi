import ajuda
import textwrap
from pathlib import Path
import argparse
from math import *
import subprocess
import win32api
import win32com.client

import sys


class args_Handler():
    def __init__(self):
        parser = argparse.ArgumentParser(description='Cria um equivalente para o ATP', 
                        prog='ATP-EQUI')
        parser.add_argument('-c', default='es', metavar='Comando', nargs='?', 
                        help='Especifica que operacao deve ser feita [esRb] -Imprime\
                        [e]quivalente.lib, imprime [s]ource.lib, imprime [R]NCC.rel,\
                        lista [b]arras com equivalentes e sai.')
        parser.add_argument('-P', default='', metavar='Path', nargs='*', 
                        help='Muda a localização padrão dos arquivos [esAarN] \
                        [e]quivalentes.lib, [s]ource.lib, nomes[A]tp.txt, equi.[a]na,\
                        [r]elatorio.OUT, R[N]CC.rel')
        self.args = parser.parse_args()

    def check_Paths(self, arqPaths):
        if self.args.P != '':
            for cami in self.args.P[0]:
                if 'e' in cami: arqPaths['Lib'] = Path(self.args.P[self.args.P[0].index(cami) +
                 1])
                if 's' in cami: arqPaths['Src'] = Path(self.args.P[self.args.P[0].index(cami) +
                 1])
                if 'A' in cami: arqPaths['Atp'] = Path(self.args.P[self.args.P[0].index(cami) +
                 1])
                if 'a' in cami: arqPaths['Ana'] = Path(self.args.P[self.args.P[0].index(cami) +
                 1])
                if 'r' in cami: arqPaths['Rela'] = Path(self.args.P[self.args.P[0].index(cami)
                 + 1])
                if 'N' in cami: arqPaths['Rncc'] = Path(self.args.P[self.args.P[0].index(cami)
                 + 1])
        return arqPaths






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

def get_EQUIV(arquivo, colecao, dbar):
    flag = 0
    equiv = colecao
    for linha in arquivo:
        if '998' in linha[65:75]:
            equiv.addBranch(branch(linha), dbar)
            flag = 1
        if (flag == 1) and ('99999' in linha[0:6]): break
    return equiv

def get_ATP(arquivo, dbar, equiv):


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

def make_Equi(arquivo, equiv, dbar):
    arquivo = arquivo.open('w')
    arquivo.write('/BRANCH\n')
    numTrf = 1

    for branch in equiv.get_all():
        arquivo.write('C ' + 77*'=' + '\n' + 'C =====' + 
            dbar.get_nomeAna(branch.nodes[0]) + ' - ' + 
            dbar.get_nomeAna(branch.nodes[1]) + '\n')

        nodeFrom = [str(dbar.get_nomeAtp(branch.nodes[0]))+'A',
                    str(dbar.get_nomeAtp(branch.nodes[0]))+'B',
                    str(dbar.get_nomeAtp(branch.nodes[0]))+'C']

        if branch.tipo == 'G':
            nodeTo = [str(dbar.get_nomeGerAtp(branch.nodes[0]))+'A',
                    str(dbar.get_nomeGerAtp(branch.nodes[0]))+'B',
                    str(dbar.get_nomeGerAtp(branch.nodes[0]))+'C']

        elif branch.nodes[1] == 0:
            nodeTo = [' '*6 for n in range(3)]

        elif branch.tipo == 'T':
             nodeTo = [str(numTrf)+'TIEA',
                        str(numTrf)+'TIEB',
                        str(numTrf)+'TIEC']

        else:
            nodeTo = [str(dbar.get_nomeAtp(branch.nodes[1]))+'A',
                    str(dbar.get_nomeAtp(branch.nodes[1]))+'B',
                    str(dbar.get_nomeAtp(branch.nodes[1]))+'C'] 

        arquivo.write('51{}{:6}'.format(nodeFrom[0],nodeTo[0]) + 12*' ' + 
            '{0!s:<.6}'.format(branch.paramsOhm['r0']) + 6*' ' +
            '{0!s:<.12}'.format(branch.paramsOhm['x0']) + '\n')
        arquivo.write('52{}{:6}'.format(nodeFrom[1],nodeTo[1]) + 12*' ' + 
            '{0!s:<.6}'.format(branch.paramsOhm['r1']) + 6*' ' +
            '{0!s:<.12}'.format(branch.paramsOhm['x1']) + '\n')
        arquivo.write('53' + nodeFrom[2] + nodeTo[2] + '\n')

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

def make_Source(arquivo, dbar):
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

def make_Rncc(arquivo, rncc, dbar, equiv):
    dummyAna = Path.cwd() / Path('dummy_' + arquivo.name)
    dummyInp = Path.cwd() / Path('dummy.inp')
    dummyBar = Path.cwd() / Path('dummy.bar')
    dummyRel = Path.cwd() / rncc
    dummyBat = Path.cwd() / Path('dummy.bat')

    equiNodes = equiv.get_equiNodes()[1:]

    arqAna = arquivo.open('r')

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

    with dummyBar.open('w') as dumbar:
        dumbar.write('ANAFAS.BAR\nbla bla\n')
        for barra in equiNodes:
            dumbar.write(str(barra)+'\n')

    with dummyInp.open('w') as duminp:
        duminp.write('dcte\nruni ka\n9999\n\n')
        duminp.write('arqv dado\n')
        duminp.write(str(dummyAna) + '\n\n')
        duminp.write('arqv cbal\n')
        duminp.write(str(dummyBar) + '\n\n')
        duminp.write('arqv said\n')
        duminp.write(str(dummyRel) + '\n\n')
        duminp.write('rela conj rncc\n\nFIM')

    with dummyBat.open('w') as dumbat:
        dumbat.write('cd /d c:\\cepel\\anafas 6.5\n\nSTART anafas.exe -WIN ' + 
            '"' + str(dummyInp) + '"')

    shell = win32com.client.Dispatch("WScript.Shell")
    shell.Run("dummy.bat")
    while not shell.AppActivate("Anafas"): pass
    win32api.Sleep(500)
    shell.SendKeys("s")

    # print(subprocess.call(['cmd', '/c', 'dummy.bat']))
    subprocess.call('rm dum* DUM*')


def make_Rela(relaBuffer, arqPaths):
    
    if 'Ana' in relaBuffer[0]:
        rela = arqPaths['Rela'].open('w')
        
        if not relaBuffer[1]:
            rela.write(ajuda.texto('relaErroArq').format(arqPaths['Ana'].name, Path.cwd()/arqPaths['Ana']))
        else: rela.write(ajuda.texto('relaArq').format(arqPaths['Ana'].name))
    else: rela = arqPaths['Rela'].open('a') 

    if 'rncc' in relaBuffer[0]:
        rela.write(ajuda.texto('relaRncc').format(arqPaths['Rncc']))

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
        rela.write(ajuda.texto('relaSrc').format(arqPaths['Src']))

    if 'equi' in relaBuffer[0]:
        fontes = set()
        for barra in barrasrelaBuffer[2]:
            fontes.add(relaBuffer[1].get_nomeGerAtp(barra))
        rela.write(ajuda.texto('relaEqui').format(Path.cwd()/arqPaths['Lib'], len(barrasrelaBuffer[2]), len(fontes)-1))
        rela.write('{:^6}{:^15}{:^10}{:^10}\n'.format(*ajuda.texto('cabecalhoF', query='list')))
        for barra in barrasrelaBuffer[2]:
            rela.write('{:^6d}{:^15}{:^11}{:^11}\n'.format(barra, relaBuffer[1].get_nomeAna(barra), relaBuffer[1].get_nomeAtp(barra), relaBuffer[1].get_nomeGerAtp(barra)))
        






class relaWatcher():
    def __init__(self, make_Rela, arqPaths):
        self._relaBuffer = ('',1)
        self.make_Rela = make_Rela
        self.arqPaths = arqPaths
    @property
    def relaBuffer(self): return self._relaBuffer

    @relaBuffer.setter
    def relaBuffer(self, value):
        self._relaBuffer = value
        self.make_Rela(self._relaBuffer, self.arqPaths)
        self._relaBuffer = 0




def main():

    arqPaths = {'Lib' : Path('equivalente.lib'),
                'Rela' : Path('relatorio.OUT'),
                'Ana' : Path('equi.ana'),
                'Atp' : Path('nomesatp.txt'),
                'Src' : Path('sources.lib'),
                'Rncc' : Path('rncc.rel')}



    argumnt = args_Handler()
    arqPaths = argumnt.check_Paths(arqPaths)
    comando = argumnt.args.c

    runTime = 1
        
    relaWatch = relaWatcher(make_Rela, arqPaths)


    try:
        dbar = get_DBAR(arqPaths['Ana'].open('r'), Nodes())
        equiv = get_EQUIV(arqPaths['Ana'].open('r'), Branches(), dbar)
        relaWatch.relaBuffer = ('Ana',1)
    except(FileNotFoundError):
        runTime = 0
        relaWatch.relaBuffer = ('Ana',0)


    if runTime:
        if 'R' in comando:
            make_Rncc(arqPaths['Ana'], arqPaths['Rncc'], dbar, equiv)
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
                    runTime = 0
            except(FileNotFoundError): 
                relaWatch.relaBuffer = ('atp', 0)
                runTime = 0

    if runTime:
        if 's' in comando:
            make_Source(arqPaths['Src'], dbar)
            relaWatch.relaBuffer = ('src',)

        if 'e' in comando:
            make_Equi(arqPaths['Lib'], equiv, dbar)
            relaWatch.relaBuffer = ('equi', dbar, equiv)

    print(ajuda.texto('fim').format(arqPaths['Rela']))



main()