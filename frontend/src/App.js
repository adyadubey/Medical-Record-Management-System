import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const Sidebar = ({ setActiveView }) => {
    const views = [
        { key: 'patients', label: 'GET /patients' },
        { key: 'patient_by_id', label: 'GET /patient/{id}' },
        { key: 'semantic_search', label: 'POST /search' },
        { key: 'appointment_info', label: 'GET /appointment_info/{id}' },
        { key: 'create_patient', label: 'POST /create_patient' },
        { key: 'update_patient', label: 'PUT /update_patient/{id}' },
    ];

    return (
        <div className="w-64 min-h-screen bg-gradient-to-b from-gray-800 to-gray-900 text-white p-4 space-y-4 shadow-lg">
            <h1 className="text-xl font-bold mb-6">API Dashboard</h1>
            {views.map((view) => (
                <button
                    key={view.key}
                    onClick={() => setActiveView(view.key)}
                    className="block w-full text-left px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition duration-200"
                >
                    {view.label}
                </button>
            ))}
        </div>
    );
};

const PatientFormModal = ({ isOpen, onClose, onSubmit, initialData = {}, isUpdate }) => {
    const [formData, setFormData] = useState({
        name: initialData.name || '',
        gender: initialData.gender || '',
        height_cm: initialData.height_cm || '',
        weight_kg: initialData.weight_kg || '',
        medical_history: initialData.medical_history || '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = () => {
        onSubmit(formData);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
                <h2 className="text-xl font-bold mb-4">{isUpdate ? 'Update Patient' : 'Create Patient'}</h2>
                <div className="grid gap-4">
                    {['name', 'gender', 'height_cm', 'weight_kg', 'medical_history'].map((field) => (
                        <input
                            key={field}
                            name={field}
                            placeholder={field.replace(/_/g, ' ')}
                            value={formData[field]}
                            onChange={handleChange}
                            className="p-2 border border-gray-300 rounded"
                        />
                    ))}
                </div>
                <div className="flex justify-end mt-4 space-x-4">
                    <button onClick={onClose} className="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
                    <button onClick={handleSubmit} className="bg-blue-600 text-white px-4 py-2 rounded">
                        {isUpdate ? 'Update' : 'Create'}
                    </button>
                </div>
            </div>
        </div>
    );
};

const Table = ({ data }) => {
    if (!Array.isArray(data)) data = [data];

    if (!data || data.length === 0 || typeof data[0] !== 'object') return <p>No data available.</p>;

    const headers = Object.keys(data[0]);

    return (
        <div className="overflow-x-auto mt-4 rounded shadow">
            <table className="min-w-full bg-white">
                <thead className="bg-gray-200">
                    <tr>
                        {headers.map((header) => (
                            <th key={header} className="text-left py-2 px-4 border-b">{header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, i) => (
                        <tr key={i} className="hover:bg-gray-100">
                            {headers.map((header) => (
                                <td key={header} className="py-2 px-4 border-b">
                                    {typeof row[header] === 'object'
                                        ? JSON.stringify(row[header])
                                        : row[header]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

function App() {
    const [activeView, setActiveView] = useState('patients');
    const [data, setData] = useState(null);
    const [idInput, setIdInput] = useState('');
    const [searchInput, setSearchInput] = useState('');
    const [showFormModal, setShowFormModal] = useState(false);
    const [formMode, setFormMode] = useState('create');
    const [formInitialData, setFormInitialData] = useState({});

    useEffect(() => {
        const fetchData = async () => {
            try {
                let url = '';
                switch (activeView) {
                    case 'patients':
                        url = `${API_BASE_URL}/patients`;
                        break;
                    case 'patient_by_id':
                        url = `${API_BASE_URL}/patient/${idInput}`;
                        break;
                    case 'appointment_info':
                        url = `${API_BASE_URL}/appointment_info/${idInput}`;
                        break;
                    default:
                        return;
                }

                const response = await fetch(url);
                const result = await response.json();
                setData(result);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        if (['patients', 'patient_by_id', 'appointment_info'].includes(activeView)) {
            fetchData();
        }
    }, [activeView, idInput]);

    useEffect(() => {
        if (activeView === 'create_patient' || activeView === 'update_patient') {
            setShowFormModal(true);
            setFormMode(activeView === 'create_patient' ? 'create' : 'update');
        }
    }, [activeView]);

    const handleSearchSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${API_BASE_URL}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: searchInput })
            });
            const result = await response.json();
            setData(result);
        } catch (error) {
            console.error("Search error:", error);
        }
    };

    const createPatient = async (payload) => {
        try {
            const res = await fetch(`${API_BASE_URL}/create_patient`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            return await res.json();
        } catch (error) {
            console.error("Create error:", error);
        }
    };

    const updatePatient = async (id, payload) => {
        try {
            const res = await fetch(`${API_BASE_URL}/update_patient/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            return await res.json();
        } catch (error) {
            console.error("Update error:", error);
        }
    };

    const handleFormSubmit = async (formData) => {
        if (formMode === 'create') {
            await createPatient(formData);
        } else if (formMode === 'update') {
            const id = prompt("Enter the ID of the patient to update:");
            if (!id) return;
            await updatePatient(id, formData);
        }
        const updated = await fetch(`${API_BASE_URL}/patients`).then(res => res.json());
        setData(updated);
    };

    return (
        <div className="flex min-h-screen">
            <Sidebar setActiveView={setActiveView} />
            <div className="flex-1 p-6 bg-gray-100 relative">
                {/* Logo */}
                <img
                    src="/logo.png"
                    alt="Logo"
                    className="absolute top-4 right-6 w-20 h-auto"
                />

                <h2 className="text-2xl font-semibold mb-6">{activeView.replace(/_/g, ' ').toUpperCase()}</h2>

                {(activeView === 'patient_by_id' || activeView === 'appointment_info') && (
                    <input
                        className="mb-4 p-2 border border-gray-400 rounded w-64"
                        placeholder="Enter ID"
                        value={idInput}
                        onChange={(e) => setIdInput(e.target.value)}
                    />
                )}

                {activeView === 'semantic_search' && (
                    <form onSubmit={handleSearchSubmit} className="mb-4">
                        <input
                            className="p-2 border border-gray-400 rounded w-64 mr-2"
                            placeholder="Enter search query"
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                        />
                        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
                            Search
                        </button>
                    </form>
                )}

                <div className="bg-white p-4 rounded shadow overflow-auto">
                    {data ? <Table data={data} /> : <p className="text-gray-600">No data to display</p>}
                </div>

                {showFormModal && (
                    <PatientFormModal
                        isOpen={showFormModal}
                        onClose={() => {
                            setShowFormModal(false);
                            setActiveView('patients');
                        }}
                        onSubmit={handleFormSubmit}
                        initialData={formInitialData}
                        isUpdate={formMode === 'update'}
                    />
                )}
            </div>
        </div>
    );
}

export default App;
