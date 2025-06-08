import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

const RecognitionTab = () => {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [faces, setFaces] = useState([]);

  const captureFrame = async () => {
    const imageSrc = webcamRef.current.getScreenshot();

    if (!imageSrc) return;

    const blob = await (await fetch(imageSrc)).blob();
    const file = new File([blob], 'frame.jpg', { type: 'image/jpeg' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:5000/recognize', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setFaces(res.data.results || []);
    } catch (err) {
      console.error('Recognition error:', err);
    }
  };

  const drawBoxes = () => {
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);

    faces.forEach(face => {
      const [top, right, bottom, left] = face.box;
      context.strokeStyle = 'lime';
      context.lineWidth = 2;
      context.strokeRect(left, top, right - left, bottom - top);

      context.fillStyle = 'lime';
      context.font = '16px Arial';
      context.fillText(face.name, left, top - 10);
    });
  };

  useEffect(() => {
    const interval = setInterval(() => {
      captureFrame();
    }, 1000); // Poll every 1 second

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    drawBoxes();
  }, [faces]);

  return (
    <div style={{ position: 'relative', width: 320, height: 240 }}>
      <Webcam
        ref={webcamRef}
        audio={false}
        screenshotFormat="image/jpeg"
        width={320}
        height={240}
        style={{ position: 'absolute' }}
      />
      <canvas
        ref={canvasRef}
        width={320}
        height={240}
        style={{ position: 'absolute', pointerEvents: 'none' }}
      />
    </div>
  );
};

export default RecognitionTab;
