import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './Usuario.css';

function Usuario() {
  const { username } = useParams();
  const [user, setUser] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchUserData() {
        try {
            const response = await fetch(`/usuario/${username}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            if (!response.ok) {
                throw new Error('Error al obtener los datos del usuario');
            }
            const userData = await response.json();
            if (Array.isArray(userData) && userData.length === 1 && Array.isArray(userData[0]) && userData[0].length === 4) {
                const [id, username, email, password] = userData[0];
                setUser({ id, username, email, password });
            } else {
                console.error('Formato de datos del usuario no válido');
            }
        } catch (error) {
            console.error('Error al obtener los datos del usuario:', error.message);
        }
    }

    fetchUserData();
}, [username]);


  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      setErrorMessage('Las contraseñas no coinciden.');
      return;
    }

    try {
      const response = await fetch('/change_password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ newPassword }),
      });

      if (!response.ok) {
        throw new Error('Error al cambiar la contraseña');
      }
      setUser({ ...user, password: '********' });
      setNewPassword('');
      setConfirmPassword('');
      setShowPassword(false);
      setErrorMessage('');
    } catch (error) {
      console.error('Error al cambiar la contraseña:', error.message);
      setErrorMessage('Error al cambiar la contraseña. Por favor, inténtalo de nuevo.');
    }
  };

  const handleVolver = () => {
    navigate('/casa-domotica');
  };

  return (
    <div>
      <button className="volver-button" onClick={handleVolver}>Volver</button>
      <div>
        <h2>Información del Usuario</h2>
        <p>Usuario: {user.username}</p>
        <p>Email: {user.email}</p>
        <p>
          Contraseña: {showPassword ? user.password : '********'}{' '}
          <button onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? 'Ocultar' : 'Mostrar'}
          </button>
        </p>
        <div>
          <h3>Cambiar Contraseña</h3>
          <input
            type="password"
            placeholder="Nueva Contraseña"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <input
            type="password"
            placeholder="Confirmar Contraseña"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <button onClick={handleChangePassword}>Cambiar Contraseña</button>
          {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
        </div>
      </div>
    </div>
  );
}

export default Usuario;
