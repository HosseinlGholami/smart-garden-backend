// src/index.js
import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";

const root = document.getElementById("root");
const reactRoot = createRoot(root);
reactRoot.render(<App />);
