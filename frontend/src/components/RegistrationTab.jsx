import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

const RegistrationTab = () => {
  const webcamRef = useRef(null);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');

  const captureAndSend = async () => {
    if (!name) return setMessage('Please enter a name');

    const imageSrc = webcamRef.current.getScreenshot();

    if (!imageSrc) {
      setMessage("Couldn't capture image");
      return;
    }

    // Convert base64 image to blob
    const blob = await (await fetch(imageSrc)).blob();
    const file = new File([blob], 'face.jpg', { type: 'image/jpeg' });

    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:5000/register', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage(`✅ Registered: ${res.data.name}`);
    } catch (err) {
      console.error(err);
      setMessage('❌ Registration failed');
    }
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <h2>Register Face</h2>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={320}
        height={240}
      />
      <div style={{ margin: '10px' }}>
        <input
          type="text"
          placeholder="Enter name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      <button onClick={captureAndSend}>Register</button>
      <p>{message}</p>
    </div>
  );
};


export default RegistrationTab;
