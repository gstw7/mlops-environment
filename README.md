#estudos #mlops 
# MLOps Env Study

Diagrama de Monitoramento do Airflow
Primeiro, vamos obter uma visão geral de todo o processo. O Apache Airflow tem a capacidade de transmitir métricas usando o protocolo statsd. Normalmente, um servidor statsd receberia essas métricas e as armazenaria em um backend selecionado. No entanto, nosso objetivo é direcionar essas métricas para o Prometheus. Como podemos realizar essa transferência do statsd para o Prometheus? O projeto Prometheus fornece convenientemente um statsd_exporter, que serve como uma ponte entre os dois sistemas. Este statsd_exporter aceita métricas statsd em uma extremidade e as disponibiliza como métricas Prometheus na outra. O servidor Prometheus pode então coletar as métricas oferecidas pelo statsd_exporter. Em resumo, a estrutura do sistema de monitoramento do Airflow pode ser representada da seguinte forma:

<img width="1022" alt="image" src="https://user-images.githubusercontent.com/46574677/236079374-01be27f1-5c8a-410d-bdc0-479a55231b7d.png">

A ilustração apresenta três componentes-chave do Airflow: o Webserver, Scheduler e Worker. A linha sólida que se origina do Webserver, Scheduler e Worker demonstra o fluxo de métricas desses componentes para o statsd_exporter. O statsd_exporter compila as métricas, transforma-as no formato Prometheus e as expõe através de um endpoint Prometheus. O servidor Prometheus periodicamente recupera dados deste endpoint e armazena as métricas em seu banco de dados. Posteriormente, as métricas do Airflow armazenadas no Prometheus podem ser acessadas por meio do painel do Grafana.

estabeleceremos a configuração retratada no diagrama acima. Nossas etapas incluirão:

- Configurar o Airflow para transmitir métricas statsd.
- Empregar o statsd_exporter para converter métricas statsd em métricas Prometheus.
- Implantar o servidor Prometheus para coletar métricas e fornecer acesso ao Grafana.

Ambientes para fins de estudos.

Os seguintes serviços serão executados:

1. MLflow
2. Airflow with Celery Executor
    - user: airflow
    - pass: airflow
3. Vault
    - token: myroot
4. PostgreSQL {Airflow e MLFlow}
5. Redis
6. Adminer
    - Airflow:
        - Server: postgres_airflow
        - User: airflow
        - Pass: airflow
    - MLFLow
        - Server: postgres_mlflow
        - User: mlflow
        - Pass: mlflow

Obs.: Credencias podem ser alteradas no arquivo `docker-compose.yml`

## Criando uma rede Docker chamada "frontend"
Se você precisa criar uma rede Docker chamada "frontend" com o driver "bridge", siga as etapas abaixo:

Abra um terminal ou prompt de comando.

Execute o seguinte comando:
```bash
docker network create frontend --driver bridge
```
Isso criará uma rede chamada "frontend" usando o driver de rede "bridge". Agora você pode usá-la para conectar seus contêineres.

Certifique-se de ter permissões adequadas para executar comandos Docker. Após a execução do comando, a rede "frontend" estará disponível para uso em seus projetos Docker.

## Verificando e substituindo o UID no arquivo .env
Abra um terminal no Ubuntu.

Digite o seguinte comando para verificar o UID do seu usuário:

```bash
id -u
```
Anote o valor retornado.

Navegue até o diretório onde você possui o arquivo .env do seu projeto.

Abra o arquivo .env com um editor de texto.

Localize a variável **AIRFLOW_UID** no arquivo **.env**.

Substitua o valor atual da variável pelo UID anotado no passo 2.

Exemplo:

```makefile
AIRFLOW_UID=18984075
```
Salve o arquivo .env com as alterações.

Agora, ao executar o comando docker-compose up para iniciar os serviços, o valor do **UID** definido no arquivo **.env** será utilizado no contêiner do Airflow.

## Comandos úteis para iniciar os serviços do docker-compose:

1.  `docker-compose up`: Este comando inicia os contêineres definidos no arquivo `docker-compose.yml`. Se os contêineres ainda não foram construídos, eles serão construídos antes de serem iniciados. Você pode usar a opção `-d` para executar os contêineres em segundo plano.
    
2.  `docker-compose down`: Este comando para e remove os contêineres definidos no arquivo `docker-compose.yml`. Isso também remove todas as redes e volumes criados pelo comando `up`. Use a opção `-v` para remover também volumes criados pelos contêineres.
    
3.  `docker-compose ps`: Este comando lista os contêineres em execução definidos no arquivo `docker-compose.yml`.
    
4.  `docker-compose logs`: Este comando exibe as saídas dos logs dos contêineres em execução definidos no arquivo `docker-compose.yml`. Use a opção `-f` para acompanhar a saída dos logs em tempo real.
    
5.  `docker-compose build`: Este comando constrói as imagens dos contêineres definidos no arquivo `docker-compose.yml`. Use a opção `--no-cache` para ignorar o cache do Docker ao construir as imagens.
    
6.  `docker-compose exec`: Este comando executa um comando em um contêiner em execução definido no arquivo `docker-compose.yml`. Use a opção `-T` para desabilitar alocação de terminal.
    
7.  `docker-compose pull`: Este comando puxa as imagens mais recentes dos repositórios de imagens do Docker definidos no arquivo `docker-compose.yml`. Use a opção `--ignore-pull-failures` para continuar puxando outras imagens, mesmo que uma delas falhe.

## Acessando os serviços:
- Airflow: http://127.0.0.1:8080/
- MLFlow: http://127.0.0.1:5000/
- Vault: http://127.0.0.1:8200/
- Flower: http://127.0.0.1:5555
- Adminer: http://127.0.0.1:8081/
- Prometheus: http://127.0.0.1:9090
- Grafana: http://127.0.0.1:3000

## Subir serviços durante inicialização:

`Linux`

- Crie o arquivo `docker-compose-mlops.service` no diretório `/etc/systemd/system/`  com o comando abaixo:

```bash
sudo vim /etc/systemd/system/docker-compose-mlops.service
```

Comando:
```txt
[Unit]
Description=Docker Compose Service MLOps
Requires=docker.service
After=docker.service

[Service]
TimeoutStartSec=0
RemainAfterExit=yes
Type=oneshot
WorkingDirectory={dir_docker_compose}/mlops-env
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=gustavo
Group=gustavo

[Install]
WantedBy=multi-user.target
```

- Recarregue as unidades do Systemd
```bash
systemctl daemon-reload
```

- Habilitando o serviço para iniciar junto do S.O:
```bash
systemctl enable docker-compose-mlops.service
```

`Created by Bruno Vieira, Gustavo Oliveira, Ronald Silva`
