import React from 'react';

const VoiceWave: React.FC = () => {
  return (
    <div className="voice-wave">
      <span style={{ animationDelay: '0s' }} />
      <span style={{ animationDelay: '0.1s' }} />
      <span style={{ animationDelay: '0.2s' }} />
      <span style={{ animationDelay: '0.3s' }} />
      <span style={{ animationDelay: '0.4s' }} />
    </div>
  );
};

export default VoiceWave;
