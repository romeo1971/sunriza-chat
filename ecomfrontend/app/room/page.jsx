'use client';

import {
  ControlBar,
  GridLayout,
  ParticipantTile,
  RoomAudioRenderer,
  useTracks,
  RoomContext,
} from '@livekit/components-react';
import { Room, Track } from 'livekit-client';
import '@livekit/components-styles';
import '@livekit/components-styles/prefabs';
import { useEffect, useState } from 'react';

export default function Page() {
  // TODO: get user input for room and name
  const room = 'test-room-' + Date.now();
  const name = 'quickstart-user';

  const [token, setToken] = useState('');  

  const [roomInstance] = useState(() => new Room({
    // Optimize video quality for each participant's screen
    adaptiveStream: true,
    // Enable automatic audio/video quality optimization
    dynacast: true,
    // Disable own video
    videoCaptureDefaults: {
      enabled: false,
    },
  }));

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const resp = await fetch(`/api/token?room=${room}&username=${name}`);
        const data = await resp.json();
        if (!mounted) return;
        if (data.token) {

          setToken(data.token); 

          await roomInstance.connect("wss://sunriza26-g5a1is22.livekit.cloud", data.token);
        }
      } catch (e) {
        console.error(e);
      }
    })();
  
    return () => {
      mounted = false;
      roomInstance.disconnect();
    };
  }, [roomInstance]);

  if (token === '') {
    return <div>Getting token...</div>;
  }

  return (
    <RoomContext.Provider value={roomInstance}>
      <div data-lk-theme="default" style={{ height: '100dvh' }}>
        {/* Your custom component with basic video conferencing functionality. */}
        <MyVideoConference />
        {/* The RoomAudioRenderer takes care of room-wide audio for you. */}
        <RoomAudioRenderer />
        {/* Controls for the user to start/stop audio, video, and screen share tracks */}
        <ControlBar />
      </div>
    </RoomContext.Provider>
  );
}

function MyVideoConference() {
  const tracks = useTracks(
    [
      { source: Track.Source.Camera, withPlaceholder: false },
    ],
    { onlySubscribed: true },
  );
  
  // Filter out tracks without actual video
  const videoTracks = tracks.filter(track => track.publication && track.publication.track);
  
  if (videoTracks.length === 0) {
    return <div style={{ height: 'calc(100vh - var(--lk-control-bar-height))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
      Waiting for avatar...
    </div>;
  }
  
  return (
    <GridLayout tracks={videoTracks} style={{ height: 'calc(100vh - var(--lk-control-bar-height))' }}>
      <ParticipantTile />
    </GridLayout>
  );
}