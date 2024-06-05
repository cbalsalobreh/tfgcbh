import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Habitacion.css';
import { useAudioRecorder } from 'react-audio-voice-recorder';
import socketIOClient from 'socket.io-client';

const ENDPOINT = 'http://localhost:5001';
const socket = socketIOClient(ENDPOINT);

function Habitacion() {
    const { startRecording, stopRecording, isRecording, recordingBlob } = useAudioRecorder();
    const [transcription, setTranscription] = useState('');
    const [audioUrl, setAudioUrl] = useState('');

    const { nombre } = useParams();
    const [habitacion, setHabitacion] = useState(null);
    const [dispositivos, setDispositivos] = useState([]);
    const [nuevoDispositivo, setNuevoDispositivo] = useState('');
    const [tipoDispositivo, setTipoDispositivo] = useState('');
    const [dispositivosPredeterminados, setDispositivosPredeterminados] = useState([]);
    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [editarDispositivoId, setEditarDispositivoId] = useState('');
    const [nuevoNombreDispositivo, setNuevoNombreDispositivo] = useState('');
    const [comandos, setComandos] = useState([]);
    const [mostrarFormularioComando, setMostrarFormularioComando] = useState(false);
    const [nuevoComando, setNuevoComando] = useState("");
    const [dispositivoSeleccionado, setDispositivoSeleccionado] = useState(null);

    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const cargarHabitacion = async () => {
            try {
                const response = await fetch(`http://localhost:5001/casa-domotica/${nombre}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    setHabitacion(data.habitacion);
                    setDispositivos(data.dispositivos || []);
                    cargarDispositivosPredeterminados(data.habitacion.tipo);
                } else {
                    const errorData = await response.json();
                    console.error('Error al cargar la habitación:', errorData);
                    setError('Error al cargar la habitación. Intente nuevamente más tarde.');
                }
            } catch (error) {
                console.error('Error al cargar la habitación:', error);
                setError('Error al cargar la habitación. Intente nuevamente más tarde.');
            }
        };

        const cargarDispositivosPredeterminados = async (tipoHabitacion) => {
            try {
                const response = await fetch(`http://localhost:5001/tipos-habitaciones/${encodeURIComponent(tipoHabitacion)}/dispositivos`);
                if (response.ok) {
                    const data = await response.json();
                    setDispositivosPredeterminados(data.dispositivos);
                } else {
                    const errorData = await response.json();
                    console.error('Error al cargar los dispositivos predeterminados:', errorData);
                    setError('Error al cargar los dispositivos predeterminados. Intente nuevamente más tarde.');
                }
            } catch (error) {
                console.error('Error al cargar los dispositivos predeterminados:', error);
                setError('Error al cargar los dispositivos predeterminados. Intente nuevamente más tarde.');
            }
        };

        cargarHabitacion();
    }, [nombre]);

    useEffect(() => {
        const handleTranscription = (data) => {
            setTranscription(data);
        };

        socket.on('transcription', handleTranscription);

        return () => {
            socket.off('transcription', handleTranscription);
        };
    }, []);

    useEffect(() => {
        if (recordingBlob && habitacion) {
            const reader = new FileReader();
            reader.readAsDataURL(recordingBlob);
            reader.onloadend = () => {
                const base64Data = reader.result.split(',')[1];
                socket.emit('audio_room', { audioData: base64Data, nombreHab: habitacion.nombre });
                
                const newAudioUrl = URL.createObjectURL(recordingBlob);
                setAudioUrl((prevAudioUrl) => {
                    if (prevAudioUrl) {
                        URL.revokeObjectURL(prevAudioUrl);
                    }
                    return newAudioUrl;
                });
            };
        }
    }, [recordingBlob, habitacion]);    

    useEffect(() => {
        socket.on('actualizar_estado', (data) => {
            console.log('estado actualizando')
            setDispositivos((prevDispositivos) => 
                prevDispositivos.map(dispositivo =>
                    dispositivo.id === data.dispositivoId
                        ? { ...dispositivo, estado: data.nuevoEstado }
                        : dispositivo
                )
            );
            console.log('estado:', data.nuevoEstado)
        });
    
        return () => {
            socket.off('actualizar_estado');
        };
    }, []);    

    const eliminarHabitacion = async () => {
        try {
            const response = await fetch(`http://localhost:5001/casa-domotica/${nombre}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            if (response.ok) {
                navigate('/casa-domotica');
            } else {
                console.error('Error al eliminar la habitación');
                setError('Error al eliminar la habitación. Intente nuevamente más tarde.');
            }
        } catch (error) {
            console.error('Error al eliminar la habitación:', error);
            setError('Error al eliminar la habitación. Intente nuevamente más tarde.');
        }
    };

    const volver = () => {
        navigate('/casa-domotica');
    };

    const agregarDispositivo = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.error('Token de autenticación no encontrado');
                return;
            }

            const response = await fetch(`http://localhost:5001/casa-domotica/${nombre}/dispositivos`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ nombre: nuevoDispositivo, tipo: tipoDispositivo })
            });

            if (response.ok) {
                const nuevoDispositivoData = await response.json();
                setDispositivos([...dispositivos, nuevoDispositivoData]);
                setNuevoDispositivo('');
                setTipoDispositivo('');
                setMostrarFormulario(false);
                window.location.reload(); 
            } else {
                console.error('Error al agregar el dispositivo');
                setError('Error al agregar el dispositivo. Intente nuevamente más tarde.');
            }
        } catch (error) {
            console.error('Error al agregar el dispositivo:', error);
            setError('Error al agregar el dispositivo. Intente nuevamente más tarde.');
        }
    };

    const handleEditarDispositivo = (id, nombre) => {
        setEditarDispositivoId(id);
        setNuevoNombreDispositivo(nombre);
        setMostrarFormulario(true);
    };

    const handleCancelarEdicion = () => {
        setEditarDispositivoId(null);
        setNuevoNombreDispositivo('');
    }

    async function handleActualizarNombreDispositivo(dispositivoId, nuevoNombre) {
        if (!dispositivoId || !nuevoNombre) {
            console.error('Falta información necesaria para actualizar el nombre del dispositivo.');
            return;
        }
    
        try {
            const response = await fetch(`http://localhost:5001/casa-domotica/${nombre}/dispositivos/${dispositivoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    nuevo_nombre: nuevoNombre
                })
            });
    
            if (response.ok) {
                window.location.reload();
            } else {
                const errorData = await response.json();
                console.error('Error al actualizar nombre del dispositivo:', errorData);
            }
        } catch (error) {
            console.error('Error al actualizar nombre del dispositivo:', error);
        }
    }
    

    const handleEliminarDispositivo = async (dispositivoId) => {
        try {
            const response = await fetch(`http://localhost:5001/casa-domotica/${nombre}/dispositivos/${dispositivoId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            if (response.ok) {
                setDispositivos(dispositivos.filter(dispositivo => dispositivo.id !== dispositivoId));
            } else {
                console.error('Error al eliminar el dispositivo');
                setError('Error al eliminar el dispositivo. Intente nuevamente más tarde.');
            }
        } catch (error) {
            console.error('Error al eliminar el dispositivo:', error);
            setError('Error al eliminar el dispositivo. Intente nuevamente más tarde.');
        }
    };

    const handleComandos = async (dispositivoId) => {
        try {
            const response = await fetch(`http://localhost:5001/casa-domotica/comandos/${dispositivoId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setComandos(data);
                setDispositivoSeleccionado(dispositivoId);
                setMostrarFormularioComando(false);
            } else {
                const errorData = await response.json();
                console.error('Error al cargar los comandos:', errorData);
                setError('Error al cargar los comandos. Intente nuevamente más tarde.');
            }
        } catch (error) {
            console.error('Error al cargar los comandos:', error);
            setError('Error al cargar los comandos. Intente nuevamente más tarde.');
        }
    }

    const handleCerrarComandos = async () => {
        setComandos(null);
        setDispositivoSeleccionado(null);
    }

    const handleAgregarComando = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`http://localhost:5001/casa-domotica/${dispositivoSeleccionado}/comando`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ comando: nuevoComando })
            });
            if (response.ok) {
                const newComando = await response.json();
                setComandos([...comandos.comandos, newComando]);
                setNuevoComando("");
                setMostrarFormularioComando(false);
                handleComandos(dispositivoSeleccionado);
            } else {
                const errorData = await response.json();
                console.error('Error al agregar el comando:', errorData);
                setError('Error al agregar el comando. Intente nuevamente más tarde.');
            }
        } catch (error) {
            console.error('Error al agregar el comando:', error);
            setError('Error al agregar el comando. Intente nuevamente más tarde.');
        }
    };       

    if (!habitacion) {
        return <p>Cargando habitación...</p>;
    }

    return (
        <div className="habitacion-container">
            {error && <p className="error-message">{error}</p>}
            <h2>Dispositivos de {habitacion.nombre}</h2>
            <button onClick={volver} className="back-button">Volver</button>
            <button onClick={eliminarHabitacion} className="delete-button">Eliminar Habitación</button>
            <ul>
                {dispositivos.length > 0 ? (
                    dispositivos.map((dispositivo) => (
                        <li key={dispositivo.id}>
                            {editarDispositivoId === dispositivo.id ? (
                                <div className="editar-dispositivo-form">
                                    <input
                                        type="text"
                                        value={nuevoNombreDispositivo}
                                        onChange={(e) => setNuevoNombreDispositivo(e.target.value)}
                                    />
                                    <button onClick={() => handleActualizarNombreDispositivo(dispositivo.id, nuevoNombreDispositivo)}>Guardar</button>
                                    <button onClick={handleCancelarEdicion} className="cancelar-button">Cancelar</button>
                                </div>
                            ) : (
                                <>
                                    <div className='info'>
                                        <span>{dispositivo.nombre}</span>
                                        <span>Tipo: {dispositivo.tipo}</span>
                                        <span>Estado: {dispositivo.estado}</span>
                                    </div>
                                    <div className='buttons'>
                                        <button onClick={() => handleComandos(dispositivo.id)} className='comandos-button'>Comandos</button>
                                        <button onClick={() => handleEditarDispositivo(dispositivo.id, dispositivo.nombre)} className="editar-button">Editar</button>
                                        <button onClick={() => handleEliminarDispositivo(dispositivo.id)} className="delete2-button">Eliminar</button>
                                    </div>
                                    {dispositivoSeleccionado === dispositivo.id && (
                                        <div>
                                            <h3>Comandos disponibles:</h3>
                                            {comandos.comandos && comandos.comandos.length > 0 ? (
                                                <ul>
                                                    {comandos.comandos.map((comando, index) => (
                                                    <li key={index}>{comando}</li>
                                                    ))}
                                                </ul>
                                                ) : (
                                                <p>No hay comandos disponibles.</p>
                                                )}
                                            {mostrarFormularioComando ? (
                                                <form onSubmit={handleAgregarComando}>
                                                    <input
                                                        type="text"
                                                        placeholder="Nuevo Comando"
                                                        value={nuevoComando}
                                                        onChange={(e) => setNuevoComando(e.target.value)}
                                                    />
                                                    <button type="submit">Agregar</button>
                                                    <button type="button" onClick={() => setMostrarFormularioComando(false)}>Cancelar</button>
                                                </form>
                                            ) : (
                                                <div className='add-close-buttons'>
                                                    <button className='agregar-comando-button' onClick={() => setMostrarFormularioComando(true)}>Agregar Comando</button>
                                                    <button className='cerrar-button' onClick={() => handleCerrarComandos()}>Cerrar</button>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </>
                            )}
                        </li>
                    ))
                ) : (
                    <p>No hay dispositivos en esta habitación.</p>
                )}
            </ul>
            {mostrarFormulario ? (
                <form onSubmit={agregarDispositivo} className="nueva-dispositivo-form">
                    <input
                        type="text"
                        placeholder="Nombre del dispositivo"
                        value={nuevoDispositivo}
                        onChange={(e) => setNuevoDispositivo(e.target.value)}
                    />
                    <select value={tipoDispositivo} onChange={(e) => setTipoDispositivo(e.target.value)}>
                        <option value="">Seleccionar tipo</option>
                        {dispositivosPredeterminados.map((dispositivo, index) => (
                            <option key={index} value={dispositivo}>{dispositivo}</option>
                        ))}
                    </select>
                    <div className="form-buttons">
                        <button type="submit">Agregar</button>
                        <button type="button" className="cancelar-button" onClick={() => setMostrarFormulario(false)}>Cancelar</button>
                    </div>
                </form>
            ) : (
                <button onClick={() => setMostrarFormulario(true)} className="agregar-button">Agregar Dispositivo</button>
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

export default Habitacion;
