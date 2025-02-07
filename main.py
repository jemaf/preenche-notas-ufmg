# -*- coding: utf8


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import click
import pandas as pd
import time

URL = 'https://sistemas.ufmg.br/diario/'
NOTAS = URL +\
    'notaTurma/notaAvaliacao/solicitar/solicitarNota.do' +\
    '?acao=lancarAvaliacaoCompleta'
CRONOGRAMA = URL +\
    'planoAula/cronogramaAula/solicitar/solicitarCronogramaAula.do'


def parse_turmas(form):
    turmas = {}
    for option in form.find_elements(By.TAG_NAME, 'option'):
        if 'Selecione' in option.text:
            continue
        turmas[option.text] = option
    return turmas


def pega_turma(turmas):
    while True:
        print()
        escolha_idx = print('Escolha uma turma:')
        escolhas = {}
        for i, turma in enumerate(sorted(turmas)):
            escolhas[str(i)] = turma
            print(i, ':', turma, sep='\t')

        escolha_idx = input()
        if escolha_idx not in escolhas:
            print('Turma inválida!')
        else:
            break

    nome_turma = escolhas[escolha_idx]
    valor_form = turmas[nome_turma]
    return valor_form

def iniciar_selenium(usuario, senha):
    print('Iniciando selenium')
    options = Options()
    driver = webdriver.Remote(
        command_executor='http://selenium-server:4444/wd/hub',
        options=options
    )
    driver.implicitly_wait(10)  # Set implicit wait time to 1 second
    driver.get(URL)

    # Logando
    username = driver.find_element(By.ID, 'j_username')
    password = driver.find_element(By.ID, 'j_password')

    username.send_keys(usuario)
    password.send_keys(senha)
    driver.find_element(By.NAME, 'submit').click()
    
    return driver


@click.group()
def cli():
    pass

@click.command()
@click.option('--usuario', prompt='Digite seu login')
@click.option('--senha', prompt='Digite sua senha', hide_input=True)
@click.argument('arquivo_notas')
def notas(usuario, senha, arquivo_notas):
    # Pouco de programacao defensiva
    print('Lendo o arquivo')
    try:
        # Lendo como string, mais seguro
        df = pd.read_csv(
            arquivo_notas,
            header=0, index_col=None, dtype=str
        )
        df['Matricula'] = pd.to_numeric(df['Matricula'])
        df = df.set_index('Matricula')
        df = df.sort_index()
        df = df.fillna('0')
    except Exception as e:
        print('Arquivo no formato errado.')
        print('Preciso de csv com uma coluna Matricula')
        print('Além de uma coluna por avaliacao estilo minha ufmg AV1,AV2,EE')
        raise e

    # Inicia selenium
    driver = iniciar_selenium(usuario, senha)

    # Form de turmas
    form_turma = driver.find_element(By.NAME, 'turma')
    turmas = parse_turmas(form_turma)
    escolha_turma = pega_turma(turmas)
    escolha_turma.click()

    # Vamos para as notas
    driver.get(NOTAS)

    # Desliga as notificacoes do minha ufmg
    print('Destivando e-mails')
    notificacoes = "//input[@type='checkbox' and @checked='checked']"
    for checkbox in driver.find_elements(By.XPATH,
                                         notificacoes):
        checkbox.click()

    # Pega os nomes das provas
    avaliacoes_header = driver.find_element(By.XPATH,
                                            "//div[@id='notasHead']")
    avaliacoes = []
    for avaliacao in avaliacoes_header.find_elements(By.TAG_NAME, 'a'):
        avaliacoes.append(avaliacao.text)

    print('As avaliacoes sao:')
    for i in range(len(avaliacoes)):
        print(avaliacoes[i])

    # YOLO
    print('Caso as colunas existam no csv, here we go...')
    cells = '//input[@class="nota centralizado widthAval"]'
    cols = set(df.columns)
    idx_aval = 0
    for cell in driver.find_elements(By.XPATH, cells):
        cell.click()
        id_ = cell.get_attribute('id')[1:]
        matricula, _ = map(int, id_.split('_'))
        if avaliacoes[idx_aval] in cols and matricula in df.index:
            nota = df.loc[matricula][avaliacoes[idx_aval]]
            cell.send_keys(nota.replace('.', ','))
        idx_aval = (idx_aval + 1) % len(avaliacoes)

    print('Antes de fechar o script, ', end='')
    print('verifique tudo e salve as notas no browser.')
    print('Depois, digite qq coisa aqui para terminar')
    input()
    try:
        driver.close()
    except Exception:
        pass

@click.command()
@click.option('--usuario', prompt='Digite seu login')
@click.option('--senha', prompt='Digite sua senha', hide_input=True)
@click.option('--clean', is_flag=True, default=True)
@click.argument('arquivo_frequencia')
def cronograma(usuario, senha, clean, arquivo_frequencia):
    print('Lendo o arquivo')
    try:
        df = pd.read_csv(
            arquivo_frequencia,
            header=0, index_col=None, dtype=str
        )
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
        df['Início'] = pd.to_datetime(df['Início'], format='%H:%M').dt.time
        df['Término'] = pd.to_datetime(df['Término'], format='%H:%M').dt.time
        df = df.fillna('0')
        df = df[df['#'].str.strip() != '0']  # Filtra as linhas válidas
    except Exception as e:
        print('Arquivo no formato errado.')
        print('Preciso de csv com as colunas: Data, Início, Término, Qtd, Tipo')
        raise e
    
    # Confirmação para prosseguir
    print(f'O arquivo contém {len(df)} linhas válidas.')
    confirm = input('Deseja continuar? (s/n): ')
    if confirm.lower() != 's':
        print('Operação cancelada.')
        return
    
    # Inicia selenium
    driver = iniciar_selenium(usuario, senha)
    
    # Form de turmas
    form_turma = driver.find_element(By.NAME, 'turma')
    turmas = parse_turmas(form_turma)
    escolha_turma = pega_turma(turmas)
    escolha_turma.click()

    driver.get(CRONOGRAMA)
    
    print("Antes de continuar, exclua TODOS os registros de aula.")
    input("Pressione qualquer tecla para continuar")
        
    # recupera componentes do formulário
    data_field = driver.find_element(By.XPATH, '//*[@id="data"]')
    inicio_field = driver.find_element(By.XPATH, '//*[@id="form_lancar"]/table[5]/tbody/tr[5]/td[1]/input')
    termino_field = driver.find_element(By.XPATH, '//*[@id="form_lancar"]/table[5]/tbody/tr[5]/td[2]/input')
    qtd_field = driver.find_element(By.XPATH, '//*[@id="form_lancar"]/table[5]/tbody/tr[7]/td[1]/input')
    type_field = driver.find_element(By.XPATH, '//*[@id="form_lancar"]/table[5]/tbody/tr[7]/td[2]/select')
    assunto_field = driver.find_element(By.XPATH, '//*[@id="assunto"]')
    btn_include = driver.find_element(By.XPATH, '//*[@id="botaoIncluirAlterar"]/input')
        
    # cadastra cada uma das datas do arquivo no cronograma
    for _, row in df.iterrows():
        data_field.clear()
        data_field.send_keys(row['Data'].strftime('%d/%m/%Y'))
        time.sleep(0.5)
        
        inicio_field.clear()
        inicio_field.send_keys(row['Início'].strftime('%H:%M'))
        time.sleep(0.1)
        
        termino_field.clear()
        termino_field.send_keys(row['Término'].strftime('%H:%M'))
        time.sleep(0.1)
        
        qtd_field.clear()
        qtd_field.send_keys(str(row['Qtd']))
        time.sleep(0.1)
        
        assunto_field.clear()
        assunto_field.send_keys(str(row['Assunto']))
        time.sleep(0.1)
        # Seleciona o tipo de aula
        for option in type_field.find_elements(By.TAG_NAME, 'option'):
            if option.text == row['Tipo']:
                option.click()
                break
        time.sleep(0.1)
        
        btn_include.click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, '//*[@id="aguarde"]'))
        )
        
    print('Antes de fechar o script, ', end='')
    print('verifique tudo e salve as notas no browser.')
    print('Depois, digite qq coisa aqui para terminar')
    input()
    try:
        driver.close()
    except Exception:
        pass

cli.add_command(notas)
cli.add_command(cronograma)

if __name__ == '__main__':
    cli()
