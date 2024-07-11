import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './Usuario.css';

function Usuario() {
  const { username } = useParams();
  const [user, setUser] = useState({});
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    console.log(`Fetching data for user: ${username}`);
    async function fetchUserData() {
        try {
            const response = await fetch(`/usuarios/${username}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
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
      const response = await fetch(`/usuarios/${username}/password`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ newPassword }),
      });

      if (!response.ok) {
        throw new Error('Error al cambiar la contraseña. Por favor, inténtalo de nuevo.');
      }
      setUser({ ...user});
      setNewPassword('');
      setConfirmPassword('');
      setErrorMessage('Error al cambiar la contraseña. Por favor, inténtalo de nuevo.');
    } catch (error) {
      setErrorMessage('Error al cambiar la contraseña. Por favor, inténtalo de nuevo.');
    }
  };

  const handleVolver = () => {
    navigate(`/usuarios/${username}/habitaciones`);
  };

  return (
    <div>
      <button className="volver-button" onClick={handleVolver}>Volver</button>
      <div>
        <h2>Información del Usuario</h2>
        <p>Usuario: {user.username}</p>
        <p>Email: {user.email}</p>
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
