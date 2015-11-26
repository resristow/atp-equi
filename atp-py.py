import ajuda
from datetime import datetime
import numpy as np
import re
from tkinter import *
from tkinter import filedialog
import textwrap

start_time = datetime.now()
S_BASE_ANA = 100 # MVA


# FUNÇÕES ---------------------------------------------------------------------#

def space_replacer(t): #
    t = t.replace(" ", "") #Exclui os espaços que acompanham o valor numérico.
    return t
# -----------------------------------------------------------------------------#        

def space_replacer_int(s): # Para números inteiro
    s = int(s.replace(" ", "")) #Exclui os espaços que acompanham o valor numérico.
    return s
# -----------------------------------------------------------------------------#    

def space_replacer_float(z): # Para números decimais
    z = float(z.replace(" ", "")) #Exclui os espaços que acompanham o valor numérico.
    return z
# -----------------------------------------------------------------------------#

def space_to_zero(u):
    if "     " in u:
        u = "0"
    return u
# -----------------------------------------------------------------------------#

def percent_to_pu(x):
    if "     " in x:
        x = "0" # Substitui por zero caso não tenha valor numérico
    x = x.replace(" ", "") # Exclui os espaços que acompanham o valor numérico
    if x != '999999':
        if "." not in x: # Filtro de ponto
            x = float(x)/10000 # Calcula PU caso não tenha ponto
        else:
            x = float(x)/100 # Calcula PU caso tenha ponto
    else:
        x = '9999'  
    return str(x) 
# -----------------------------------------------------------------------------#    

def pu_to_ohm(y):
    y = float(y)
    x = float(line[8])*float(line[8])/(S_BASE_ANA)*y # Cálculo em OHM
    if x > 9999:
        y = '9999.0'
    else:
        y = str(round(x,5)) # Arrendonda para 5 casas decimais
    if x < 0: # Filtro para valor negativo
        y = '0.1000'
    return y
# -----------------------------------------------------------------------------#  

def get_DBAR(arquivo):

    flag = 0
    DBAR = []

    for linha in arquivo:
        if (flag == 3) & ('99999' in linha): 
            flag = 0
            break
        if (flag == 1) and not ('(' in linha[0]):
            flag = flag | 2  
        if flag == 3: DBAR.append(linha[0:35])
        if 'DBAR' in linha[0:4]: flag = flag | 1

    bn, vbas = {},{}
    for linha in DBAR:
        nb = int(linha[0:5])
        bn[nb] = linha[9:21].strip()
        vbas[nb] =float(linha[31:35])
    bn[0] = 'TERRA'
    vbas[0] = 0
    return [bn,vbas]

def get_EQUIV(arquivo):
    flag = 0
    BF, BT, T, R1, X1, R0, X0 = [[] for n in range(7)]
    for linha in arquivo:
        if '998' in linha[65:75]:
            BF.append(int(linha[0:5]))
            BT.append(int(linha[7:12]))
            T.append(linha[16])
            try:
                if '.' in linha[17:23]: R1.append(float(linha[17:23])/100)
                else: R1.append(float(linha[17:23])) 
            except(ValueError):R1.append(0)
            try:
                if '.' in linha[23:29]: X1.append(float(linha[23:29])/100)
                else: X1.append(float(linha[23:29]))
            except(ValueError): X1.append(0)
            try:
                if '.' in linha[29:35]: R0.append(float(linha[29:35])/100)
                else: R0.append(float(linha[29:35]))
            except(ValueError): R0.append(0)
            try:
                if '.' in linha[35:41]: X0.append(float(linha[35:41])/100)
                else: X0.append(float(linha[35:41]))
            except(ValueError): X0.append(0)
            flag = 1
        if (flag == 1) and ('99999' in linha[0:6]): break
    return [BF, BT, T, R1, X1, R0, X0]

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


# LEITURA DO ARQUIVO ORIGINAL -------------------------------------------------#



ajuda.texto('welcome')
ajuda.texto('queryArq')
ANA = input()
while ANA != '':
    ajuda.texto('queryArq')
    ANA = input()
else:
    root_ANA = Tk()
    root_ANA.withdraw()
    file_ANA = open(filedialog.askopenfilename(),'r')
    root_ANA.destroy()

    
# LISTA DE BARRAS --------------------------------------------------#

    dbarLista = get_DBAR(file_ANA)

    
# LISTA DE EQUIVALENTES -------------------------------------------------------#
    
    equivLista = get_EQUIV(file_ANA)

    valsOhm = percentOhm(equivLista, dbarLista[1])
    
# IMPRESSAO DE BARRAS QUE POSSUEM EQUIVALENTES
    
    barrasEquiv = set()

    for n in range(2):
        for barra in equivLista[n]: barrasEquiv.add(barra)
    barrasEquiv = sorted(barrasEquiv)

    
    print('{0:>6s} {1:<11s} {2:>6s}'.format(*ajuda.texto('cabecalho', query='list')))
    for barra in barrasEquiv:
        print('{0:>6d} {1:<12s} {2!s:>6}'.format(barra, dbarLista[0][barra], dbarLista[1][barra]))
    print(' ')
    print(ajuda.texto('barrasTot', query='string'), len(barrasEquiv))

# INSERÇÃO DA LISTA DE NOMES PARA ATP PELO USUÁRIO ------------------------#

    ajuda.texto('ATPinput')
    ajuda.texto('queryArq')
    TXT = input()
    while TXT != '':
        ajuda.texto('queryArq')
        TXT = input()
    else:
        root_TXT = Tk()
        root_TXT.withdraw()
        file_TXT = open(filedialog.askopenfilename(),'r')
        root_TXT.destroy()

        barrasATP = {0:'      '}
        cont = 1
        for barra in file_TXT:
            barrasATP[barrasEquiv[cont]] = barra.strip()
            cont += 1

        print(ajuda.texto('barrasTot', query='string') , len(barrasATP))
        if len(barrasATP) != len(barrasEquiv):
            ajuda.texto('diff')
        else:
            ajuda.texto('igual')
        ajuda.texto('queryLib')
        CONTINUAR = input()
        while CONTINUAR != '1':
            CONTINUAR = input()


    #composição de nome auxiliares para geração no ATP

    gerATP = {}

    for barra in range(len(equivLista[0])):
        if (equivLista[1][barra] == 0) and (equivLista[3][barra] != 999999):
            gerATP[barra] = 'F' + barrasATP[equivLista[0][barra]][:-1]
    print(gerATP)
    if set(gerATP.values()) != len(gerATP): print('REPETECO')


    file_EQUI = open('equivalente.lib','w')
    file_EQUI.write('/BRANCH')



    for linha in range(len(equivLista[0])):
        file_EQUI.write('51' + barrasATP[equivLista[0][linha]] + 'A' + barrasATP[equivLista[1][linha]] + 'A' + 12*' ' \
            + '{0:<6s}'.format(valsOhm[2][linha]) + 6*' ' + '{0:<6s}'.format(valsOhm[3][linha]) + '\n')
        file_EQUI.write('52' + barrasATP[equivLista[0][linha]] + 'B' + barrasATP[equivLista[1][linha]] + 'B' + 12*' ' \
            + '{0:<6s}'.format(valsOhm[0][linha]) + 6*' ' + '{0:<6s}'.format(valsOhm[1][linha]) + '\n')
        file_EQUI.write('53' + barrasATP[equivLista[0][linha]] + 'C' + barrasATP[equivLista[1][linha]] + 'C\n')


        
    
# NC --------------------------------------------------------------------------#
    NC = []
    for line in data_equiv:
        if "T" in line[2]:
            item = "NT"
        else:
            if "999999" in line[3]:
                item = "NH"
            elif line[1] != "0":
                item = "N"
            else:
                item = "NG"
        NC.append(item)        
    #print(NC)    
    
# UNIÃO DA LISTA NC COM A LISTA DE EQUIVALENTES -------------------------------#
    
    for line in data_equiv:
        line.append(NC[data_equiv.index(line)])
    #print(data_equiv) 
    
# ORGANIZAÇÃO DA LISTA DE TENSÕES DAS BARRAS (BF) -----------------------------#
    
    VBAS_BF = []
    for e_line in data_equiv:
        for b_line in DBAR_LISTA:
            if e_line[0] == b_line[0]:
                VBAS_BF.append(b_line[2])
    #print(VBAS_BF)
    
# UNIÃO DA LISTA ORGANIZADA DE TENSÕES (BF) COM A LISTA DE EQUIVALENTES -------#
    
    for line in data_equiv:
        line.append(VBAS_BF[data_equiv.index(line)])
    #print(data_equiv)
    
# ORGANIZAÇÃO DA LISTA DE TENSÕES DAS BARRAS (BT) -----------------------------#
    
    VBAS_BT = []
    for e_line in data_equiv:
        for b_line in DBAR_LISTA:
            if e_line[1] == b_line[0]:
                VBAS_BT.append(b_line[2])
    #print(VBAS_BT)
    
# UNIÃO DA LISTA ORGANIZADA DE TENSÕES (BT) COM A LISTA DE EQUIVALENTES -------#
    
    for line in data_equiv:
        line.append(VBAS_BT[data_equiv.index(line)])
    #print(data_equiv)
    
# ORGANIZAÇÃO DA LISTA DE NOMES PARA ATP DAS BARRAS DE SAÍDA PARA UNIR COM A LISTA DE EQUIVALENTES #
    
    ATP_CODE_LIST_DE = []
    for e_line in data_equiv:
        for d_line in DBAR_LISTA:
            if e_line[0] == d_line[0]:
                ATP_CODE_LIST_DE.append(d_line[3])
    #print(ATP_CODE_LIST_DE)
    
# UNIÃO DA LISTA ORGANIZADA DE BARRAS DE SAÍDA DE NOMES PARA ATP COM A LISTA DE EQUIVALENTES #
    
    for line in data_equiv:
        line.append(ATP_CODE_LIST_DE[data_equiv.index(line)])
    # print(data_equiv)
    
# ORGANIZAÇÃO DA LISTA DE NOMES PARA ATP DAS BARRAS DE ENTRADA PARA UNIR COM A LISTA DE EQUIVALENTES #
    
    ATP_CODE_LIST_PARA = []
    for e_line in data_equiv:
        for d_line in DBAR_LISTA:
            if e_line[1] == d_line[0]:
                ATP_CODE_LIST_PARA.append(d_line[3])
    # print(ATP_CODE_LIST_PARA)
    
# UNIÃO DA LISTA ORGANIZADA DE BARRAS DE ENTRADA DE NOMES PARA ATP COM A LISTA DE EQUIVALENTES #
    
    for line in data_equiv:
        line.append(ATP_CODE_LIST_PARA[data_equiv.index(line)])
    # print(data_equiv)
    
# GERAÇÃO DA LISTA DE CÓDIGOS NECESSÁRIOS PARA ATP ----------------------------#
    
    TIE = []
    for line in data_equiv:
        if line[7] == "N":
            item = "TIE   "
        else:
            if "NG" in line[7]:
                item = "TIEGER"
            else:      
                if "NT" in line[7]:
                    item = "TIETFO"
                else:
                    if "NH" in line[7]:
                        item = "TIETRR"
        TIE.append(item)      
    # print(TIE)
    
# UNIÃO DA LISTA ORGANIZADA DE CÓDIGOS NECESSÁRIOS PARA ATP COM A LISTA DE EQUIVALENTES #
    
    for line in data_equiv:
        line.append(TIE[data_equiv.index(line)])
    
    ATP_FINAL_NAME = []
    for line in data_equiv:
        if line[12] == "TIEGER":
            nome = line[10]
            item = "F" + nome[0:4]
        else:
            if "TIETRR" in line[12]:
                item = "     "
            else:
                if "TIETFO" in line[12]:
                    nome1 = line[11]
                    nome_de = nome1[3:5]
                    nome2 = line[10]
                    nome_para = nome2[3:5]
                    item = nome1[0] + nome_de[0] + line[2] + nome2[0] + nome_para[0]
                else:
                    if "TIE   " in line[12]:
                        item = line[11]
        ATP_FINAL_NAME.append(item)
    # print(ATP_FINAL_NAME)
    
    for line in data_equiv:
        line.append(ATP_FINAL_NAME[data_equiv.index(line)])
    # print(data_equiv)
    
    
# GERAÇÃO DOS DADOS EXTRA PARA ATP E UNIÃO COM A LISTA DE EQUIVALENTES --------#
    
    ATP_EXTRA_1 = []
    for line in data_equiv:
        if "TIETFO" in line[12]:
            item = line[11]
        else:
            item = ""
        ATP_EXTRA_1.append(item)
    # print(ATP_EXTRA_1)
    
    for line in data_equiv:
        line.append(ATP_EXTRA_1[data_equiv.index(line)])
    # print(data_equiv)
    
    ATP_EXTRA_2 = []
    for line in data_equiv:
        if "TIETFO" in line[12]:
            item = line[8]
    #         item = 
        else:
            item = ""
        ATP_EXTRA_2.append(item)
    # print(ATP_EXTRA_2)
        
    for line in data_equiv:
        line.append(ATP_EXTRA_2[data_equiv.index(line)])
    # print(data_equiv)
    
    ATP_EXTRA_3 = []
    for line in data_equiv:
        if "TIETFO" in line[12]:
            item = line[9]
        else:
            item = ""
        ATP_EXTRA_3.append(item)
    # print(ATP_EXTRA_3)
    
    for line in data_equiv:
        line.append(ATP_EXTRA_3[data_equiv.index(line)])
    
# -----------------------------------------------------------------------------#
    
    
    # print(data_equiv[0])
    # print(data_equiv[1])
    # print(data_equiv[2])
    # print(data_equiv[3])
    # print(data_equiv[4])
    # print(data_equiv[5])
    # print(" ")
    
# TRANSFORMAÇÃO DE IMPEDANCIAS PARA PU -------------------------==-------------#
    
    for line in data_equiv:
        line[3] = percent_to_pu(line[3])
        line[4] = percent_to_pu(line[4])
        line[5] = percent_to_pu(line[5])
        line[6] = percent_to_pu(line[6])
        
    # print(data_equiv[0])
    # print(data_equiv[1])
    # print(data_equiv[2])
    # print(data_equiv[3])
    # print(data_equiv[4])
    # print(data_equiv[5])
    # print(" ")
    
# TRANSFORMAÇÃO DE IMPEDANCIAS EM PU PARA OHM E FILTRO DE NEGATIVO ------------#
    
    for line in data_equiv:
        line[3] = pu_to_ohm(line[3])
        line[4] = pu_to_ohm(line[4])
        line[5] = pu_to_ohm(line[5])
        line[6] = pu_to_ohm(line[6])
    
#     print(data_equiv[0])
#     print(data_equiv[1])
#     print(data_equiv[2])
#     print(data_equiv[3])
#     print(data_equiv[4])
#     print(data_equiv[5])
    

# GERAÇÃO DO ARQUIVO DE SAÍDA EM FORMATO PADRÃO ATP ---------------------------#


    with open('C:\EQUIVALENTE-DADOS.lib', 'w') as data_lib:
        for line in data_equiv:
            data_lib.writelines(line[12] + " " + line[13] + " " + line[10] + " " + line[5] + " " + line[6] + " " + line[3] + " " + line[4] + " "+ line[14] + " " +line[16] + " " + line[15] + "\n")


print('\n' + 'ARQUIVO "EQUIVALENTE-DADOS.lib" SALVO EM "C:"'+ '\n')

# SELEÇÃO DE BARRAS "TIETFO"  -------------------------------------------------#

TESTE_TRAFO = []
for line in data_equiv:
    if "TIETFO" in line[12]: #Identifica as linhas com o código "TIETFO".
        TESTE_TRAFO.append(line[13]) #Adiciona os códigos à lista "TESTE_TRAFO".
#print(TESTE_TRAFO)

# SELEÇÃO DE BARRAS "TIETFO" COM CÓDIGOS REPETIDOS ----------------------------#

REPETIDOS = []
for item in TESTE_TRAFO:
    if TESTE_TRAFO.count(item) > 1: #Identifica os códigos repetidos.
        REPETIDOS.append(item) #Adiciona os códigos à lista "REPETIDOS".
#print(REPETIDOS)

# AVISO DE BARRAS "TIETFO" COM CÓDIGOS REPETIDOS ------------------------------#

if len(REPETIDOS) != 0:
    SET_REPETIDOS = set(REPETIDOS) #Cria uma nova lista sem o códigos repetidos
    #print(SET_REPETIDOS)
    for item in SET_REPETIDOS:
        print('O CÓDIGO "' + item + '" ESTÁ REPETIDO!',
              ' ',
              'EDITE O ARQUIVO EQUIVALENTE-DADOS.lib SALVO EM C: ANTES DE UTILIZAR OS DADOS',
              ' ', sep='\n', end='\n')
        print(' ','CONFIRA ANTES DE UTILIZAR OS DADOS', sep='\n', end='\n')
else:
    print('NÃO HÁ CÓDIGOS DE TRANSFORMADORES REPETIDOS.')

print(' ','PRESSIONE "ENTER" PARA CONTINUAR.', sep='\n', end='\n')
ANA = input()
while ANA != '':
    print('PRESSIONE "ENTER" PARA CONTINUAR.')
    ANA = input()
else:
    with open('C:\EQUIVALENTE-DADOS.lib', 'r') as data_lib:
        data_lib_lines = data_lib.readlines()
#         print(data_lib_lines)
        with open('C:\EQUIVALENTE-BRANCH.lib', 'w') as data_lib_new:    
            data_lib_new.writelines('/BRANCH' + '\n')
            data_lib_new.writelines('C < n1 >< n2 ><ref1><ref2>< R  >< L  >< C  >' + '\n')
            data_lib_new.writelines('C < n1 >< n2 ><ref1><ref2>< R  >< A  >< B  ><Leng><><>0' + '\n')
            data_lib_new.writelines('C        1         2         3         4         5         6         7         8' + '\n')
            data_lib_new.writelines('C 345678901234567890123456789012345678901234567890123456789012345678901234567890' + '\n')
            for line in data_lib_lines:
                data_lib_new.writelines('C ******************************************************************************' + '\n')
                data_lib_new.writelines('C EQUIV: ' + line)
    # C < n1 >< n2 ><ref1><ref2>< R  >< L  >< C  >
    # C < n1 >< n2 ><ref1><ref2>< R  >< A  >< B  ><Leng><><>0
    # C        1         2         3         4         5         6         7         8
    # C 345678901234567890123456789012345678901234567890123456789012345678901234567890
    # 51TERMIATERMFA            RESIS0      REACT0                                    
    # 52TERMIBTERMFB            RESIS1      REACT1                                    
    # 53TERMICTERMFC
                lib_line = line.strip()
#                 print(lib_line)
                lib_line = lib_line.split(' ')
#                 print(lib_line)
    #             for item in lib_line:
                while '' in lib_line:
                    lib_line.remove('')
#                print(lib_line)
                if lib_line[0] == "TIE":
                    TERMI = lib_line[1]
                    TERMF = lib_line[2]
                    RESIS0 = lib_line[3]
                    REACT0 = lib_line[4]
                    RESIS1 = lib_line[5]
                    REACT1 = lib_line[6]
                    data_lib_new.writelines('C ------------------------------------------------------------------------------' + '\n')
#                     data_lib_new.writelines('C        1         2         3         4         5         6         7         8' + '\n')
#                     data_lib_new.writelines('C 345678901234567890123456789012345678901234567890123456789012345678901234567890' + '\n')
                    data_lib_new.writelines('51'+TERMI[0:5]+'A'+TERMF[0:5]+'A            '+RESIS0[0:6]+'      '+REACT0[0:6]+' ' + '\n')
                    data_lib_new.writelines('52'+TERMI[0:5]+'B'+TERMF[0:5]+'B            '+RESIS1[0:6]+'      '+REACT1[0:6]+' ' + '\n')
                    data_lib_new.writelines('53'+TERMI[0:5]+'C'+TERMF[0:5]+'C' + '\n')
                elif lib_line[0] == "TIEGER":
                    TERMIG = lib_line[1]
                    TERMFG = lib_line[2]
                    RESIS0G = lib_line[3]
                    REACT0G = lib_line[4]
                    RESIS1G = lib_line[5]
                    REACT1G = lib_line[6]
                    data_lib_new.writelines('C ------------------------------------------------------------------------------' + '\n')
#                   data_lib_new.writelines('C        1         2         3         4         5         6         7         8' + '\n')
#                   data_lib_new.writelines('C 345678901234567890123456789012345678901234567890123456789012345678901234567890' + '\n')
                    data_lib_new.writelines('51'+TERMIG[0:5]+'A'+TERMFG[0:5]+'A            '+RESIS0G[0:6]+'      '+REACT0G[0:6]+' ' + '\n')
                    data_lib_new.writelines('52'+TERMIG[0:5]+'B'+TERMFG[0:5]+'B            '+RESIS1G[0:6]+'      '+REACT1G[0:6]+' ' + '\n')
                    data_lib_new.writelines('53'+TERMIG[0:5]+'C'+TERMFG[0:5]+'C' + '\n')
    #             print(data_lib_new)
    # # C 345678901234567890123456789012345678901234567890123456789012345678901234567890
    # # 51TERMIA                  RESIS0      REACT0                                    
    # # 52TERMIB                  RESIS1      REACT1                                    
    # # 53TERMIC   
                elif lib_line[0] == "TIETRR":
                    TERMIT = lib_line[1]
                    RESIS0T = lib_line[2]
                    REACT0T = lib_line[3]
                    RESIS1T = lib_line[4]
                    REACT1T = lib_line[5]
                    data_lib_new.writelines('C ------------------------------------------------------------------------------' + '\n')
#                   data_lib_new.writelines('C        1         2         3         4         5         6         7         8' + '\n')
#                   data_lib_new.writelines('C 345678901234567890123456789012345678901234567890123456789012345678901234567890' + '\n')
                    data_lib_new.writelines('51'+TERMIT[0:5]+'A                  '+RESIS0T[0:6]+'      '+REACT0T[0:6]+' ' + '\n')
                    data_lib_new.writelines('52'+TERMIT[0:5]+'B                  '+RESIS1T[0:6]+'      '+REACT1T[0:6]+' ' + '\n')
                    data_lib_new.writelines('53'+TERMIT[0:5]+'C' + '\n')
    #             print(data_lib_new)
    # # C 345678901234567890123456789012345678901234567890123456789012345678901234567890
    # # 51TERMTATERMFA            RESIS0      REACT0
    # # 52TERMTBTERMFB            RESIS1      REACT1
    # # 53TERMTCTERMFC
    # # C TRAFO IDEAL DE TRANSF. 
    # # C        1         2         3         4         5         6         7         8
    # # C 345678901234567890123456789012345678901234567890123456789012345678901234567890
    # #   TRANSFORMER                         ATERMT  1.E6                             0
    # #             9999
    # #  1TERMIA                   .0001 .0001VTERMI
    # #  2TERMTA                   .0001 .0001VTERMF
    # #   TRANSFORMER ATERMT                  BTERMT                                   0
    # #  1TERMIB
    # #  2TERMTB
    # #   TRANSFORMER ATERMT                  CTERMT                                   0
    # #  1TERMIC
    # #  2TERMTC
    # # C ******************************************************************************
                elif lib_line[0] == "TIETFO":
                    TERMTF = lib_line[1]
                    TERMFF = lib_line[2]
                    RESIS0F = lib_line[3]
                    REACT0F = lib_line[4]
                    RESIS1F = lib_line[5]
                    REACT1F = lib_line[6]
                    TERMIF = lib_line[7]
                    VTERMIF = lib_line[8]
                    VTERMFF = lib_line[9]
                    data_lib_new.writelines('C ------------------------------------------------------------------------------' + '\n')
#                     data_lib_new.writelines('C        1         2         3         4         5         6         7         8' + '\n')
#                     data_lib_new.writelines('C 345678901234567890123456789012345678901234567890123456789012345678901234567890' + '\n')
                    data_lib_new.writelines('51'+TERMTF[0:5]+'A'+TERMFF[0:5]+'A            '+RESIS0F[0:6]+'      '+REACT0F[0:6]+'                                    ' + '\n')
                    data_lib_new.writelines('52'+TERMTF[0:5]+'B'+TERMFF[0:5]+'B            '+RESIS1F[0:6]+'      '+REACT1F[0:6]+'                                     ' + '\n')
                    data_lib_new.writelines('53'+TERMTF[0:5]+'C'+TERMFF[0:5]+'C                                                                  ' + '\n')
                    data_lib_new.writelines('C TRAFO IDEAL DE TRANSF.                                                        ' + '\n')
                    data_lib_new.writelines('C        1         2         3         4         5         6         7         8' + '\n')
                    data_lib_new.writelines('C 345678901234567890123456789012345678901234567890123456789012345678901234567890' + '\n')
                    data_lib_new.writelines('  TRANSFORMER                         A'+TERMTF[0:5]+'  1.E6                             0' + '\n')
                    data_lib_new.writelines('            9999' + '\n')
                    data_lib_new.writelines(' 1'+TERMIF[0:5]+'A                   .0001 .0001'+VTERMIF[0:6]+ '\n')
                    data_lib_new.writelines(' 2'+TERMTF[0:5]+'A                   .0001 .0001'+VTERMFF[0:6]+ '\n')
                    data_lib_new.writelines('  TRANSFORMER A'+TERMTF[0:5]+'                  B'+TERMTF[0:5]+'                                   0' + '\n')
                    data_lib_new.writelines(' 1'+TERMIF[0:5]+'B' + '\n')
                    data_lib_new.writelines(' 2'+TERMTF[0:5]+'B' + '\n')
                    data_lib_new.writelines('  TRANSFORMER A'+TERMTF[0:5]+'                  C'+TERMTF[0:5]+'                                   0' + '\n')
                    data_lib_new.writelines(' 1'+TERMIF[0:5]+'C' + '\n')
                    data_lib_new.writelines(' 2'+TERMTF[0:5]+'C' + '\n')
            data_lib_new.writelines('C ******************************************************************************' + '\n')


print('ARQUIVO "EQUIVALENTE-BRANCH.lib" SALVO EM "C:"'+ '\n')

end_time = datetime.now()
print('Duração: {}'.format(end_time - start_time), sep='\n', end='\n')

print('PRESSIONE "ENTER" PARA SAIR.', sep='\n', end='\n')
SAIR = input()
while SAIR != '':
    print('PRESSIONE "ENTER" PARA SAIR.', sep='\n', end='\n')
    SAIR = input()
else:
    quit