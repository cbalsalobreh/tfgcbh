
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CasaDomotica.css';
import { useAudioRecorder } from 'react-audio-voice-recorder';
import socketIOClient from 'socket.io-client';

const ENDPOINT = 'http://localhost:5001';
const socket = socketIOClient(ENDPOINT, {
    extraHeaders: {
      Authorization: `Bearer ${localStorage.getItem('token')}`
    }
});

function CasaDomotica() {
    const { startRecording, stopRecording, isRecording, recordingBlob } = useAudioRecorder();
    const [transcription, setTranscription] = useState('');
    const [audioUrl, setAudioUrl] = useState('');

    const [dispositivo, setDispositivo] = useState('');
    const [estado, setEstado] = useState('');
    const [habitacion, setHabitacion] = useState('');
    const [username, setUsername ] = useState('');

    const [habitaciones, setHabitaciones] = useState([]);
    const [tiposHabitaciones, setTiposHabitaciones] = useState([]);
    const [nuevaHabitacion, setNuevaHabitacion] = useState('');
    const [tipoHabitacion, setTipoHabitacion] = useState('');
    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [esTipoPersonalizado, setEsTipoPersonalizado] = useState(false);
    const [tipoPersonalizado, setTipoPersonalizado] = useState('');
    const [editarHabitacionId, setEditarHabitacionId] = useState(null);
    const [nuevoNombreHabitacion, setNuevoNombreHabitacion] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        cargarHabitaciones();
        cargarTiposHabitaciones();
    }, []);

    useEffect(() => {
        async function fetchUserData() {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    console.error('Token no encontrado');
                    return;
                }
                
                const response = await fetch(`/get_username`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    const userData = await response.json();
                    setUsername(userData.username);
                } else {
                    console.error('Error al obtener los datos del usuario');
                }
            } catch (error) {
                console.error('Error al obtener los datos del usuario:', error);
            }
        }
        fetchUserData();
    }, []);

    useEffect(() => {
        const handleTranscription = (data) => {
            setTranscription(data);
        };

        socket.on('transcription', handleTranscription);

        const handleEstadoDispositivo = (data) => {
            setDispositivo(data.dispositivo);
            setEstado(data.estado);
            setHabitacion(data.habitacion);
        };

        socket.on('estado_dispositivo', handleEstadoDispositivo);

        return () => {
            socket.off('transcription', handleTranscription);
            socket.off('estado_dispositivo', handleEstadoDispositivo);
        };
    }, []);  

    useEffect(() => {
        if (recordingBlob) {
            const reader = new FileReader();
            reader.readAsDataURL(recordingBlob);
            reader.onloadend = () => {
                const base64Data = reader.result.split(',')[1];
                socket.emit('audio', base64Data);
                const newAudioUrl = URL.createObjectURL(recordingBlob);
                setAudioUrl((prevAudioUrl) => {
                    if (prevAudioUrl) {
                        URL.revokeObjectURL(prevAudioUrl);
                    }
                    return newAudioUrl;
                });
            };
        }
    }, [recordingBlob]);

    const cargarHabitaciones = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Token de autenticación no encontrado');
            }
            const response = await fetch('/casa-domotica', {
                headers: {
                'Authorization': `Bearer ${token}`,
                },
            });
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            const data = await response.json();
            setHabitaciones(data);
            } catch (error) {
            console.error('Error al cargar habitaciones:', error);
            }
    };

    const cargarTiposHabitaciones = async () => {
        try {
            const response = await fetch('/tipos-habitaciones');
            if (response.ok) {
                const data = await response.json();
                setTiposHabitaciones(data.tipos_habitaciones);
            } else {
                console.error('Error al cargar los tipos de habitaciones');
            }
        } catch (error) {
            console.error('Error al cargar los tipos de habitaciones:', error);
        }
    };

    const handleAgregarHabitacion = async () => {
        let tipoHabitacionId = tipoHabitacion;
    
        if (tipoHabitacion === 'Otro' && tipoPersonalizado) {
            try {
                const tipoExistente = tiposHabitaciones.find(tipo => tipo.nombre === tipoPersonalizado);
                if (tipoExistente) {
                    tipoHabitacionId = tipoExistente.id;
                } else {
                    const response = await fetch('/tipos-habitaciones', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ nombre: tipoPersonalizado }),
                    });
    
                    if (response.ok) {
                        const data = await response.json();
                        tipoHabitacionId = data.id;
                    } else {
                        console.error('Error al agregar el nuevo tipo de habitación');
                        return;
                    }
                }
            } catch (error) {
                console.error('Error al agregar el nuevo tipo de habitación:', error);
                return;
            }
        }
    
        try {
            const response = await fetch('/casa-domotica', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ nombre: nuevaHabitacion, tipo: tipoHabitacionId })
            });
    
            if (response.ok) {
                cargarHabitaciones();
                setMostrarFormulario(false);
                setNuevaHabitacion('');
                setTipoHabitacion('');
            } else {
                console.error('Error al agregar habitación');
            }
        } catch (error) {
            console.error('Error al agregar habitación:', error);
        }
    };    

    async function handleActualizarHabitacion() {
        const nombreActual = habitaciones.find(hab => hab[0] === editarHabitacionId)?.[1];
        const nuevoNombre = nuevoNombreHabitacion;
        console.log(nombreActual, nuevoNombre);
    
        if (!nombreActual || !nuevoNombre) {
            console.error('Nombre actual o nuevo nombre no están disponibles.');
            return;
        }
    
        try {
            const response = await fetch(`/casa-domotica/${nombreActual}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    nombre_actual: nombreActual,
                    nuevo_nombre: nuevoNombre
                })
            });
    
            if (response.ok) {
                setEditarHabitacionId(null);
                setNuevoNombreHabitacion('');
                cargarHabitaciones();
            } else {
                const errorData = await response.json();
                console.error('Error al actualizar habitación', errorData);
            }
        } catch (error) {
            console.error('Error al actualizar habitación', error);
        }
    }
    
    const handleEliminarHabitacion = async (id) => {
        try {
            const response = await fetch(`/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            if (response.ok) {
                cargarHabitaciones();
            } else {
                console.error('Error al eliminar la habitación');
            }
        } catch (error) {
            console.error('Error al eliminar la habitación:', error);
        }
    };

    const handleAgregarClick = () => {
        setMostrarFormulario(true);
    };

    const handleCancelarClick = () => {
        setMostrarFormulario(false);
        setNuevaHabitacion('');
        setTipoHabitacion('');
        setEsTipoPersonalizado(false);
        setTipoPersonalizado('');
    };

    const handleTipoChange = (e) => {
        const value = e.target.value;
        setTipoHabitacion(value);
    }

    const handleLogout = async () => {
        try {
            const response = await fetch('/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                localStorage.removeItem('token');
                navigate('/');
            } else {
                console.error('Error al cerrar sesión');
            }
        } catch (error) {
            console.error('Error al cerrar sesión:', error);
        }
    };

    const handleHabitacionClick = (nombre) => {
        navigate(`/casa-domotica/${nombre}`);
    };

    const handleEditarClick = (id, nombre) => {
        setEditarHabitacionId(id);
        setNuevoNombreHabitacion(nombre);
        cargarHabitaciones();
    };

    const handleCancelarEdicion = () => {
        setEditarHabitacionId(null);
        setNuevoNombreHabitacion('');
    };

    return (
        <div className="casadomotica-container">
            <header className="header">
                <h5>Bienvenido <a href={`/usuario/${username}`}>@{username}</a> a las habitaciones de tu casa domótica</h5>
                <button onClick={handleLogout} className="logout-button">Cerrar Sesión</button>
            </header>
            <ul className="habitaciones-list">
                {habitaciones.length > 0 ? (
                    habitaciones.map((habitacion) => (
                        <li key={habitacion[0]} className="habitacion-item">
                            {editarHabitacionId === habitacion[0] ? (
                                <div className="editar-habitacion-form">
                                    <input
                                        type="text"
                                        value={nuevoNombreHabitacion}
                                        onChange={(e) => setNuevoNombreHabitacion(e.target.value)}
                                    />
                                    <button onClick={handleActualizarHabitacion}>Guardar</button>
                                    <button onClick={handleCancelarEdicion} className="cancelar-button">Cancelar</button>
                                </div>
                            ) : (
                                <>
                                    <button onClick={() => handleHabitacionClick(habitacion[1])}>{habitacion[1]}</button>
                                    <button onClick={() => handleEditarClick(habitacion[0], habitacion[1])} className="editar-button">Editar</button>
                                    <button onClick={() => handleEliminarHabitacion(habitacion[0])} className="delete-button">Eliminar</button>
                                </>
                            )}
                        </li>
                    ))
                ) : (
                    <p>No hay habitaciones disponibles.</p>
                )}
            </ul>
    
            {mostrarFormulario ? (
                <div className="nueva-habitacion-form">
                    <input
                        type="text"
                        placeholder="Nombre de la habitación"
                        value={nuevaHabitacion}
                        onChange={(e) => setNuevaHabitacion(e.target.value)}
                    />
                    {tiposHabitaciones && tiposHabitaciones.length > 0 && (
                        <select value={tipoHabitacion} onChange={handleTipoChange}>
                            <option value="">Seleccionar tipo de habitación</option>
                            {tiposHabitaciones.map((tipo) => (
                                <option key={tipo.id} value={tipo.nombre}>{tipo.nombre}</option>
                            ))}
                        </select>
                    )}
                    {esTipoPersonalizado && (
                        <input
                            type="text"
                            placeholder="Tipo de habitación"
                            value={tipoPersonalizado}
                            onChange={(e) => setTipoPersonalizado(e.target.value)}
                        />
                    )}
                    <button onClick={handleAgregarHabitacion}>Agregar</button>
                    <button className="cancel-button" onClick={handleCancelarClick}>Cancelar</button>
                </div>
            ) : (
                <button onClick={handleAgregarClick} className="agregar-button">Agregar Habitación</button>
            )}
            <div>
                {isRecording ? <p>Grabando...</p> : <p>Listo para grabar</p>}
                <button onClick={startRecording} disabled={isRecording}>
                    Iniciar Grabación
                </button>
                {isRecording && (
                    <button onClick={stopRecording}>Detener Grabación</button>
                )}
                <p>Transcripción: {transcription}</p>
                <p>Dispositivo: {dispositivo}</p>
                <p>Estado: {estado}</p>
                <p>Habitación: {habitacion}</p>
                {audioUrl && (
                    <div>
                        <audio controls key={audioUrl}>
                            <source src={audioUrl} />
                            Su navegador no soporta el elemento de audio.
                        </audio>
                        <a href={audioUrl}>Descargar audio</a>
                    </div>
                )}
            </div>
        </div>
    );           
}

export default CasaDomotica;
