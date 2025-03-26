const express = require('express');
const cors = require('cors');
const db = require('./db');
const app = express();
const port = 5000;

app.use(express.json());
app.use(cors());

app.post('/products', (req, res) => {
  const { nome_produto, codigo_produto, cod_marca, categoria, preco, qtd_minima, periodo_maximo } = req.body;

  const query = `
    INSERT INTO produto (
      codigo_produto, nome_produto, cod_marca, categoria, preco, qtd_minima, periodo_maximo
    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING codigo_produto
  `;
  const values = [codigo_produto, nome_produto, cod_marca, categoria, preco, qtd_minima, periodo_maximo];

  db.query(query, values)
    .then(result => {
      res.json({ message: 'Produto cadastrado com sucesso!', produtoId: result.rows[0].codigo_produto });
    })
    .catch(err => {
      console.error('Erro ao cadastrar produto:', err);
      res.status(500).json({ error: 'Erro ao cadastrar produto' });
    });
});

app.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
});
