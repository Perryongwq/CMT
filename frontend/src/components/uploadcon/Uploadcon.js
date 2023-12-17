import React, { useState , useRef, useEffect } from 'react';



const Uploadcon = () => {
    // store uploaded files 
    const [trainingDataset, setTrainingDataset] = useState(null);
    const [validationDataset, setValidationDataset] = useState(null);
    const [message, setMessage] = useState('');

    const trainingFileRef = useRef();    
    const validationFileRef = useRef();
    

    // store uploaded files info
    const [train, setDataset] = useState(null);
    const [validation, setValidation] = useState(null);
    const [loading, setLoading] = useState(false);

    const [datasetInfo, setDatasetInfo] = useState({
        train_dataset: { g_count: 0, ng_count: 0, slide_count: 0 },
        validation_dataset: { val_g_count: 0, val_ng_count: 0, val_slide_count: 0 }
    });

    

    // handle file upload and check the file types and update the appropriate state variables

    const handleDatasetUpload = (event, datasetType) => {
        const file = event.target.files[0];
        if (file.type !== 'application/zip' && file.type !== 'application/x-zip-compressed') {
            setMessage('Invalid File Type! Please upload a zip file.');
            return;
        }

        if (datasetType === 'training') {
            setTrainingDataset(file);
        } else if (datasetType === 'validation') {
            setValidationDataset(file);
        }
    };

    // handle form submit and send the files to the backend
    // Create a new FormData object with uploaded file and send a POST request to the server        

    const handleSubmit = async () => {
        if (!trainingDataset || !validationDataset) {
            setMessage('Please upload both training and validation datasets!');
            return;
        }

        let formData = new FormData();
        formData.append('dataset', trainingDataset); // Changed key to 'dataset'
        formData.append('validation', validationDataset); // Changed key to 'validation'

        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Response:', data);
                setMessage('Datasets Upload successful!');

                const { dataset, validation, dataset_info } = data;

                setDataset(dataset);
                setValidation(validation); // Corrected state setter function
                setDatasetInfo(dataset_info);  
                setLoading(false); 

            } else {
                console.log('Error', response.statusText);
                setMessage('Error uploading datasets!');
            setLoading(false);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessage('Error uploading datasets!');
            setLoading(false);
        }

      
    };

    // handle reset and clear all the state variables

    const handleReset = () => {
        setTrainingDataset(null);
        setValidationDataset(null);
        setLoading(false);
        setDataset(null);
        setValidation(null);
        setMessage('');
        setDatasetInfo({
            train_dataset: { g_count: 0, ng_count: 0, slide_count: 0 },
            validation_dataset: { val_g_count: 0, val_ng_count: 0, val_slide_count: 0 }
        
        });
        if (trainingFileRef.current) {
            trainingFileRef.current.value = '';
        }
        if (validationFileRef.current) {
            validationFileRef.current.value = '';
        }
    }
    
    useEffect(() => {
        let alertMessage = '';

        if (message) {
            alertMessage += `Message: ${message}\n`;
        }
        if (train) {
            alertMessage += `Train: ${JSON.stringify(train)}\n`
        }
        if (validation) {
            alertMessage += `Validation:${JSON.stringify(validation)}\n`;
        }
        if (alertMessage) {
            alert(alertMessage);
        }
    }, [message, train, validation]);

    return (
        <div className='relative'>
        <h1 className='text-xl font-bold mb-1'>Upload Training and Validation Datasets</h1>
        <div className='flex'>
            <div className ='bg-gray-100 p-1 rounded shadow-md' style={{width: '20%'}}>
                <h3 className ="text-m font-semibold mb-1">Training </h3>
                <input type="file" accept=".zip" ref={trainingFileRef} onChange={(event) => handleDatasetUpload(event, 'training')} />
            </div>
            <div className='bg-gray-100 p-1 rounded shadow-md' style={{width: '20%'}}>
                <h3 className ="text-m font-semibold mb-1">Validation </h3>
                <input type="file" accept=".zip" ref={validationFileRef} onChange={(event) => handleDatasetUpload(event, 'validation')} />
            </div>        
            <div className=' flex flex-col justify-center ml-2'>
            <button onClick={handleSubmit} className="bg-blue-500 text-white p-1 rounded mt-4">Upload</button>
            <button onClick={handleReset} className="bg-red-500 text-white p-1 rounded mt-4 ml-2">Reset</button>
            </div>
        </div>
        {loading && (
            <div className="flex justify-center items-center absolute top-0 left-0 w-full h-full bg-opacity-50">
                <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
                <p className="absolute">Loading..</p>
            </div>
        )}
            {datasetInfo && (
                <div className='bg-gray-100 p-rounded shadow-md mt-2' style={{width: '40%'}}>
                    <h2 className='text-m font-bold mb-1'>Dataset Info:</h2>
                    <table>
                        <thead>
                            <tr>
                                <th></th>
                                <th className='border px-2'>G Count</th>
                                <th className='border px-2'>NG Count</th>
                                <th className='border px-2'>Slide Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td className='border px-2'>Training</td>
                                <td className='border px-2'>{datasetInfo.train_dataset.g_count}</td>
                                <td className='border px-2'>{datasetInfo.train_dataset.ng_count}</td>
                                <td className='border px-2'>{datasetInfo.train_dataset.slide_count}</td>
                            </tr>
                            <tr>
                                <td className='border px-2'>Validation </td>
                                <td className='border px-2'>{datasetInfo.validation_dataset.val_g_count}</td>
                                <td className='border px-2'>{datasetInfo.validation_dataset.val_ng_count}</td>
                                <td className='border px-2'>{datasetInfo.validation_dataset.val_slide_count}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            )}
        
    </div>
    );
}
export default Uploadcon;