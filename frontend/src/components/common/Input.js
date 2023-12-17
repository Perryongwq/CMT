import React from 'react';

const Input = ({ type, value, onChange, name }) => {
    return (
        <input type={type} value={value} onChange={onChange} name={name} />
    );
};

export default Input;