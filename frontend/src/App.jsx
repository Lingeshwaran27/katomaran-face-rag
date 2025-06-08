import React, { useState } from 'react';
import RegistrationTab from './components/RegistrationTab';
import RecognitionTab from './components/RecognitionTab';
import ChatWidget from './components/ChatWidget';

function App() {
  const [tab, setTab] = useState('register');

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>👤 Katomaran Face System</h1>

      <div style={{ marginBottom: 20 }}>
        <button onClick={() => setTab('register')}>Register</button>
        <button onClick={() => setTab('recognize')}>Recognize</button>
        <button onClick={() => setTab('chat')}>Chat</button>
      </div>

      {tab === 'register' && <RegistrationTab />}
      {tab === 'recognize' && <RecognitionTab />}
      {tab === 'chat' && <ChatWidget />}
    </div>
  );
}

export default App;
