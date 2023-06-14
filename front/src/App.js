import React, {useState, useEffect} from 'react'

export default function App() {
  const [src, setSrc] = useState("right-curl")
  const [time, setTime] = useState('00:00')

  useEffect(() => {
    const startTime = new Date().getTime();

    const interval = setInterval(() => {
      const currentTime = new Date().getTime();
      const elapsedTimeInSeconds = Math.floor((currentTime - startTime) / 1000);
      const minutes = Math.floor(elapsedTimeInSeconds / 60);
      const seconds = elapsedTimeInSeconds % 60;
      const formattedTime = `${padDigits(minutes)}:${padDigits(seconds)}`;
      setTime(formattedTime);
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  // Helper function to pad single digits with leading zeros
  const padDigits = (value) => {
    return String(value).padStart(2, '0');
  };

  return (
    <>
      
      <div className='video-container'>
        <h3>Rutina 1 {time}</h3>
        <img src={"http://127.0.0.1:5000/video_feed/"+src}  className='video'/>
        <br></br>
        <button onClick={()=>setSrc("squat")} className='change-exer-btn'>
          squat
        </button>
        <button onClick={()=>setSrc("squat")} className='change-exer-btn'>
          squat
        </button>
      </div>
    </>
  )
}
