import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginForm.css';

function LoginForm() {
    const [loginUsername, setLoginUsername] = useState('');
    const [loginPassword, setLoginPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const [csrfToken, setCsrfToken] = useState('');
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Al montar el componente, solicita y guarda el token CSRF
        fetchCsrfToken();
    }, []);

    const fetchCsrfToken = async () => {
        try {
            const response = await fetch('http://localhost:5001/');
            const data = await response.json();
            setCsrfToken(data.csrf_token);
        } catch (error) {
            console.error('Error al obtener el token CSRF:', error);
            setMessage('Error al obtener el token CSRF');
        }
    };

    const handleLoginSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:5001/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfToken
                },
                body: JSON.stringify({ loginUsername, loginPassword, rememberMe })
            });
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('token', data.token);
                navigate(data.redirect);
            } else {
                setMessage(data.message || 'Inicio de sesión fallido');
            }
        } catch (error) {
            console.error('Error al enviar la solicitud de inicio de sesión:', error);
            setMessage('Error de conexión al iniciar sesión');
        } finally {
            setIsLoading(false);
        }
    };

    const redirectToRegister = () => {
        navigate('/register');
    };

    return (
        <div className='login-container'>
            <div className='login-form-container'>
                <h2>Iniciar Sesión</h2>
                <form className='login-form' onSubmit={handleLoginSubmit}>
                    <div className='form-group'>
                        <label htmlFor='loginUsername'>Usuario:</label>
                        <input 
                            type='text' 
                            id='loginUsername' 
                            value={loginUsername} 
                            onChange={(e) => setLoginUsername(e.target.value)} 
                            required 
                        />
                    </div>
                    <div className='form-group'>
                        <label htmlFor='loginPassword'>Contraseña:</label>
                        <input 
                            type='password' 
                            id='loginPassword' 
                            value={loginPassword} 
                            onChange={(e) => setLoginPassword(e.target.value)} 
                            required 
                        />
                    </div>
                    <div className='form-group'>
                        <label>
                            <input 
                                type='checkbox' 
                                checked={rememberMe} 
                                onChange={(e) => setRememberMe(e.target.checked)} 
                            />
                            Mantener la sesión iniciada
                        </label>
                    </div>
                    <button type='submit' disabled={isLoading}>
                        {isLoading ? 'Cargando...' : 'Iniciar Sesión'}
                    </button>
                </form>
                <button onClick={redirectToRegister}>Registrarse</button>
            </div>
            {message && <p className='message' style={{ color: 'red' }}>{message}</p>}
        </div>
    );
}

export default LoginForm;
