# Preenche notas Minha-UFMG

Script que preenche as notas automagicamente. Precisa de Selenium + GeckoDriver para funcionar.

Como: 1) sou péssimo em manter consistência e 2) às vezes tenho turmas quebradas, com o script preciso apenas criar uma planilha e "importar" no sistema depois.

## Dependências

1. Firefox, deve ter em qualquer distribuição linux. Em outros sistemas instale o Firefox.
1. [selenium](https://selenium-python.readthedocs.io)
1. [gecko-driver](https://github.com/mozilla/geckodriver/)
1. [pandas](https://pandas.pydata.org)
1. [click](https://click.palletsprojects.com)

### Instalando as dependências

```bash
pip install selenium pandas click
```

### Instalando o GeckoDriver no Linux

Execute as linhas abaixo como root. Caso prefira, mude os comandos para instalar em um outro local.

Caso esteja em outro sistema operacional, instale o gecko-driver manualmente.

```bash
LATEST=`wget -O - https://github.com/mozilla/geckodriver/releases/latest 2>&1 | grep "Location:" | grep --only-match -e "v[0-9\.]\+"`
wget "https://github.com/mozilla/geckodriver/releases/download/${LATEST}/geckodriver-${LATEST}-linux64.tar.gz"
tar -x geckodriver -zf geckodriver-${LATEST}-linux64.tar.gz -O > /usr/local/bin/geckodriver
chmod +x /usr/local/bin/geckodriver
```

## Como utilizar

Basta rodar:

```
python main.py -h
```

Para ver as opções. O vídeo abaixo mostra um exemplo de uso.

Sempre mantenha um terminal aberto. O mesmo vai perguntar para você qual é a turma, veja o vídeo abaixo.

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Z7yhH-4r8YI/0.jpg)](https://www.youtube.com/watch?v=Z7yhH-4r8YI)

### Utilizando com Docker

Para facilitar a execução do script, foi criado um ambiente em Docker para rodar o script em qualquer configuração de hardware.
Esse script contém todas as dependências necessárias para rodar o script, incluindo um navegador (Firefox) e seu driver (GeckoDriver).

#### Pré-requisitos

- Docker instalado na máquina.
- VNC client para visualizar o navegador. `sudo apt-get install tigervnc-viewer`. 

#### Passo-a-passo

1. Inicie o servidor do Selenium.

```bash
$ docker-compose up -d selenium-server
```

2. Abra o navegador virtual para visualizar o Selenium em funcionamento. Caso lhe pergunte a senha, a mesma é `secret`.

```bash
$ vncviewer localhost:5900
```

3. Copie o arquivo `notas.csv` para a pasta `csv` do projeto. É do arquivo neste diretório que o script irá ler as notas. **O arquivo deverá se chamar `notas.csv`**.

```bash
$ cp /caminho/para/arquivo.csv ./csv/notas.csv
```

4. Execute o container do script.

```bash
$ docker-compose up preenche-notas
```

## Formato dos Dados

Como entrada, basta passar um csv que contenha um cabeçalho onde as avaliações tem os mesmos códigos do sistema (AV1, ...). Qualquer coluna que não seja `AV#` ou `EE` será ignorada.

**A ideia aqui é que o: excell, google-sheets, \*-office, todos permitem salvar planilhas como csv**

```
Matricula,AV1,AV2,AV3,AV4,EE
```
