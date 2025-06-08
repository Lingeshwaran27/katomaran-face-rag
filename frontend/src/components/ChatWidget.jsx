import React, { useState } from 'react';
import axios from 'axios';

const ChatWidget = () => {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newChat = [...chat, { type: 'user', text: input }];
    setChat(newChat);
    setInput('');

    try {
      const res = await axios.post('http://localhost:5000/chat', {
        message: input
      });

      const reply = res.data.answer;
      setChat([...newChat, { type: 'bot', text: reply }]);
    } catch (err) {
      console.error(err);
      setChat([...newChat, { type: 'bot', text: '❌ Error talking to server.' }]);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', textAlign: 'left' }}>
      <h2>🧠 Ask About Registrations</h2>

      <div style={{
        border: '1px solid #ccc',
        padding: 10,
        height: 200,
        overflowY: 'scroll',
        marginBottom: 10
      }}>
        {chat.map((msg, idx) => (
          <p key={idx}>
            <strong>{msg.type === 'user' ? 'You' : 'Bot'}:</strong> {msg.text}
          </p>
        ))}
      </div>

      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question..."
        style={{ width: '70%', marginRight: 10 }}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};

export default ChatWidget;
