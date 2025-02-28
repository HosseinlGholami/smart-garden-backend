export const User_apiUrl = "http://172.30.33.136:5002/trf";

export const fetchDevices = async () => {
  try {
    const access_token = localStorage.getItem("access_token");
    const response = await fetch(`${User_apiUrl}/api/trf-device/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${access_token}`,
      },
    });
    if (response.ok) {
      return await response.json();
    } else {
      console.error("Failed to fetch devices");
      return [];
    }
  } catch (error) {
    console.error("Error fetching devices:", error);
    return [];
  }
};

export const fetchParamOptions = async (device_id) => {
  try {
    // Retrieve the access token from localStorage
    const access_token = localStorage.getItem("access_token");
    // Make the API request
    const response = await fetch(`${User_apiUrl}/api/trf-param/?device_id=${device_id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${access_token}`,
      },
    });
    console.log(response)
    // Check if the response is successful
    if (response.ok) {
      // Parse and return the JSON data
      const data = await response.json();
      return data;
    } else {
      // Handle API errors
      const errorData = await response.json();
      console.error("Failed to fetch param options:", errorData);
      return [];
    }
  } catch (error) {
    // Handle network or other errors
    console.error("Error fetching param options:", error);
    return [];
  }
};


// commandTypes.js
export const CommandType = {
  UPLINK_HEARTBEAT_PACKET: 0,
  UPLINK_PING_PONG_PACKET: 1,
  UPLINK_REPORT_PACKET: 2,
  UPLINK_COMMAND_PACKET: 3,
  UPLINK_GET_PARAM_PACKET: 4,
  UPLINK_SET_PARAM_PACKET: 5,
};

export const sendCommand = async (deviceId, commandType, addressId, value) => {
  try {
    const access_token = localStorage.getItem("access_token");
    const response = await fetch(`${User_apiUrl}/api/trf-cmd/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${access_token}`,
      },
      body: JSON.stringify({
        device_id: deviceId,
        command_type: commandType,
        parameter_id: addressId,
        value: value,
      }),
    });

    if (response.ok) {
      return await response.json();
    } else {
      console.error(`Failed to send ${commandType} command`);
      return null;
    }
  } catch (error) {
    console.error(`Error sending ${commandType} command:`, error);
    return null;
  }
};