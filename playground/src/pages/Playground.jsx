import { useState, useEffect, useRef } from 'react'
import '../App.css'

function Playground() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [telemetry, setTelemetry] = useState({
    instance_id: "Spawning...",
    generation: 0,
    age: 0,
    energy: 100,
    state: "INCUBATING",
    predator_distance: "N/A"
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket connection logic with auto-reconnect
  useEffect(() => {
    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket("ws://127.0.0.1:8000/ws");

      ws.onopen = () => console.log("WS Connected");

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'telemetry') {
          setTelemetry(data.data);
        }
      };

      ws.onclose = () => {
        console.log("WS Disconnected - Retrying in 2s...");
        reconnectTimer = setTimeout(connect, 2000);
      };

      ws.onerror = (err) => {
        console.error("WS Error:", err);
        ws.close();
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
      clearTimeout(reconnectTimer);
    };
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Optimistic UI update
    setMessages(prev => [...prev, { text: inputMessage, sender: 'user' }]);

    // Send to backend via HTTP
    fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: inputMessage })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'ok') {
          setMessages(prev => [...prev, { text: data.response, sender: 'agent' }]);
        }
      })
      .catch(err => {
        console.error("Failed to send:", err);
        setMessages(prev => [...prev, { text: "Connection error. Is the backend running?", sender: 'agent' }]);
      });

    setInputMessage("");
  };

  // State colors with brutalist styling
  const stateColor = {
    'INCUBATING': 'bg-gray-900 border-2 border-gray-600 shadow-[3px_3px_0px_black]',
    'BREATHING': 'bg-blue-500 border-2 border-blue-700 shadow-[3px_3px_0px_black]',
    'HEARING': 'bg-yellow-500 border-2 border-yellow-700 shadow-[3px_3px_0px_black]',
    'ACTING': 'bg-green-500 border-2 border-green-700 shadow-[3px_3px_0px_black]',
    'DYING': 'bg-red-500 border-2 border-red-700 shadow-[3px_3px_0px_black]'
  }[telemetry.state] || 'bg-gray-900 border-2 border-gray-600 shadow-[3px_3px_0px_black]';

  return (
    <div className="fixed inset-0 flex bg-black text-white p-4 font-sans gap-4 overflow-hidden">

      {/* LEFT PANEL: Chat Interface */}
      <div className="flex flex-col w-2/3 bg-white text-black border-4 border-black shadow-[6px_6px_0px_black] rounded-lg overflow-hidden transition-transform hover:shadow-[3px_3px_0px_black] hover:-translate-x-1 hover:-translate-y-1">
        <div className="bg-black text-white py-3 px-5 font-black text-xl tracking-tighter uppercase border-b-4 border-black flex flex-col justify-center">
          <div>MONO Instance Console</div>
          <div className="text-xs font-mono font-normal text-gray-400 uppercase tracking-widest mt-0.5">Phase 29: Red Queen Test</div>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="text-gray-600 text-center mt-16 text-base font-mono">
              Terminal initialized. Waiting for user input...
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[70%] px-5 py-3 rounded-lg shadow-[3px_3px_0px_black] border-2 border-black font-mono text-sm leading-relaxed ${msg.sender === 'user' ? 'bg-black text-white' : 'bg-white text-black'}`}>
                  {msg.text}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={sendMessage} className="p-4 border-t-4 border-black bg-gray-100 flex gap-4">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            className="flex-1 bg-white text-black px-4 py-2 border-2 border-black rounded shadow-[2px_2px_0px_black] focus:outline-none focus:shadow-[4px_4px_0px_black] font-mono text-sm"
            placeholder="Query the active MONO instance..."
          />
          <button type="submit" className="bg-black text-white px-6 py-2 border-2 border-black rounded shadow-[3px_3px_0px_black] hover:shadow-[1px_1px_0px_black] hover:-translate-x-1 hover:-translate-y-1 transition-all font-black text-sm uppercase tracking-wider">
            Send
          </button>
        </form>
      </div>

      {/* RIGHT PANEL: Telemetry Dashboard */}
      <div className="flex flex-col w-1/3 bg-white text-black border-4 border-black shadow-[6px_6px_0px_black] rounded-lg overflow-hidden transition-transform hover:shadow-[3px_3px_0px_black] hover:-translate-x-1 hover:-translate-y-1">
        <div className="bg-black text-white py-3 px-5 font-black text-xl tracking-tighter uppercase border-b-4 border-black">
          Telemetry Dashboard
        </div>

        {/* Removed overflow-y-auto and adjusted spacing to fit exactly */}
        <div className="p-5 flex-1 flex flex-col justify-between bg-gray-50 overflow-hidden">

          {/* Active Instance Identity */}
          <div>
            <h3 className="text-xs text-gray-600 uppercase tracking-widest mb-1.5 font-bold">Active Instance</h3>
            <div className="text-sm font-black bg-white p-3 rounded border-2 border-black shadow-[3px_3px_0px_black] font-mono truncate">
              {telemetry.instance_id}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Generation */}
            <div className="bg-white p-4 rounded border-2 border-black shadow-[3px_3px_0px_black] text-center flex flex-col justify-center">
              <div className="text-[10px] text-gray-600 uppercase tracking-widest mb-1 font-bold">Generation</div>
              <div className="text-3xl font-black text-blue-600 leading-none">{telemetry.generation}</div>
            </div>

            {/* Age */}
            <div className="bg-white p-4 rounded border-2 border-black shadow-[3px_3px_0px_black] text-center flex flex-col justify-center">
              <div className="text-[10px] text-gray-600 uppercase tracking-widest mb-1 font-bold">Age (cycles)</div>
              <div className="text-3xl font-black text-yellow-600 leading-none">{telemetry.age}</div>
            </div>
          </div>

          {/* Energy Bar */}
          <div>
            <div className="flex justify-between items-end mb-1.5">
              <h3 className="text-xs text-gray-600 uppercase tracking-widest font-bold">Energy Reserves</h3>
              <span className="text-sm font-black text-gray-800">{telemetry.energy} EP</span>
            </div>
            <div className="w-full bg-white rounded border-2 border-black shadow-[2px_2px_0px_black] h-6 overflow-hidden relative">
              <div
                className={`h-full transition-all duration-300 shadow-[inset_0_0_0_2px_black] ${telemetry.energy < 20 ? 'bg-red-500' : 'bg-green-500'}`}
                style={{ width: `${Math.max(0, Math.min(100, telemetry.energy))}%` }}
              ></div>
            </div>
          </div>

          {/* Current State */}
          <div>
            <h3 className="text-xs text-gray-600 uppercase tracking-widest mb-1.5 font-bold">Current State</h3>
            <div className={`p-3 rounded border-2 border-black text-center font-black text-base uppercase tracking-wider ${stateColor}`}>
              <span className={telemetry.state === 'INCUBATING' ? 'text-white' : 'text-white drop-shadow-md'}>{telemetry.state}</span>
            </div>
          </div>

          {/* Predator Radar */}
          <div>
            <h3 className="text-xs text-gray-600 uppercase tracking-widest mb-1.5 font-bold flex items-center">
              <span className="mr-1.5 text-red-500">⚠</span> Predator Radar
            </h3>
            <div className="bg-black p-3.5 rounded border-2 border-red-900 shadow-[3px_3px_0px_#7f1d1d] relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-red-600 opacity-50"></div>
              <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs">
                <div className="text-gray-400 text-right uppercase tracking-wider font-bold">Status:</div>
                <div className={telemetry.predator_distance === "N/A" ? "text-gray-500 font-bold tracking-widest" : "text-red-400 font-bold tracking-widest animate-pulse"}>
                  {telemetry.predator_distance === "N/A" ? "DORMANT" : "HUNTING"}
                </div>
                <div className="text-gray-400 text-right uppercase tracking-wider font-bold">Proximity:</div>
                <div className={telemetry.predator_distance === "N/A" ? "text-gray-500 font-mono font-bold" : "text-red-400 font-mono font-bold text-sm"}>
                  {telemetry.predator_distance}
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  )
}

export default Playground
