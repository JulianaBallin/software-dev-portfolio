# 💼 Inventorize - Sistema de Cadastro de Produtos

Este sistema foi desenvolvido para **treinamento durante a graduação**, com o objetivo de testar a persistência de dados em um banco de dados online (Neon) e integrar o **frontend** e **backend** com **mínimos passos** para facilitar o uso.

### O que o sistema faz:
- **Cadastra produtos** no banco de dados Neon (na nuvem).
- Permite inserir as seguintes informações:
  - Nome do produto
  - Código do produto
  - Marca (opções predefinidas)
  - Categoria (opções predefinidas)
  - Preço
  - Quantidade mínima em estoque
  - Período máximo em estoque

---

## 🌐 O que você precisa para rodar o sistema?

### ✅ Requisitos:
1. **Instalar o Node.js** (Somente o Node.js, sem necessidade de IDEs ou outras dependências):
   - Baixe e instale o [Node.js](https://nodejs.org/).
   
2. **Banco de Dados Neon**:
   - **O sistema já está configurado para se conectar ao Neon**, então não há necessidade de configurar um banco de dados local.
   - **Tudo o que você precisa é rodar o arquivo `.bat` que vai automaticamente conectar ao banco de dados online.**

---

## 🖱️ Como rodar o sistema

### Passo 1: Baixe o projeto
Baixe o repositório diretamente do GitHub ou extraia o arquivo ZIP.

### Passo 2: Instale o Node.js
Baixe e instale a versão mais recente do Node.js [aqui](https://nodejs.org/).

### Passo 3: Inicie o sistema

1. Abra a pasta do projeto e clique duas vezes no arquivo **`iniciar-inventorize.bat`**.
   
2. O arquivo `.bat` vai:
   - Instalar as dependências automaticamente
   - Rodar o **backend** (`server.js`)
   - Iniciar o **frontend** (`npm start`)

3. O sistema será iniciado e abrirá automaticamente no seu navegador padrão.

---

## 🔧 Como o sistema funciona

- O backend usa o **Node.js + Express** para receber as requisições de cadastro de produtos e se conectar ao banco de dados online Neon.
- O frontend, feito em **React**, recebe os dados do formulário e os envia para o backend.
- O banco de dados Neon guarda as informações dos produtos de forma persistente.

---

## 🛠️ Resumo do Processo:

1. O usuário só precisa ter o **Node.js** instalado.
2. Basta **rodar o `.bat`** e o sistema faz todo o resto:
   - Instala dependências
   - Conecta ao banco Neon
   - Inicia o servidor backend
   - Inicia o frontend no navegador

---

## 🚀 Como verificar se está funcionando corretamente

1. Após rodar o `.bat`, abra o navegador.
2. Acesse a página **`localhost:3000`**.
3. Preencha o formulário de cadastro de produto e clique em **Cadastrar**.
4. Verifique se o produto foi adicionado ao banco.
