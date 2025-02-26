import React, { useState, useEffect } from 'react';
import { Button, Col, Container, Form, FormGroup, Input, Label, Row } from 'reactstrap';
import User_apiUrl from "../components/apiConfig";

const ConfigComponent = ({ toggleModal, togglePageFreeze }) => {
  const [options, setOptions] = useState([]);
  const [selectedSorterOption, setselectedSorterOption] = useState('');
  const [showRadioButtons, setShowRadioButtons] = useState(false);
  const [selectedDeviceRadio, setselectedDeviceRadio] = useState('');
  const [showInputBox, setShowInputBox] = useState(false);
  const [selectedParamID, setselectedParamID] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [ControllerParamOptions, setControllerParamOptions] = useState([]);
  const [DCParamOptions, setDCParamOptions] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(`${User_apiUrl}/api/home/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${access_token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setOptions(data.packages);
        } else {
          console.error('Failed to fetch data');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);


  useEffect(() => {
    const fetchControllerParamOptions = async () => {

      try {
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(`${User_apiUrl}/api/ctrl-parameters/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${access_token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          // console.log(data)
          setControllerParamOptions(data);
        } else {
          console.error('Failed to fetch param options');
        }
      } catch (error) {
        console.error('Error fetching param options:', error);
      }
    };

    const fetchDcParamOptions = async () => {
      try {
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(`${User_apiUrl}/api/dc-parameters/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${access_token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          // console.log(data)
          setDCParamOptions(data);
        } else {
          console.error('Failed to fetch param options');
        }
      } catch (error) {
        console.error('Error fetching param options:', error);
      }
    };

    fetchDcParamOptions();
    fetchControllerParamOptions();
  }, []);


  const handleOptionChange = (event) => {
    setselectedSorterOption(event.target.value);
    if (event.target.value !== '') {
      setShowRadioButtons(true);
    } else {
      setShowRadioButtons(false);
      setShowInputBox(false);
      setselectedDeviceRadio('')
    }
  };

  const handleRadioChange = (event) => {
    setselectedDeviceRadio(event.target.value);
    setInputValue("");
    setShowInputBox(true);
  };

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleParamIdChange = (event) => {
    setselectedParamID(event.target.value);
  };

  const handleSendGetParam = async () => {
    if (selectedSorterOption !== "" && selectedDeviceRadio !== "" && selectedParamID !== "") {
      try {
        togglePageFreeze(true)
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(`${User_apiUrl}/api/user-config/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${access_token}`,
          },
          body: JSON.stringify({
            "sorter_pigeon": selectedSorterOption,
            "device_name": selectedDeviceRadio,
            "parameter_id": selectedParamID,
            "value": "0",
            "command_type": "GET",
          }),
        });

        if (response.ok) {
          // Handle successful response
          const data = await response.json();
          console.log(data);
          toggleModal(data.result);
        } else {
          console.error('Failed to send get param');
          toggleModal('Failed to send get param');
        }
      } catch (error) {
        console.error('Error sending set param:', error);
        toggleModal('Error sending set param:', error);
      } finally {
        togglePageFreeze(false)
      }

    } else {
      toggleModal('Fill the value properly');
    }
  };

  const handleSendSetParam = async () => {
    if (selectedSorterOption !== "" && selectedDeviceRadio !== "" && selectedParamID !== "" && inputValue !== "") {
      console.log(selectedSorterOption)
      try {
        togglePageFreeze(true)
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(`${User_apiUrl}/api/user-config/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${access_token}`,
          },
          body: JSON.stringify({
            "sorter_pigeon": selectedSorterOption,
            "device_name": selectedDeviceRadio,
            "parameter_id": selectedParamID,
            "value": inputValue,
            "command_type": "SET",
          }),
        });

        if (response.ok) {
          // Handle successful response
          const data = await response.json();
          console.log(data);
          toggleModal(data.result);
        } else {
          console.error('Failed to send set param');
          toggleModal('Failed to send set param');
        }
      } catch (error) {
        console.error('Error sending set param:', error);
        toggleModal('Error sending set param:', error);
      } finally {
        togglePageFreeze(false)
      }
    } else {
      toggleModal('Fill the value properly');
    }
  };

  const handleRestoreDefaults = async () => {
    if (selectedSorterOption !== "" && selectedDeviceRadio !== "" && selectedParamID !== "") {
      console.log(selectedSorterOption)
      try {
        togglePageFreeze(true)
        const access_token = localStorage.getItem("access_token");
        const response = await fetch(`${User_apiUrl}/api/user-config/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${access_token}`,
          },
          body: JSON.stringify({
            "sorter_pigeon": selectedSorterOption,
            "device_name": selectedDeviceRadio,
            "parameter_id": selectedParamID,
            "value": "0",
            "command_type": "DEF",
          }),
        });

        if (response.ok) {
          // Handle successful response
          const data = await response.json();
          console.log(data);
          toggleModal(data.result);
        } else {
          console.error('Failed to send set param');
          toggleModal('Failed to send set param');
        }
      } catch (error) {
        console.error('Error sending set param:', error);
        toggleModal('Error sending set param:', error);
      } finally {
        togglePageFreeze(false)
      }
    } else {
      toggleModal('Fill the value properly');
    }
  };

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={6}>
          <Form>
            <FormGroup>
              <Label for="wheelSorterSelect">Select The WheelSorter</Label>
              <Input type="select" id="wheelSorterSelect" value={selectedSorterOption} onChange={handleOptionChange}>
                <option value="">Select The WheelSorter</option>
                {options.map((option, index) => (
                  <option key={index} value={option.pigeon}>{option.pigeon}</option>
                ))}
              </Input>
            </FormGroup>

            {showRadioButtons && (
              <FormGroup>
                <Label>Choose Device</Label>
                <FormGroup check>
                  <Label check>
                    <Input type="radio" name="device" value="controller" checked={selectedDeviceRadio === 'controller'} onChange={handleRadioChange} />{' '}
                    Controller
                  </Label>
                </FormGroup>
                <FormGroup check>
                  <Label check>
                    <Input type="radio" name="device" value="dc1" checked={selectedDeviceRadio === 'dc1'} onChange={handleRadioChange} />{' '}
                    DC Driver 1
                  </Label>
                </FormGroup>
                <FormGroup check>
                  <Label check>
                    <Input type="radio" name="device" value="dc2" checked={selectedDeviceRadio === 'dc2'} onChange={handleRadioChange} />{' '}
                    DC Driver 2
                  </Label>
                </FormGroup>
              </FormGroup>
            )}

            {showInputBox && (
              <FormGroup>
                <Label for="parameterSelect">Select Parameter</Label>
                <Input type="select" id="parameterSelect" value={selectedParamID} onChange={handleParamIdChange}>
                  <option value="">Select parameter</option>
                  {selectedDeviceRadio === 'controller' && ControllerParamOptions.map((option, index) => (
                    <option key={index} value={option.param_id}>{option.param_name}</option>
                  ))}
                  {selectedDeviceRadio === 'dc1' && DCParamOptions.map((option, index) => (
                    <option key={index} value={option.param_id}>{option.param_name}</option>
                  ))}
                  {selectedDeviceRadio === 'dc2' && DCParamOptions.map((option, index) => (
                    <option key={index} value={option.param_id}>{option.param_name}</option>
                  ))}
                </Input>
                {selectedParamID && (
                  <div>
                    {selectedDeviceRadio === 'controller' && (
                      <p>{DCParamOptions.find(option => option.param_id === parseInt(selectedParamID))?.detail}</p>
                    )}
                    {selectedDeviceRadio === 'dc1' && (
                      <p>{DCParamOptions.find(option => option.param_id === parseInt(selectedParamID))?.detail}</p>
                    )}
                    {selectedDeviceRadio === 'dc2' && (
                      <p>{DCParamOptions.find(option => option.param_id === parseInt(selectedParamID))?.detail}</p>
                    )}
                  </div>
                )}
                <Input type="text" value={inputValue} onChange={handleInputChange} placeholder="Enter some value" />
              </FormGroup>
            )}


            <div className="text-center">
              <Button color="primary" onClick={handleSendSetParam}>SetParam</Button>
              <Button color="primary" onClick={handleSendGetParam}>GetParam</Button>
              <Button color="secondary" onClick={handleRestoreDefaults}>Restore Defaults</Button>
            </div>
          </Form>
        </Col>
      </Row>
    </Container>
  );
};

export default ConfigComponent;
