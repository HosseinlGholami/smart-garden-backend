import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CustomNavbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import LoginForm from "./components/LoginForm";
import User_apiUrl from "./components/apiConfig";
import SoundPage from "./pages/SoundPage";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const navItems = [
    { text: "Home", link: "/trf/", access: userData?.user_role?.home_access },
    {
      text: "Config",
      link: "/trf/config",
      access: userData?.user_role?.config_access,
    },
    {
      text: "Analytics",
      link: "https://robotics.digikala.com/dashboard/d/c0620a83-38ca-4d65-9654-52908028e96f/nd-panel?orgId=1&refresh=5s",
      access: true,
    },
  ];

  // Filter navItems based on access permissions
  const filteredNavItems = navItems.filter((item) =>
    item.access !== undefined ? item.access : true
  );

  const generateRoutes = () => {
    if (!userData || !userData.user_role) {
      return null;
    }

    // Create an array of route objects based on user access permissions
    const routes = [
      // Map additional routes based on user access permissions
      ...(userData.user_role.home_access
        ? [{ path: "/trf/", element: <HomePage /> }]
        : []),
      ...(userData.user_role.home_access
        ? [{ path: "/trf/config", element: <SoundPage /> }]
        : []),
    ];

    return routes.map((route, index) => (
      <Route key={index} path={route.path} element={route.element} />
    ));
  };

  useEffect(() => {
    const verifyAccessToken = async (access_token) => {
      try {
        const verifyResponse = await fetch(
          `${User_apiUrl}/auth/jwt/verify/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ token: access_token }),
          }
        );

        if (verifyResponse.ok) {
          const userDataResponse = await fetch(
            `${User_apiUrl}/auth/users/me/`,
            {
              headers: {
                Authorization: `JWT ${access_token}`,
              },
            }
          );

          if (userDataResponse.ok) {
            const userData = await userDataResponse.json();
            setUserData(userData); // Set user data
            setIsLoggedIn(true);
          } else {
            console.error("Error fetching user data:", userDataResponse.status);
            refreshAccessToken();
          }
        } else {
          refreshAccessToken();
        }
      } catch (error) {
        console.error("Error verifying access token:", error);
      } finally {
        setIsLoading(false);
      }
    };

    const refreshAccessToken = async () => {
      try {
        const refresh_token = localStorage.getItem("refresh_token");
        const response = await fetch(
          `${User_apiUrl}/auth/jwt/refresh/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ refresh: refresh_token }),
          }
        );

        if (response.ok) {
          const data = await response.json();
          localStorage.setItem("access_token", data.access);
          setIsLoggedIn(true);
        } else {
          console.error("Error refreshing access token:", response.status);
          // Handle refresh token error if needed
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      } catch (error) {
        console.error("Error refreshing access token:", error);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }
    };

    const access_token = localStorage.getItem("access_token");
    if (access_token) {
      setIsLoading(true);
      verifyAccessToken(access_token);
    }
  }, []); // Include verifyAccessToken in the dependency array

  const handleLogin = async (access_token) => {
    const userDataResponse = await fetch(
      `${User_apiUrl}/auth/users/me/`,
      {
        headers: {
          Authorization: `JWT ` + access_token,
        },
      }
    );
    if (userDataResponse.ok) {
      const userData = await userDataResponse.json();
      setUserData(userData); // Set user data
      setIsLoggedIn(true);
    } else {
      console.error("Error on fetching user - you cannot login");
    }
  };

  return (
    <Router>
      {isLoading ? (
        // Show a nice loading indicator while verifying the token
        <div className="d-flex align-items-center justify-content-center vh-100">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : isLoggedIn ? (
        // If logged in, render the main content
        <div>
          <div className="d-flex">
            <CustomNavbar userData={userData} navItems={filteredNavItems} />
          </div>
          <div className="page-content-wrapper">
            <Routes>{generateRoutes()}</Routes>
          </div>
        </div>
      ) : (
        // If not logged in, render the login form
        <LoginForm onLogin={handleLogin} />
      )}
    </Router>
  );
}

export default App;
