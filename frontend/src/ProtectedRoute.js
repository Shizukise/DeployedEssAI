//This can be used to wrap any component we want to be acessed only by authenticated users

import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const username = localStorage.getItem("user")
  const Jwtoken = localStorage.getItem("jwtoken")

  // If the user is logged in and the token exists, allow access
  if (username && Jwtoken) {
    return children;
  }

  // Redirect to login if not authenticated
  return <Navigate to="/" />;
};

export default ProtectedRoute;
