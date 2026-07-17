import os
import glob
import re
import pandas as pd

# Busca todos os arquivos Excel na pasta de brutos
arquivos = glob.glob('dados_brutos/*.xlsx')
lista_tabelas = []

for arquivo in arquivos:
    try:
        # Lê apenas as primeiras linhas para pegar o cabeçalho
        df_cabecalho = pd.read_excel(arquivo, header=None, nrows=5)
        linha2 = str(df_cabecalho.iloc[1, 0])  # RELATÓRIO DO CLIENTE (002-DIESEL)
        linha3 = str(df_cabecalho.iloc[2, 0])  # Empresa: TRANS PIZZATTO...

        # Extrai o produto (o que está entre parênteses)
        match_produto = re.search(r'\((.*?)\)', linha2)
        produto = match_produto.group(1) if match_produto else "Sem_Produto"

        # Extrai a empresa (o que está depois dos dois pontos)
        empresa = linha3.split(':')[-1].strip() if ':' in linha3 else "Sem_Empresa"

        # Lê os dados de verdade pulando as 5 primeiras linhas
        df_dados = pd.read_excel(arquivo, skiprows=5)

        # Adiciona as colunas identificadoras
        df_dados['Empresa'] = empresa
        df_dados['Produto'] = produto

        lista_tabelas.append(df_dados)
        
        # DELETA o Excel bruto para não deixar dados expostos no repositório público
        os.remove(arquivo)
        
    except Exception as e:
        print(f"Erro ao processar o arquivo {arquivo}: {e}")

# Consolida tudo no arquivo final se houver dados novos
if lista_tabelas:
    # Se o arquivo final já existir, lê ele antes para não perder o histórico do passado
    arquivo_final = 'dados_processados/vendas_consolidadas.csv'
    if os.path.exists(arquivo_final):
        df_antigo = pd.read_csv(arquivo_final)
        lista_tabelas.insert(0, df_antigo)
        
    tabela_final = pd.concat(lista_tabelas, ignore_index=True)
    # Remove linhas duplicadas caso o mesmo arquivo seja enviado duas vezes por erro
    tabela_final.drop_duplicates(inplace=True)
    
    tabela_final.to_csv(arquivo_final, index=False, encoding='utf-8-sig')
    print("Sucesso! Base consolidada atualizada.")
else:
    print("Nenhum arquivo novo para processar.")
