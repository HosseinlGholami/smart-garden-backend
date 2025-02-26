import React from "react";
import logo from "../statics/dk.png";
import Dropdown from "react-bootstrap/Dropdown";
import Nav from "react-bootstrap/Nav";

const CustomNavbar = ({ userData, navItems }) => {
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.reload();
  };

  const renderUserDropdown = () => {
    console.log(userData)
    return (
      <Dropdown.Menu>
        <Dropdown.Item>
          <h6>first name:</h6> {userData.first_name}
        </Dropdown.Item>
        <Dropdown.Item>
          <h6>last name:</h6> {userData.last_name}
        </Dropdown.Item>
        <Dropdown.Item>
          <h6>role:</h6> {userData.user_role.name}
        </Dropdown.Item>
        <Dropdown.Divider />
        <Dropdown.Item onClick={handleLogout}>Logout</Dropdown.Item>
      </Dropdown.Menu>
    );
  };

  return (
    <Nav className="navbar navbar-expand-lg navbar-light bg-light container-fluid">
      <a className="navbar-brand" href="#">
        <img src={logo} alt="Logo" width="200" />
      </a>
      <Nav.Item className="ml-auto">
        <Dropdown>
          <Dropdown.Toggle variant="light" id="dropdown-basic">
            {userData ? userData.username : "User"}
          </Dropdown.Toggle>
          {renderUserDropdown()}
        </Dropdown>
      </Nav.Item>
      <Nav.Item>
        <ul className="navbar-nav ml-auto">
          {navItems.map((item, index) => (
            <li className="nav-item" key={index}>
              <a className="nav-link" href={item.link}>
                {item.text}
              </a>
            </li>
          ))}
        </ul>
      </Nav.Item>
    </Nav>
  );
};

export default CustomNavbar;
