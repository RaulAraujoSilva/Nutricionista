# Avaliador Nutricional

Sistema de avaliação nutricional que utiliza IA para analisar refeições e fornecer recomendações personalizadas.

## Requisitos

- Python 3.12+
- Docker (opcional)
- Chave de API da OpenAI

## Configuração

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_DIRETORIO]
```

2. Crie um arquivo `.env` na raiz do projeto:
```bash
OPENAI_API_KEY=sua_chave_aqui
```

## Execução Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a aplicação:
```bash
streamlit run app.py
```

## Deploy com Docker

1. Construa a imagem:
```bash
docker build -t avaliador-nutricional .
```

2. Execute o container:
```bash
docker run -d -p 8501:8501 --env-file .env avaliador-nutricional
```

A aplicação estará disponível em `http://localhost:8501`

## Deploy em Produção

### Heroku

1. Instale o Heroku CLI
2. Login no Heroku:
```bash
heroku login
```

3. Crie uma nova aplicação:
```bash
heroku create nome-da-sua-app
```

4. Configure a variável de ambiente:
```bash
heroku config:set OPENAI_API_KEY=sua_chave_aqui
```

5. Deploy:
```bash
git push heroku main
```

### Google Cloud Run

1. Instale o Google Cloud SDK
2. Configure o projeto:
```bash
gcloud config set project seu-projeto
```

3. Construa e publique a imagem:
```bash
gcloud builds submit --tag gcr.io/seu-projeto/avaliador-nutricional
```

4. Deploy no Cloud Run:
```bash
gcloud run deploy avaliador-nutricional \
  --image gcr.io/seu-projeto/avaliador-nutricional \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=sua_chave_aqui"
```

## Estrutura do Projeto

```
.
├── app.py              # Aplicação Streamlit
├── models.py           # Definições de classes e modelos
├── database.py         # Gerenciamento de dados
├── avaliador.py        # Lógica de avaliação nutricional
├── requirements.txt    # Dependências do projeto
├── Dockerfile         # Configuração do Docker
└── README.md          # Este arquivo
```

## Uso

1. Acesse a aplicação através do navegador
2. Digite o nome do alimento na barra de busca
3. Selecione o alimento e a quantidade
4. Adicione observações sobre a refeição
5. Clique em "Avaliar Refeição" para receber a análise

## Manutenção

Para atualizar a aplicação em produção:

1. Faça as alterações necessárias
2. Atualize a versão no `requirements.txt` se necessário
3. Faça commit das alterações
4. Reconstrua e republique a imagem Docker
5. Atualize o deploy

## Suporte

Para suporte, abra uma issue no repositório ou entre em contato com a equipe de desenvolvimento. 