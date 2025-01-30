import csv
import json
import os

# Função para somar as despesas e transferências por PIX de um determinado mês no arquivo CSV
def somar_despesas_por_mes(caminho_csv):
    despesas_totais = 0.0
    pix_totais = 0.0  # Para armazenar o total de PIX
    try:
        with open(caminho_csv, 'r', encoding='utf-8-sig') as arquivo_csv:
            leitor = csv.reader(arquivo_csv)
            # Pular as três primeiras linhas (caso haja cabeçalho ou linhas iniciais irrelevantes)
            next(leitor)
            next(leitor)
            next(leitor)

            for linha in leitor:
                # Verificar se a linha tem pelo menos 4 colunas (padrão mínimo)
                if len(linha) < 4:
                    print(f"Advertência: Linha ignorada (não tem 4 colunas): {linha}")
                    continue  # Ignorar linhas com número incorreto de colunas

                # Tentar desempacotar as 6 colunas se disponíveis, caso contrário, processar conforme o número de colunas
                try:
                    # Desempacotar até 6 colunas, mas não forçar se não houver todas
                    data, _, valor, _, tipo_transacao, descricao = linha[:6] if len(linha) >= 6 else (linha[0], "", linha[1], "", linha[2], linha[3])

                    # Remover vírgulas do valor para conversão
                    valor = valor.replace(',', '')  

                    # Processar transações de débito
                    if tipo_transacao and tipo_transacao.lower() == 'debito':
                        try:
                            despesas_totais += float(valor)
                        except ValueError:
                            print(f"Advertência: Valor inválido na linha: {linha}")
                            continue  # Ignorar linhas com valor inválido

                    # Verificar se a descrição contém palavras-chave relacionadas a PIX
                    elif tipo_transacao and 'pix' in descricao.lower():  # Se for uma transação PIX
                        try:
                            pix_totais += float(valor)
                        except ValueError:
                            print(f"Advertência: Valor inválido na linha: {linha}")
                            continue  # Ignorar linhas com valor inválido

                except ValueError as e:
                    print(f"Erro ao processar a linha: {linha} - Erro: {e}")
                    continue  # Ignorar linhas que não podem ser processadas corretamente

    except UnicodeDecodeError as e:
        print(f"Erro de codificação ao tentar ler o arquivo: {e}")
        return 0.0, 0.0  # Retornar valores 0 para despesas e PIX em caso de erro
    return despesas_totais, pix_totais  # Retorna tanto as despesas quanto as transferências por PIX


# Função para atualizar ou criar o arquivo JSON com as despesas totais do mês
def atualizar_despesas_json(caminho_json, mes, totais):
    dados_despesas = {}

    # Verificar se o arquivo JSON já existe
    if os.path.exists(caminho_json):
        with open(caminho_json, 'r') as arquivo_json:
            dados_despesas = json.load(arquivo_json)

    # Atualizar os dados de despesas e transferências por PIX com os novos totais para o mês
    dados_despesas[mes] = totais

    # Escrever os dados atualizados de volta no arquivo JSON
    with open(caminho_json, 'w') as arquivo_json:
        json.dump(dados_despesas, arquivo_json, indent=4, ensure_ascii=False)


# Programa principal
if __name__ == "__main__":
    # Solicitar o mês ao usuário
    mes_entrada = input("Por favor, insira o mês no formato MM/AAAA: ")

    # Especificar o nome do arquivo CSV
    nome_arquivo_csv = 'Transacoes.csv'

    # Especificar o nome do arquivo JSON
    nome_arquivo_json = 'despesas_mensais.json'

    # Calcular o total das despesas e transferências por PIX para o mês
    total_despesas_mes, total_pix_mes = somar_despesas_por_mes(nome_arquivo_csv)
    
    print(f"Total de despesas para {mes_entrada}: R$ {total_despesas_mes:.2f}")
    print(f"Total de transferências por PIX para {mes_entrada}: R$ {total_pix_mes:.2f}")

    # Atualizar o arquivo JSON com o total de despesas e o total de PIX
    atualizar_despesas_json(nome_arquivo_json, mes_entrada, {"despesas": total_despesas_mes, "pix": total_pix_mes})
    print(f"Arquivo {nome_arquivo_json} atualizado com os totais de despesas e PIX para {mes_entrada}.")
