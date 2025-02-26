import React, { useState, useEffect } from "react";
import User_apiUrl from "../components/apiConfig";
import F6 from "../statics/F6.png";
import F7 from "../statics/F7.png";
import F8 from "../statics/F8.png";
import F9 from "../statics/F9.png";
import F10 from "../statics/F10.png";

const HomePage = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFloor, setSelectedFloor] = useState(null); // State for selected floor

  useEffect(() => {
    // Fetch data from API
    const fetchData = async () => {
      try {
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(`${User_apiUrl}/api/sound-device/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${access_token}`,
          },
        });
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setDevices(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p className="text-center mt-5">Loading...</p>;
  if (error) return <p className="text-center mt-5 text-danger">Error: {error.message}</p>;

  // Group devices by floor
  const groupedDevices = devices.reduce((acc, device) => {
    (acc[device.floor] = acc[device.floor] || []).push(device);
    return acc;
  }, {});

  // Map of floor numbers to image URLs (replace with your actual URLs)
  const floorMaps = {
    "F6": F6,
    "F7": F7,
    "F8": F8,
    "F9": F9,
    "F10": F10,
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Floor Plans</h1>

      {/* Floor selection dropdown */}
      <div className="mb-4 text-center">
        <label htmlFor="floorSelect" className="form-label me-2">
          Select Floor:
        </label>
        <select
          id="floorSelect"
          className="form-select d-inline w-auto"
          value={selectedFloor || ""}
          onChange={(e) => setSelectedFloor(e.target.value)}
        >
          <option value="" disabled>
            -- Choose a Floor --
          </option>
          {Object.keys(groupedDevices).map((floor) => (
            <option key={floor} value={floor}>
              Floor {floor.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Display selected floor map */}
      {selectedFloor && floorMaps[selectedFloor] ? (
        <div className="text-center">
          <h2 className="mb-3">Floor {selectedFloor.slice(1)}</h2>
          <img
            src={floorMaps[selectedFloor]}
            alt={`Floor ${selectedFloor.slice(1)} Plan`}
            className="img-fluid"
          />
        </div>
      ) : (
        selectedFloor && (
          <p className="text-center text-danger">No plan available for this floor.</p>
        )
      )}
    </div>
  );
};

export default HomePage;