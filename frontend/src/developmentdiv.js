import React, { useState, useEffect } from "react";
import { useAuth } from "./context/authContext"
import useGetCredentials from "./hooks/getCredentials";

import PageSpinner from "./components/PageSpinner/PageSpinner";
import SupervisorSecNav from "./components/SupervisorSecNav/SupervisorSecNav";

/* for refresh token call, check if user !== null (same as checking if user is logged in)*/


function Development() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const { user,jwtoken,refreshToken } = useAuth()
  const [credentials, setCredentials] = useState({ username: null, api_key: null });
 
  const getCredentials = useGetCredentials()   // Get credentials api hook, calls the api with the current logged user and retrieves username and api_key
                                                // Then stores it in useState credentials
  const [ loading,setLoading ] = useState(false)

  // Fetch credentials on component mount
  useEffect(() => {
    if (!user || !jwtoken) {
      setLoading(true)
      return; // Don't attempt to fetch credentials if user or token is not set yet. A loading can be inserted here
    }
    
    setLoading(false)
    setCredentials(getCredentials())
  }, [jwtoken, user]); // Only fetch credentials when jwtoken or user is available
  

  // Handle file selection
  const handleFileSelect = (event) => {
    /* This is the first step in the app flow to create a Validation instance and page.
       User will use the upload inpux box to upload all files from an order
    */
    const files = Array.from(event.target.files); // Convert FileList to an array
    setSelectedFiles(files);
  };

  
  // File upload handler using cached credentials
  async function uploadFiles() {
    if (!credentials.username || !credentials.api_key) {
      console.error("Credentials not loaded yet.");
      return;
    }

    if (selectedFiles.length === 0) {
      console.error("No files selected!");
      return;
    }

    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => formData.append("files", file));

      const response = await fetch(
        `http://134.122.108.55:8000/api/validation/create?username=${credentials.username}&api_key=${credentials.api_key}`,
        {
          method: "POST",
          body: formData,
          headers: {
            Authorization: `Bearer ${jwtoken}`,
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log("Files uploaded successfully:", result);
      } else {
        console.error("Failed to upload files:", response.statusText);
      }
    } catch (error) {
      console.error("Network error:", error);
    }
  }

  async function validate() {
    try {
      const response = await fetch('http://134.122.108.55:8000/api/validation/validate', {
        method: 'POST',
        credentials: 'include',
      });
      if (response.ok) {
        const result = await response.json();
        console.log("THIS HAS BEEN", result);
      } else {
        console.error("This has not been validated because:", response.statusText);
      }
    } catch (error) {
      console.error("Network error:", error);
    }
  }

  return !loading ? (
    <>
      <SupervisorSecNav/>
      HOMEPAGE
    </>
  ) : 
      <PageSpinner/>;
}

export default Development;
