import React from 'react';
import Uploadcon from './components/uploadcon/Uploadcon';
import WebSocketChart from './components/chart/WebSocketChart';
import './index.css';

const App = () => {
    return (
        <div className="App">
            <Uploadcon />
            <WebSocketChart />
        </div>
    );
};
export default App;
