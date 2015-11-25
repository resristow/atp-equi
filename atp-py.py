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


# LEITURA DO ARQUIVO ORIGINAL -------------------------------------------------#



ajuda.texto('welcome')
ajuda.texto('queryArq')
ANA = input()
while ANA != '':
    ajuda.texto('queryArq')
    ANA = input()
else:
    root_ANA = Tk()
#     ttk.Button(root_ANA, text="Selecione o arquivo.").grid()
    file_ANA = filedialog.askopenfilename()
    print(file_ANA + '\n')
    root_ANA.destroy()
    with open(file_ANA, 'r') as f:
        f_lines = f.readlines()
    
# SELEÇÃO DA LISTA DE BARRAS --------------------------------------------------#
    
    #Lista de linhas que contem DBAR no inicio
    DBAR_inicio = [bar for bar, data in enumerate(f_lines) if 'DBAR' in data[0:4]]
    
    #Lista de linhas que contem 99999 no inicio
    DBAR_final = [bar for bar, data in enumerate(f_lines) if '99999' in data[0:5]] 
    
    # print(DBAR_inicio) 
    # print(DBAR_final) 
    
    for item in DBAR_final:
        if item < DBAR_inicio[0]: # Testa se o primeiro item de DARB_final é maior que DBAR_inicio
            continue # Passa para o próximo item se não obedecer a condição.
        DBAR = f_lines[DBAR_inicio[0]+3:item] # seleciona dados de barras entre DBAR_final e DBAR_inicio sem cabeçalho
        break # Pára a função ao achar uma linha (um item em DBAR_final) com valor maior que DBAR_inicio
    #print(DBAR)
    
    DBAR = [re.sub(line, line[0:35], line) for line in DBAR] #Filtra os primeiros 35 caracteres da lista de barras
    #print(DBAR)


# FILTRO DA LISTA DE BARRAS -------------------------------------------------------#

    DBAR_LISTA = []
    for line in DBAR:
        NB = space_replacer(line[0:5])
        BN = line[9:20]
        VBAS = space_replacer(line[31:35])
        DBAR_LISTA.append([NB, BN, VBAS])
    DBAR_LISTA.append(['0', 'TERRA', '0'])
    # print(DBAR_LISTA)
    
    
# LISTA DE EQUIVALENTES -------------------------------------------------------#
    
    EQUIV = []
    for line in f_lines:
        if "EQUIV." in line:
            EQUIV.append(line)
    # print(EQUIV)
        
    data_equiv = []
    CODE_FOR_EQUIV = []
    for line_equiv in EQUIV:
        # -------------------------------------------------------------------------#
        BF = space_replacer(line_equiv[0:5])
        BT = space_replacer(line_equiv[7:12])
        T = space_replacer(line_equiv[16])
        #Impedâncias --------------------------------------------------------------#
        R1 = space_replacer(space_to_zero(line_equiv[17:23]))
        X1 = space_replacer(space_to_zero(line_equiv[23:29]))
        R0 = space_replacer(space_to_zero(line_equiv[29:35]))
        X0 = space_replacer(space_to_zero(line_equiv[35:41]))
        data_equiv.append([BF , BT , T , R1 , X1 , R0 , X0])
        CODE_FOR_EQUIV.append([BF, BT])
    # print(data_equiv)
    # print(CODE_FOR_EQUIV)
    
# SELEÇÃO DE BF E BT DO EQUIVALENTE EM LINHA UNICA ----------------------------#
    
    CODE_FOR_ATP = []
    for line in CODE_FOR_EQUIV:
        CODE_FOR_ATP.append(line[0])
        CODE_FOR_ATP.append(line[1])
    # print(CODE_FOR_ATP)
    
# FILTRO DAS BARRAS EXISTENTES NO EQUIVALENTE EM FORMATO STRING ---------------#
    
    CODE_LIST = list(set(CODE_FOR_ATP))
    # print(CODE_LIST)
    
# NÚMERO DAS BARRAS EXISTENTES NO EQUIVALENTE EM FORMATO NUMÉRICO -------------#
    
    CODE_LISTA = []
    for item in CODE_LIST:
        CODE_LISTA.append(int(item))
    # print(CODE_LISTA)
    
# NÚMERO DAS BARRAS EXISTENTES NO EQUIVALENTE EM ORDEM CRESCENTE --------------#
    
    CODE_LISTA.sort()
    # print(list(CODE_LISTA))
    
    EQUIV_LISTA = []
    for item in CODE_LISTA:
        for line in DBAR_LISTA:
            if str(item) == line[0]:
                EQUIV_LISTA.append(line)
    # print(EQUIV_LISTA)
    print('{0:>6s} {1:<11s} {2:>6s}'.format(*ajuda.texto('cabecalho', query='list')))
    for line in EQUIV_LISTA:
        print('{0:>6s} {1:<11s} {2:>6s}'.format(*line))
    print(' ')
    print(ajuda.texto('barrasTot', query='string'), len(EQUIV_LISTA))

# INSERÇÃO DA LISTA DE NOMES PARA ATP PELO USUÁRIO ------------------------#
    ajuda.texto('ATPinput')
    ajuda.texto('queryArq')
    TXT = input()
    while TXT != '':
        ajuda.texto('queryArq')
        TXT = input()
    else:
        root_TXT = Tk()
        file_TXT = filedialog.askopenfilename()
        print(file_TXT + '\n')
        root_TXT.destroy()
        with open(file_TXT, 'r') as atp:
            TXT_NAME  = atp.readlines()
        for item in TXT_NAME:
            print(item[0:5])
        print(' ')
        print(ajuda.texto('barrasTot', query='string') , len(TXT_NAME))
        if len(TXT_NAME) != len(EQUIV_LISTA):
            ajuda.texto('diff')
        else:
            ajuda.texto('igual')
        ajuda.texto('queryLib')
        CONTINUAR = input()
        while CONTINUAR != '1' and CONTINUAR != '2':
            print("OPÇÃO INVÁLIDA!")
            CONTINUAR = input()
        else:
            while CONTINUAR == '2': #'2 - INSERIR NOVA LISTA'
                root_TXT = Tk()
                file_TXT = filedialog.askopenfilename()
                print(file_TXT + '\n')
                root_TXT.destroy()
                with open(file_TXT, 'r') as atp:
                    TXT_NAME  = atp.readlines()
                print('ABAIXO ESTÁ A LISTA DE BARRAS QUE VOCÊ INCLUIU:' + '\n')
                for item in TXT_NAME:
                    print(item[0:5])
                print(' ')
                print("TOTAL DE BARRAS CODIFICADAS: " , len(TXT_NAME))
                if len(TXT_NAME) != len(EQUIV_LISTA):
                    print(' ','AS LISTAS CONTÊM QUANTIDADES DIFERENTES!', sep='\n', end='\n')
                else:
                    print(' ','AS LISTAS CONTÊM QUANTIDADES IGUAIS.', sep='\n', end='\n')
                print(' ','CONFIRA SE AMBAS AS LISTAS CORRESPONDEM','ESCOLHA UMAS DAS OPÇÕES ABAIXO:', sep='\n', end='\n')
                print(' ','1 - ACEITAR A LISTA E GERAR ARQUIVO .LIB.', '2 - INSERIR NOVA LISTA.',' ', sep='\n', end='\n')
                CONTINUAR = input()
            else: #'1 - ACEITAR A LISTA E GERAR ARQUIVO .LIB'
                while CONTINUAR != '1':
                    print("OPÇÃO INVÁLIDA!")
                    CONTINUAR = input()
                else:
                    DBAR_NAME = []
                    for line in TXT_NAME:
                        DBAR_NAME.append(space_replacer(line[0:5]))
#    print(DBAR_NAME)
    for line in EQUIV_LISTA:
        line.append(DBAR_NAME[EQUIV_LISTA.index(line)])
    #print(EQUIV_LISTA)
    
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