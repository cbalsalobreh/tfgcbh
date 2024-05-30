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
                console.log(`Cargando dispositivos predeterminados para tipo: ${tipoHabitacion}`);
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
            const { dispositivoId, nuevoEstado } = data;
            setDispositivos(dispositivos.map(dispositivo => {
                if (dispositivo.id === dispositivoId) {
                    return { ...dispositivo, estado: nuevoEstado };
                }
                return dispositivo;
            }));
        });

        return () => {
            socket.off('actualizar_estado');
        };
    })

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
            } else {
                console.error('Error al agregar el dispositivo');
                setError('Error al agregar el dispositivo. Intente nuevamente más tarde.');
            }
        } catch (error) {
            console.error('Error al agregar el dispositivo:', error);
            setError('Error al agregar el dispositivo. Intente nuevamente más tarde.');
        }
    };

    const eliminarDispositivo = async (dispositivoId) => {
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
                            <span>{dispositivo.nombre}</span>
                            <span>Tipo: {dispositivo.tipo}</span>
                            <span>Estado: {dispositivo.estado}</span>
                            <button className="delete2-button" onClick={() => eliminarDispositivo(dispositivo.id)}>Eliminar</button>
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
