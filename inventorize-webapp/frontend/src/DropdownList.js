import React from "react";

const DropdownList = ({ options, label, onChange }) => {
  const handleChange = (event) => {
    const selectedValue = event.target.value;
    onChange(selectedValue);
  };

  return (
    <div className="dropdown-list">
      <label>{label}</label>
      <select onChange={handleChange} defaultValue="">
        <option value="" disabled>
          Selecione uma opção
        </option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default DropdownList;
