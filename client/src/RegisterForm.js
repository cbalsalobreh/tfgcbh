import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginForm.css';

function RegisterForm() {
    const [registerUsername, setRegisterUsername] = useState('');
    const [registerPassword, setRegisterPassword] = useState('');
    const [registerEmail, setRegisterEmail] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        // Validar formato de correo electrónico
        if (!validateEmail(registerEmail)) {
            setErrorMessage('Por favor, introduce un correo electrónico válido.');
            return;
        }
        // Validar seguridad de contraseña
        if (!validatePassword(registerPassword)) {
            setErrorMessage('La contraseña debe tener al menos 8 caracteres.');
            return;
        }
        // Enviar datos de registro al servidor
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ registerUsername, registerEmail, registerPassword })
            });
            const data = await response.json();
            if (response.ok) {
                navigate("/");
            } else {
                setErrorMessage(data.message || 'Error al registrar usuario');
            }
        } catch (error) {
            console.error('Error al enviar la solicitud de registro:', error);
            setErrorMessage('Error de conexión al registrar usuario');
        }
    };

    const validateEmail = (email) => {
        // Expresión regular para validar formato de correo electrónico
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const validatePassword = (password) => {
        // Validar que la contraseña tenga al menos 8 caracteres
        return password.length >= 8;
    };

    const redirectToLogin = () => {
        navigate("/");
    };

    return (
        <div className='register-container'>
            <div className='register-form-container'>
                <h2>Registrarse</h2>
                <form className='register-form' onSubmit={handleSubmit}>
                    <div className='form-group'>
                        <label htmlFor="registerUsername">Usuario:</label>
                        <input type="text" id="registerUsername" value={registerUsername} onChange={(e) => setRegisterUsername(e.target.value)} required />
                    </div>
                    <div className='form-group'>
                        <label htmlFor="registerPassword">Contraseña:</label>
                        <input type="password" id="registerPassword" value={registerPassword} onChange={(e) => setRegisterPassword(e.target.value)} required />
                    </div>
                    <div className='form-group'>
                        <label htmlFor="registerEmail">Correo electrónico:</label>
                        <input type="email" id="registerEmail" value={registerEmail} onChange={(e) => setRegisterEmail(e.target.value)} required />
                    </div>
                    <button type="submit">Registrarse</button>
                </form>
                <button onClick={redirectToLogin}>Iniciar Sesión</button>
            </div>
            {errorMessage && <p className='error-message' style={{ color: 'red' }}>{errorMessage}</p>}
        </div>
    );
}

export default RegisterForm;
