import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginForm.css';

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
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
            setMessage('Error al obtener el token CSRF');
        }
    };

    const handleLoginSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfToken
                },
                body: JSON.stringify({ username, password, rememberMe })
            });
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('token', data.token);
                navigate(data.redirect);
            } else {
                if (response.status === 400){
                    setMessage('No existe el usuario.');
                } if (response.status === 409){
                    setMessage('Contraseña incorrecta.');
                } else {
                    setMessage(data.message || 'Error al registrar usuario');
                }
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
                            value={username} 
                            onChange={(e) => setUsername(e.target.value)} 
                            required 
                        />
                    </div>
                    <div className='form-group'>
                        <label htmlFor='loginPassword'>Contraseña:</label>
                        <input 
                            type='password' 
                            id='loginPassword' 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)} 
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
