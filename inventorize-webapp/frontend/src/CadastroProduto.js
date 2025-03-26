import React, { useState } from "react";
import DropdownList from "./DropdownList";
import "./CadastroProduto.css";

const ProductForm = () => {
  const [formData, setFormData] = useState({
    nome_produto: "",
    codigo_produto: "",
    cod_marca: "",
    categoria: "",
    qtd_minima: "",
    preco: "",
    periodo_maximo: "",
  });

  const [errors, setErrors] = useState({});
  const [searchTerm, setSearchTerm] = useState(""); // estado para armazenar o termo de busca
  const [productList, setProductList] = useState([]); // lista de produtos 

  // atualização para as opções com valores numéricos para cod_marca
  const brandOptions = [
    { value: 1, label: "Nestlé" },
    { value: 2, label: "Coca-cola" },
    { value: 3, label: "Unilever" },
    { value: 4, label: "Colgate" },
    { value: 5, label: "Danone" },
    { value: 6, label: "Procter & Gamble" },
    { value: 7, label: "Heinz, Kellogg's" },
    { value: 8, label: "Nescafé" },
    { value: 9, label: "PepsiCo" },
    { value: 10, label: "Sadia" },
    { value: 11, label: "Perdigão" },
  ];

  const categoryOptions = [
    { value: "category1", label: "Açougue" },
    { value: "category2", label: "Padaria" },
    { value: "category3", label: "Hortifruti (Frutas e Verduras)" },
    { value: "category4", label: "Frios e Laticínios" },
    { value: "category5", label: "Peixaria" },
    { value: "category6", label: "Mercearia" },
    { value: "category7", label: "Congelados" },
    { value: "category8", label: "Bebidas" },
    { value: "category9", label: "Perfumaria" },
    { value: "category10", label: "Higiene e Limpeza" },
    { value: "category11", label: "Utilidades Domésticas" },
  ];

  const handleDropdownChange = (name, value) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };  

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    console.log("Dados do Formulário Enviados:", formData);
  
    const validationErrors = validateFields();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
    } else {
      setErrors({});
  
      try {
        const response = await fetch("http://localhost:5000/products", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            nome_produto: formData.nome_produto,  
            codigo_produto: formData.codigo_produto, 
            cod_marca: formData.cod_marca,
            categoria: formData.categoria,
            preco: formData.preco,
            qtd_minima: formData.qtd_minima,
            periodo_maximo: formData.periodo_maximo
          }),
        });
  
        if (!response.ok) {
          const errorData = await response.json();
          alert(`Erro ao cadastrar produto: ${errorData.error}`);
        } else {
          const responseData = await response.json();
          alert(responseData.message);
          setFormData({
            nome_produto: "",
            codigo_produto: "",
            cod_marca: "",
            categoria: "",
            qtd_minima: "",
            preco: "",
            periodo_maximo: "",
          });
        }
      } catch (error) {
        console.error("Erro na requisição:", error);
        alert("Erro ao conectar com o servidor.");
      }
    }
  };
    

  const validateFields = () => {
    const newErrors = {};
    
    if (!formData.nome_produto.trim()) 
      newErrors.nome_produto = "O nome do produto é obrigatório.";
    
    if (!formData.codigo_produto.trim()) 
      newErrors.codigo_produto = "O código do produto é obrigatório.";
    
    if (!formData.cod_marca) 
      newErrors.cod_marca = "A marca é obrigatória.";
    
    if (!formData.categoria) 
      newErrors.categoria = "A categoria é obrigatória.";
    
    if (!formData.qtd_minima.trim() || isNaN(Number(formData.qtd_minima)) || Number(formData.qtd_minima) <= 0 || !Number.isInteger(Number(formData.qtd_minima))) {
      newErrors.qtd_minima = "Quantidade mínima deve ser um número inteiro positivo.";
    }
    
    const precoRegex = /^\d+(\.\d{1,2})?$/;
    if (!formData.preco.trim() || !precoRegex.test(formData.preco) || Number(formData.preco) <= 0) {
      newErrors.preco = "Preço inválido. Utilize um valor numérico maior que zero com até duas casas decimais.";
    }
    
    if (!formData.periodo_maximo.trim() || isNaN(Number(formData.periodo_maximo)) || Number(formData.periodo_maximo) <= 0 || !Number.isInteger(Number(formData.periodo_maximo))) {
      newErrors.periodo_maximo = "Período máximo de permanência deve ser um número inteiro positivo.";
    }
  
    return newErrors;
  };
  
  const filteredProducts = productList.filter((product) =>
    product.nome_produto.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.codigo_produto.includes(searchTerm)
  );

  return (
    <div className="form-container">
      <h2 className="form-title">CADASTRAR PRODUTO</h2>

      <div className="search-container">
        <input
          type="text"
          placeholder="Pesquisar produto por nome ou código"
          value={searchTerm}
          onChange={handleSearchChange}
        />
        <div className="search-results">
          {searchTerm && filteredProducts.length === 0 ? (
            <p>Nenhum produto encontrado.</p>
          ) : (
            filteredProducts.map((product, index) => (
              <div key={index} className="search-result">
                <p>{product.nome_produto} - {product.codigo_produto}</p>
              </div>
            ))
          )}
        </div>
      </div>

      <form className="product-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Nome</label>
            <input
              type="text"
              name="nome_produto"
              placeholder="Digite o nome do produto"
              value={formData.nome_produto}
              onChange={handleChange}
            />
            {errors.nome_produto && <span className="error">{errors.nome_produto}</span>}
          </div>
          <div className="form-group">
            <label>Código do Produto</label>
            <input
              type="text"
              name="codigo_produto"
              placeholder="Digite o código do produto"
              value={formData.codigo_produto}
              onChange={handleChange}
            />
            {errors.codigo_produto && <span className="error">{errors.codigo_produto}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <DropdownList
              options={brandOptions}
              label="Selecionar Marca"
              onChange={(value) => handleDropdownChange("cod_marca", value)} // Mudança aqui para enviar o valor numérico
            />
            <img src={"./botao.png"} className='botaozinho'/>
            {errors.cod_marca && <span className="error">{errors.cod_marca}</span>}
          </div>
          <div className="form-group">
            <DropdownList
              options={categoryOptions}
              label="Selecionar Categoria"
              onChange={(value) => handleDropdownChange("categoria", value)}
            />
            {errors.categoria && <span className="error">{errors.categoria}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Qtde Mínima em Estoque</label>
            <input
              type="number"
              name="qtd_minima"
              placeholder="Digite a quantidade limite"
              value={formData.qtd_minima}
              onChange={handleChange}
            />
            {errors.qtd_minima && <span className="error">{errors.qtd_minima}</span>}
          </div>
          <div className="form-group">
            <label>Preço Revenda</label>
            <input
              type="text"
              name="preco"
              placeholder="Digite o valor de revenda"
              value={formData.preco}
              onChange={handleChange}
            />
            {errors.preco && <span className="error">{errors.preco}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Período Máximo em Estoque</label>
            <input
              type="number"
              name="periodo_maximo"
              placeholder="Digite o período em dias"
              value={formData.periodo_maximo}
              onChange={handleChange}
            />
            {errors.periodo_maximo && <span className="error">{errors.periodo_maximo}</span>}
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-back">
            VOLTAR
          </button>
          <button type="submit" className="btn-submit">
            CADASTRAR
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;
