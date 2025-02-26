import React, { useState } from "react";
import logo from "../statics/sorter.png";
import User_apiUrl from "./apiConfig";

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const requestBody = {
      username: username,
      password: password,
    };

    try {
      const response = await fetch(`${User_apiUrl}/auth/jwt/create/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const data = await response.json();

        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);

        // Add the code to test the tokens here
        const verifyResponse = await fetch(
          `${User_apiUrl}/auth/jwt/verify/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `JWT ${data.access}`,
            },
            body: JSON.stringify({ token: data.access }),
          }
        );

        if (verifyResponse.ok) {
          onLogin(data.access);
        } else {
          setErrorMessage("Error verifying access token:");
          setTimeout(() => {
            setErrorMessage("");
          }, 5000);
        }
      } else {
        console.error("Error:", response.status);
        setErrorMessage("Login failed. Please check your credentials.");
        setTimeout(() => {
          setErrorMessage("");
        }, 5000);
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("An unexpected error occurred.");
      setTimeout(() => {
        setErrorMessage("");
      }, 5000);
    }
  };

  return (
    <div className="container mt-5">
      {errorMessage && (
        <div className="alert alert-danger" role="alert">
          {errorMessage}
        </div>
      )}
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <img src={logo} alt="Logo" className="img-fluid mb-3" />
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="username">Username:</label>
                  <input
                    type="text"
                    className="form-control"
                    id="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="password">Password:</label>
                  <input
                    type="password"
                    className="form-control"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <button type="submit" className="btn btn-primary">
                  Login
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
