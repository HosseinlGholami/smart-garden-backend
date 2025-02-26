import React, { useState, useEffect } from "react";
import {
  Button,
  Col,
  Container,
  Form,
  FormGroup,
  Row,
  ProgressBar,
} from "react-bootstrap";
import User_apiUrl from "./apiConfig";

const SoundConfigComponent = ({ toggleModal, togglePageFreeze }) => {
  const [soundDevices, setSoundDevices] = useState([]);
  const [selectedDevices, setSelectedDevices] = useState([]);
  const [paramOptions, setParamOptions] = useState([]);
  const [selectedParam, setSelectedParam] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [progress, setProgress] = useState(0); // Progress tracking
  const [apiResults, setApiResults] = useState([]);

  useEffect(() => {
    const fetchSoundDevices = async () => {
      try {
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(
          `${User_apiUrl}/api/sound-device/`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `JWT ${access_token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setSoundDevices(data);
        } else {
          console.error("Failed to fetch sound devices");
        }
      } catch (error) {
        console.error("Error fetching sound devices:", error);
      }
    };

    fetchSoundDevices();
  }, []);

  const fetchParamOptions = async () => {
    try {
      const access_token = localStorage.getItem("access_token");
      const response = await fetch(`${User_apiUrl}/api/sound-param/`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `JWT ${access_token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setParamOptions(data);
      } else {
        console.error("Failed to fetch param options");
      }
    } catch (error) {
      console.error("Error fetching param options:", error);
    }
  };

  useEffect(() => {
    // Fetch parameter options when at least one device is selected
    if (selectedDevices.length > 0) {
      fetchParamOptions();
    } else {
      setParamOptions([]); // Reset if no devices are selected
    }
  }, [selectedDevices]);

  const handleDeviceChange = (event) => {
    const value = event.target.value;
    setSelectedDevices(
      (prevState) =>
        prevState.includes(value)
          ? prevState.filter((device) => device !== value) // Remove if unchecked
          : [...prevState, value] // Add if checked
    );
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      // Select all devices
      const allDeviceIds = soundDevices.map((device) => device.device_id);
      setSelectedDevices(allDeviceIds);
    } else {
      // Deselect all devices
      setSelectedDevices([]);
    }
  };

  const handleParamChange = (event) => {
    setSelectedParam(event.target.value);
  };

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = async (commandType) => {
    if (selectedDevices.length && selectedParam) {
      setApiResults([]);
      let results = [];
      setProgress(0);

      for (let i = 0; i < selectedDevices.length; i++) {
        const deviceId = selectedDevices[i];
        try {
          togglePageFreeze(true);
          const access_token = localStorage.getItem("access_token");
          const response = await fetch(`${User_apiUrl}/api/sound-cmd/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `JWT ${access_token}`,
            },
            body: JSON.stringify({
              device_id: deviceId,
              parameter_id: selectedParam,
              value: commandType === "SET" ? inputValue : "0",
              command_type: commandType,
            }),
          });

          if (response.ok) {
            const data = await response.json();
            // Extract the id and value_start for display
            if (data && data.result) {
              const detail_res = data.result.replace(/'/g, '"');
              const parsedObj = JSON.parse(detail_res);
              results.push({
                id: deviceId,
                value_start: parsedObj.value_start,
              });
            }
          } else {
            console.error(`Failed to send ${commandType} command`);
            results.push({
              id: deviceId,
              error: `Failed to send ${commandType} command`,
            });
          }
        } catch (error) {
          console.error(`Error sending ${commandType} command:`, error);
          results.push({
            id: deviceId,
            error: `Error sending ${commandType} command: ${error}`,
          });
        } finally {
          setProgress(((i + 1) / selectedDevices.length) * 100);
        }
      }

      setApiResults(results);
      togglePageFreeze(false);
    } else {
      toggleModal("Select devices and parameter properly");
    }
  };

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={10}>
          <Form>
            {/* Device Selection */}
            <FormGroup>
              <Form.Label>Select Sound Device(s)</Form.Label>
              {/* Select All Checkbox */}
              <Form.Check
                type="checkbox"
                label="Select All"
                checked={selectedDevices.length === soundDevices.length}
                onChange={handleSelectAll}
              />
              <Row>
                {soundDevices.map((device) => (
                  <Col key={device.device_id} md={2}>
                    {" "}
                    {/* 5-column grid */}
                    <Form.Check
                      type="checkbox"
                      label={`${device.floor}-${device.section} (${device.device_id})`}
                      value={device.device_id}
                      checked={selectedDevices.includes(device.device_id)}
                      onChange={handleDeviceChange}
                    />
                  </Col>
                ))}
              </Row>
            </FormGroup>
          </Form>
        </Col>

        <Col md={8}>
          <div className="my-4">
            <Form>
              <FormGroup>
                <Form.Label>Select Parameter</Form.Label>
                <Form.Select
                  value={selectedParam}
                  onChange={handleParamChange}
                  disabled={!selectedDevices.length}
                >
                  <option value="">Select Parameter</option>
                  {paramOptions.map((param) => (
                    <option key={param.param_id} value={param.param_id}>
                      {param.param_name}
                    </option>
                  ))}
                </Form.Select>
              </FormGroup>

              <FormGroup>
                <Form.Label>Enter Value</Form.Label>
                <Form.Control
                  type="text"
                  value={inputValue}
                  onChange={handleInputChange}
                  disabled={!selectedParam}
                />
              </FormGroup>

              <div className="my-4">
                <ProgressBar
                  animated
                  now={progress}
                  label={`${Math.round(progress)}%`}
                />
              </div>

              <div className="text-center mt-3">
                <Button
                  variant="primary"
                  onClick={() => handleSubmit("SET")}
                  disabled={!selectedParam}
                >
                  SetParam
                </Button>
                <Button
                  variant="primary"
                  className="ms-3"
                  onClick={() => handleSubmit("GET")}
                  disabled={!selectedParam}
                >
                  GetParam
                </Button>
              </div>
            </Form>
          </div>

          {apiResults.length > 0 && (
            <div className="mt-5">
              <h3>Results</h3>
              <ul className="list-group">
                {apiResults.map((result, index) => (
                  <li key={index} className="list-group-item">
                    {result.id ? (
                      <>
                        <strong>Device ID:</strong> {result.id} <br />
                        <strong>Value Start:</strong>{" "}
                        {result.value_start ? result.value_start : "N/A"}
                      </>
                    ) : (
                      <>
                        <strong>Error:</strong> {result.error}
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default SoundConfigComponent;
