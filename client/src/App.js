import './App.css';
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import CasaDomotica from './CasaDomotica';
import Habitacion from './Habitacion';
import Usuario from './Usuario';

function App() {
  return (
    <div className="App">
      <img src="/CabeceraPWTFG.png" alt='Cabecera de Whisper Living' style={{ height: '150px', width: '100%', grid: 'flex' }}/>
      <BrowserRouter>
          <Routes>
            <Route path="/" element={<LoginForm />} />
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/usuarios/:username/habitaciones" element={<CasaDomotica />}/>
            <Route path="/usuarios/:username/habitaciones/:nombre/dispositivos" element={<Habitacion />} />
            <Route path="/usuarios/:username" element={<Usuario />} />
          </Routes>
        </BrowserRouter>
    </div>
  );
}

export default App;
