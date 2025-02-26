import React, { useState } from 'react';
import SoundConfigComponent from "../components/SoundConfigComponent";
import ModalComponent from "../components/ModalComponent";

const SoundPage = () => {
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMessage, setModalMessage] = useState('');
    const [isPageFrozen, setPageFrozen] = useState(false); // State to control freezing of the page

    const toggleModal = (message) => {
        setModalMessage(message);
        setModalOpen(true);
        setTimeout(() => {
            setModalOpen(false);
        }, 2000);
    };

    const togglePageFreeze = (freeze) => {
        setPageFrozen(freeze);
    };
    const overlayStyle = {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.5)', // Semi-transparent black
        zIndex: 1000, // Ensure it appears above other content
        display: isPageFrozen ? 'block' : 'none' // Conditionally display the overlay
    };

    return (
        <div className="container mt-5">
            <div style={overlayStyle}></div>
            <h1 className="text-center mb-4">Config sound sensor page</h1>
            <SoundConfigComponent toggleModal={toggleModal} togglePageFreeze={togglePageFreeze} /> {/* Pass togglePageFreeze as prop */}
            <ModalComponent isOpen={modalOpen} message={modalMessage} toggle={() => setModalOpen(!modalOpen)} /> {/* Integrate CustomModal */}

        </div>
    );
};

export default SoundPage;
