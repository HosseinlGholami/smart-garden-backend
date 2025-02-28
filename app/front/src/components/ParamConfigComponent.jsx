import React, { useState, useEffect } from "react";
import {
  Button,
  Col,
  Container,
  Form,
  Row,
} from "react-bootstrap";
import { fetchDevices, fetchParamOptions , sendCommand, CommandType} from "./apiConfig";

const ParamConfigComponent = ({ toggleModal, togglePageFreeze }) => {
  const [devices, setDevices] = useState({});
  const [selectedDevice, setSelectedDevice] = useState("");
  const [paramOptions, setParamOptions] = useState([]);
  const [selectedParam, setSelectedParam] = useState("");
  const [inputValue, setInputValue] = useState("");

  // Fetch devices on component mount
  useEffect(() => {
    const fetchData = async () => {
      const data = await fetchDevices();
      setDevices(data);
    };
    fetchData();
  }, []);

  // Fetch paramOptions when selectedDevice changes
  useEffect(() => {
    const fetchParams = async () => {
      if (selectedDevice) {
        try {
          const data = await fetchParamOptions(selectedDevice);
          setParamOptions(data);
        } catch (error) {
          console.error("Error fetching param options:", error);
          toggleModal("Failed to fetch parameter options");
        }
      } else {
        setParamOptions([]); // Reset paramOptions if no device is selected
      }
    };

    fetchParams();
  }, [selectedDevice, toggleModal]);

  const handleDeviceChange = (event) => {
    setSelectedDevice(event.target.value);
    setSelectedParam(""); // Reset selectedParam when device changes
  };

  const handleParamChange = (event) => {
    setSelectedParam(event.target.value);
  };

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = async (commandType) => {
    if (selectedDevice && selectedParam) {
      togglePageFreeze(true); // Freeze the page while processing
      try {
        const response = await sendCommand(
          selectedDevice,
          commandType,
          selectedParam,
          commandType === CommandType.UPLINK_SET_PARAM_PACKET ? inputValue : "0"
        );

        console.log("-----> ",response)

        if (response) {
          const result = response.result;
          toggleModal(`Result: ${result[1]}`);
        } else {
          toggleModal(`Error: Failed to send ${commandType} command`);
        }
      } catch (error) {
        console.log("-----> ",error.toString())
        toggleModal(`Error: ${error.toString()}`);
      } finally {
        togglePageFreeze(false); // Unfreeze the page
      }
    } else {
      toggleModal("Error: Please select a device and parameter properly");
    }
  };
  return (
    <Container>
      <Row>
        <Col>
          <h3>Select Device</h3>
          {Object.entries(devices).map(([key, value]) => (
            <Form.Check
              key={key}
              type="radio"
              label={`${value.section.join(", ")} (ID: ${key})`}
              value={key}
              onChange={handleDeviceChange}
              checked={selectedDevice === key}
            />
          ))}
        </Col>
      </Row>
      <Row>
        <Col>
          <h3>Select Parameter</h3>
          <Form.Select onChange={handleParamChange} value={selectedParam} disabled={!selectedDevice}>
            <option value="">Select Parameter</option>
            {paramOptions.map((param) => (
              <option key={param.param_id} value={param.param_id}>{param.param_name}</option>
            ))}
          </Form.Select>
        </Col>
      </Row>
      <Row>
        <Col>
          <h3>Enter Value</h3>
          <Form.Control type="text" value={inputValue} onChange={handleInputChange} disabled={!selectedParam} />
        </Col>
      </Row>
      <Row className="mt-3">
        <Col>
          <Button onClick={() => handleSubmit(CommandType.UPLINK_SET_PARAM_PACKET)} disabled={!selectedParam}>
            Set Param
          </Button>
          <Button onClick={() => handleSubmit(CommandType.UPLINK_GET_PARAM_PACKET)} disabled={!selectedParam} className="ms-3">
            Get Param
          </Button>
        </Col>
      </Row>
    </Container>
  );
};

export default ParamConfigComponent;