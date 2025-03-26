import React from "react";
import CadastroProduto from "./CadastroProduto.js";
import "./App.css";

const App = () => {
  return (
    <div className="app-container">
      <header className="app-header">
        <img src={'./logoinventorize2.png'}/>
        <div className="user-info">
          <img src={'./profile.png'} className='profile'/>
          <span className="user-name">ANA_MARIA</span>
          <button className="close-button">X</button>
        </div>
      </header>
      <CadastroProduto />
    </div>
  );
};

export default App;
