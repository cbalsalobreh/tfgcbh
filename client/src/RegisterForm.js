import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginForm.css';

function RegisterForm() {
    const [registerUsername, setRegisterUsername] = useState('');
    const [registerPassword, setRegisterPassword] = useState('');
    const [registerEmail, setRegisterEmail] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [csrfToken, setCsrfToken] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Al montar el componente, solicita y guarda el token CSRF
        fetchCsrfToken();
    }, []);

    const fetchCsrfToken = async () => {
        try {
            const response = await fetch('/csrf-token', {
                credentials: 'include', // Incluye las cookies en la solicitud
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            setCsrfToken(data.csrf_token);
        } catch (error) {
            console.error('Error al obtener el token CSRF:', error);
            setErrorMessage('Error al obtener el token CSRF');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        // Validar formato de correo electrónico
        if (!validateEmail(registerEmail)) {
            setErrorMessage('Por favor, introduce un correo electrónico válido.');
            setIsLoading(false);
            return;
        }
        // Validar seguridad de contraseña
        const passwordValidationResult = validatePassword(registerPassword);
        if (passwordValidationResult !== "La contraseña es válida.") {
            setErrorMessage(passwordValidationResult);
            setIsLoading(false);
            return;
        }
        // Enviar datos de registro al servidor
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfToken
                },
                body: JSON.stringify({ registerUsername, registerEmail, registerPassword })
            });
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('token', data.token);
                navigate(data.redirect);
            } else {
                if (response.status === 400){
                    setErrorMessage('El usuario ya está registrado.');
                } if (response.status === 409){
                    setErrorMessage('El correo electrónico ya está registrado.');
                } else {
                    setErrorMessage(data.message || 'Error al registrar usuario');
                }
                setIsLoading(false);
            }
        } catch (error) {
            console.error('Error al enviar la solicitud de registro:', error);
            setErrorMessage('Error de conexión al registrar usuario');
            setIsLoading(false);
        }
    };

    const validateEmail = (email) => {
        // Expresión regular para validar formato de correo electrónico
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const validatePassword = (password) => {
        // Validar que la contraseña tenga al menos 8 caracteres
        if (password.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
    
        // Validar que la contraseña tenga al menos una letra mayúscula
        const hasUpperCase = /[A-Z]/.test(password);
        if (!hasUpperCase) return "La contraseña debe tener al menos una letra mayúscula.";
    
        // Validar que la contraseña tenga al menos una letra minúscula
        const hasLowerCase = /[a-z]/.test(password);
        if (!hasLowerCase) return "La contraseña debe tener al menos una letra minúscula.";
    
        // Validar que la contraseña tenga al menos un número
        const hasNumber = /[0-9]/.test(password);
        if (!hasNumber) return "La contraseña debe tener al menos un número.";
    
        // Validar que la contraseña tenga al menos un carácter especial
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        if (!hasSpecialChar) return "La contraseña debe tener al menos un carácter especial.";
    
        // Si pasa todas las validaciones, retornar éxito
        return "La contraseña es válida.";
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
                    <button type='submit' disabled={isLoading}>
                        {isLoading ? 'Cargando...' : 'Registrarse'}
                    </button>
                </form>
                <button onClick={redirectToLogin}>Iniciar Sesión</button>
            </div>
            {errorMessage && <p className='error-message' style={{ color: 'red' }}>{errorMessage}</p>}
        </div>
    );
}

export default RegisterForm;
