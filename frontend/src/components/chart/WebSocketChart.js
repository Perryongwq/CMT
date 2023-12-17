import React, { useState, useEffect, useRef } from 'react';
import { Chart, LineController, LinearScale, CategoryScale, PointElement, LineElement } from 'chart.js';
import Input from '../common/Input';

Chart.register(LineController, LinearScale, CategoryScale, PointElement, LineElement);

const WebSocketChart = () => {
    const [socket, setSocket] = useState(null);
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    const [epochs, setEpochs] = useState('');
    const [datasetDir, setDatasetDir] = useState('');
    const [validationDir, setValidationDir] = useState('');


    useEffect(() => {
        const newSocket = new WebSocket('ws://localhost:8000/ws');
        setSocket(newSocket);

        newSocket.addEventListener('open', () => {
            console.log('WebSocket is open now.');
            initializeChart();
        });

        newSocket.addEventListener('close', () => {
            console.log('WebSocket is closed now.');
        });

        newSocket.addEventListener('error', (event) => {
            console.log('WebSocket error: ', event);
        });

        newSocket.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);
            console.log('Received message:', event.data);
            handleSocketData(data);
        });

        return () => {
            newSocket.close();
        };
    }, []);



    const initializeChart = () => {
        const ctx = chartRef.current.getContext('2d');
        if (chartInstance.current) {
            chartInstance.current.destroy();
        }
        
        chartInstance.current = new Chart(ctx,{
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Training Loss',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: [],
                    fill: false,
                }, {
                    label: 'Validation Loss',
                    backgroundColor: 'rgb(54, 162, 235)',
                    borderColor: 'rgb(54, 162, 235)',
                    data: [],
                    fill: false,
                }, {
                    label: 'Training Accuracy',
                    backgroundColor: 'rgb(75, 192, 192)',
                    borderColor: 'rgb(75, 192, 192)',
                    data: [],
                    fill: false,
                }, {
                    label: 'Validation Accuracy',
                    backgroundColor: 'rgb(153, 102, 235)',
                    borderColor: 'rgb(153, 102, 235)',
                    data: [],
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Training and Validation Loss and Accuracy'
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Epoch'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Metrics'
                        },
                        id: 'y-axis-metrics',
                        type: 'linear',
                        position: 'left',
                        ticks: {
                            beginAtZero: true, // This ensures that the scale starts at 0
                            callback: function(value) {
                                return value + '%';
                            },
                            min: 0,
                            max: 100
                        }
                    }]
                }
            }
        });
    };

    const handleSocketData = (data) => {

        if (data.status === 'epoch_end') {
            updateGraph(data.epoch, data.loss, data.val_loss, data.accuracy, data.val_accuracy);
        }
    };

    const updateGraph = (epoch, trainingLoss, validationLoss, trainingAccuracy, validationAccuracy) => {
        if (!chartInstance.current) return;

        chartInstance.current.data.labels.push(`Epoch ${epoch + 1}`);
        chartInstance.current.data.datasets[0].data.push(trainingLoss);
        chartInstance.current.data.datasets[1].data.push(validationLoss);
        chartInstance.current.data.datasets[2].data.push(trainingAccuracy);
        chartInstance.current.data.datasets[3].data.push(validationAccuracy);
        chartInstance.current.update();
    };

    const startTraining = () => {
        if (!epochs || epochs <= 0) {
            alert('Please enter a valid number of epochs.');
            return;
        }
    
        if (!datasetDir || !validationDir) {
            alert('Please enter both dataset and validation directory paths.');
            return;
        }
    
        const trainingData = {
            epochs: epochs,
            dataset_dir: datasetDir,
            validation_dir: validationDir
        };
    
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(trainingData));  // Send the training data to the server
        } else {
            alert('The socket is not open.');
        }
    };

    const handleEpochsChange = (event) => {
        setEpochs(event.target.value);
    };

    return (
        <div className='bg-gray-100 p-1 rounded shadow-md w-2/5 h-2/5'>
            <Input type="number" value={epochs} onChange={handleEpochsChange} name="epochsInput" />
            <canvas ref={chartRef}></canvas>
        </div>
    );
};

export default WebSocketChart;
