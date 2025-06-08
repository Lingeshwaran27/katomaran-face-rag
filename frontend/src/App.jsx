import React, { useState } from 'react';
import RegistrationTab from './components/RegistrationTab';
import RecognitionTab from './components/RecognitionTab';

function App() {
  const [tab, setTab] = useState('register');

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>Katomaran Face System</h1>
      <button onClick={() => setTab('register')}>Register</button>
      <button onClick={() => setTab('recognize')}>Recognize</button>

      {tab === 'register' && <RegistrationTab />}
      {tab === 'recognize' && <RecognitionTab />}
    </div>
  );
}

export default App;
