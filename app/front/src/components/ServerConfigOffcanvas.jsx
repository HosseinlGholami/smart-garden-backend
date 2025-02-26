// ServerConfigOffcanvas.js
import React from "react";

const ServerConfigOffcanvas = ({
  isOpen,
  responseData,
  setIsOffcanvasOpen,
}) => {
  const handleClose = () => {
    setIsOffcanvasOpen(false);
  };

  return (
    <div
      className={`offcanvas offcanvas-bottom ${isOpen ? "show" : ""}`}
      tabIndex="-1"
      id="offcanvasBottom"
      aria-labelledby="offcanvasBottomLabel">
      <div className="offcanvas-header">
        <h5 className="offcanvas-title" id="offcanvasBottomLabel">
          Server Config
        </h5>
        <button
          type="button"
          className="btn-close text-reset"
          data-bs-dismiss="offcanvas"
          aria-label="Close"
          onClick={handleClose}></button>
      </div>
      <div className="offcanvas-body small">
        {responseData && responseData.projects ? (
          <div>
            {responseData.projects.map((project, index) => (
              <div key={index} className="card mb-3">
                <div className="card-body">
                  <h5 className="card-title">
                    Version: {project.project_version}
                  </h5>
                  <p className="card-text">
                    Event Task Status: {project.event_task_status}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No server config data available.</p>
        )}
      </div>
    </div>
  );
};

export default ServerConfigOffcanvas;
