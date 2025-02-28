import React, { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CustomNavbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import ParamPage from "./pages/ParamPage";
import { useAuth } from "./components/OAuth/useAuth";



function App() {
  const { isLoggedIn, userData, handleLogin, isLoading, logout } = useAuth();


  const navItems = [
    { text: "Home", link: "/trf/", access: userData?.access_level >= 0,
    },
    {
      text: "Config",
      link: "/trf/config",
      access: userData?.access_level >= 1,
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
    if (!userData || !userData.access_level) {
      return null;
    }

    // Create an array of route objects based on user access permissions
    const routes = [
      // Map additional routes based on user access permissions
      ...(userData?.access_level >= 0
        ? [{ path: "/trf/", element: <HomePage /> }]
        : []),
      ...(userData?.access_level >= 1
        ? [{ path: "/trf/config", element: <ParamPage /> }]
        : []),
    ];

    return routes.map((route, index) => (
      <Route key={index} path={route.path} element={route.element} />
    ));
  };

  useEffect(() => {
    if (!isLoading && !isLoggedIn) {
      // Automatically trigger the OAuth login flow if the user is not logged in
      handleLogin();
    }
  }, [isLoading, isLoggedIn, handleLogin]);
  
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
        <Routes>
          <Route path="*" element={<div>Redirecting...</div>} />
        </Routes>


      )}
    </Router>
  );
}

export default App;
