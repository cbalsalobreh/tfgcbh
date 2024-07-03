
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './CasaDomotica.css';
import { useAudioRecorder } from 'react-audio-voice-recorder';
import socketIOClient from 'socket.io-client';

const ENDPOINT = 'http://localhost:5001';

function CasaDomotica() {
    const { startRecording, stopRecording, isRecording, recordingBlob } = useAudioRecorder();
    const [transcription, setTranscription] = useState('');
    const [audioUrl, setAudioUrl] = useState('');

    const [dispositivo, setDispositivo] = useState('');
    const [estado, setEstado] = useState('');
    const [habitacion, setHabitacion] = useState('');
    const { username } = useParams();

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
        const cargarHabitaciones = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    throw new Error('Token de autenticación no encontrado');
                }
                const response = await fetch(`/usuarios/${username}/habitaciones`, {
                    headers: {
                    'Authorization': `Bearer ${token}`,
                    },
                });
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                const data = await response.json();
                setHabitaciones(data.habitaciones);
                } catch (error) {
                console.error('Error al cargar habitaciones:', error);
                }
        };
    
        const cargarTiposHabitaciones = async () => {
            try {
                const response = await fetch(`/tipos-habitaciones`);
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
        cargarHabitaciones();
        cargarTiposHabitaciones();
    }, [username]);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const socket = socketIOClient(ENDPOINT, {
            extraHeaders: {
                Authorization: `Bearer ${token}`
            }
        });

        const handleTranscription = (data) => {
            setTranscription(data);
        };

        const handleEstadoDispositivo = (data) => {
            setDispositivo(data.dispositivo);
            setEstado(data.estado);
            setHabitacion(data.habitacion);
        };

        socket.on('transcription', handleTranscription);
        socket.on('estado_dispositivo', handleEstadoDispositivo);

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

        return () => {
            socket.off('transcription', handleTranscription);
            socket.off('estado_dispositivo', handleEstadoDispositivo);
        };
    }, [recordingBlob]);

    const handleAgregarHabitacion = async () => {
        let tipoHabitacionId = tipoHabitacion;
        try {
            const response = await fetch(`/usuarios/${username}/habitaciones`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ nombre: nuevaHabitacion, tipo: tipoHabitacionId })
            });
    
            if (response.ok) {
                const nuevaHabitacionData = await response.json(); 
                setHabitaciones(prevHabitaciones => [...prevHabitaciones, nuevaHabitacionData]); // Actualizar el estado con la nueva habitación
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

    const handleActualizarHabitacion = async () => {
        const nombreActual = habitaciones.find(hab => hab[0] === editarHabitacionId)?.[1];
        const nuevoNombre = nuevoNombreHabitacion;
        if (!nombreActual || !nuevoNombre) {
            console.error('Nombre actual o nuevo nombre no están disponibles.');
            return;
        }
        try {
            const response = await fetch(`/usuarios/${username}/habitaciones/${nombreActual}`, {
                method: 'PATCH',
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
                const nuevasHabitaciones = habitaciones.map(hab => {
                    if (hab[0] === editarHabitacionId) {
                        return [editarHabitacionId, nuevoNombre, hab[2]];
                    }
                    return hab;
                });
                setHabitaciones(nuevasHabitaciones);
                setEditarHabitacionId(null);
                setNuevoNombreHabitacion('');
            } else {
                const errorData = await response.json();
                console.error('Error al actualizar habitación', errorData);
            }
        } catch (error) {
            console.error('Error al actualizar habitación', error);
        }
    }
    
    const handleEliminarHabitacion = async (nombre) => {
        try {
            const response = await fetch(`/usuarios/${username}/habitaciones/${nombre}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
    
            if (response.ok) {
                const nuevasHabitaciones = habitaciones.filter(hab => hab[1] !== nombre);
                setHabitaciones(nuevasHabitaciones);
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
                method: 'DELETE',
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
        navigate(`/usuarios/${username}/habitaciones/${nombre}/dispositivos`);
    };

    const handleEditarClick = (id, nombre) => {
        setEditarHabitacionId(id);
        setNuevoNombreHabitacion(nombre);
    };

    const handleCancelarEdicion = () => {
        setEditarHabitacionId(null);
        setNuevoNombreHabitacion('');
    };

    const handleNavigate = () => {
        navigate(`/usuarios/${username}`);
    };
    
    return (
        <div className="casadomotica-container">
            <header className="header">
                <h5>Bienvenido <span onClick={handleNavigate}>@{username}</span> a las habitaciones de tu casa domótica</h5>
                <button onClick={handleLogout} className="logout-button">Cerrar Sesión</button>
            </header>
            <ul className="habitaciones-list">
                {habitaciones.length > 0 ? (
                    habitaciones.map((habitacion, index) => (
                        <li key={index} className="habitacion-item">
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
                                    <button onClick={() => handleEliminarHabitacion(habitacion[1])} className="delete-button">Eliminar</button>
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
