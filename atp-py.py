import ajuda
import textwrap
from pathlib import Path
import argparse


parser = argparse.ArgumentParser(description='Cria um equivalente para o ATP', 
                prog='ATP-EQUI')
parser.add_argument('-c','--comando', default='equi', metavar='Comando', 
                help='Especifica que operacao deve ser feita')
parser.add_argument('arqAna', default='equi.ana', metavar='.ANA', nargs='?', 
                help='Especifica o nome do arquivo .ANA para leitura')
parser.add_argument('arqAtp', default='nomes atp.txt', metavar='Nomes ATP', 
                nargs='?', help='Especifica o nome do arquivo com os nomes de barras do ATP')
parser.add_argument('--rela', default='RELATORIO_SAIDA.txt', 
                metavar='arquivo', help='Especifica o nome do arquivo de relatório de saída')
parser.add_argument('--lib', default='equivalente.lib', metavar='.lib', 
                help='Especifica o nome do arquivo de equivalente .lib que será gerado')

args = parser.parse_args()

arqPaths = {'Lib' : Path(args.lib),
            'Rela' : Path(args.rela),
            'Ana' : Path(args.arqAna),
            'Atp' : Path(args.arqAtp)}


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

def makeEqui(arquivo, equiv, dbar):
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

def emiteRela(arquivo, status, dbar, equiv):
    rela = arquivo.open('w')

    if status['ana'] != 0: barrasEquiv = equiv.get_equiNodes()[1:]

    if status['ana'] == 0:
        rela.write(ajuda.texto('relaErroArq').format('.ANA', Path.cwd()/arqPaths['Ana']))

    elif status['atp'] == 0:
        rela.write(ajuda.texto('relaErroArq').format('com os nomes do ATP', Path.cwd()/arqPaths['Atp']))

    elif status['diff'] > 0:
        rela.write(ajuda.texto('relaErroDiff').format(status['diff']))

    elif args.comando == 'equi':
        
        rela.write(ajuda.texto('relaEqui').format(Path.cwd()/arqPaths['Lib'], len(barrasEquiv)))
        rela.write('{:^6}{:^15}{:^10}{:^10}\n'.format(*ajuda.texto('cabecalhoF', query='list')))
        for barra in barrasEquiv:
            rela.write('{:^6d}{:^15}{:^11}{:^11}\n'.format(barra, dbar.get_nomeAna(barra), dbar.get_nomeAtp(barra), dbar.get_nomeGerAtp(barra)))

    elif args.comando == 'barras':
        barrasEquiv = equiv.get_equiNodes()[1:]
        rela.write(ajuda.texto('relaBarra').format(len(barrasEquiv)))

        rela.write('{0:^6s} {1:<11s} {2:^6s}\n'\
            .format(*ajuda.texto('cabecalho', query='list')))
        for barra in barrasEquiv:
            rela.write('{0:^6d} {1:<12s} {2!s:^6}\n'.format(barra, dbar.get_nomeAna(barra), dbar.get_vBase(barra)))



def main():


    status = {'ana': 1, 'atp': 1, 'diff': 0}
        

    try:
        dbar = get_DBAR(arqPaths['Ana'].open('r'), Nodes())
        equiv = get_EQUIV(arqPaths['Ana'].open('r'), Branches(), dbar)
    except(FileNotFoundError): 
        status['ana'] = 0
        dbar, equiv = 0,0

    if args.comando == 'equi':
        try:
            get_ATP(arqPaths['Atp'].open('r'), dbar, equiv)
            diff = abs(len(arqPaths['Atp'].open('r').readlines()) - len(equiv.get_equiNodes()[1:]))
            if diff > 0: status['diff'] = diff
        except(FileNotFoundError): status['atp'] = 0


    emiteRela(arqPaths['Rela'], status, dbar, equiv)


    makeEqui(arqPaths['Lib'], equiv, dbar)



main()