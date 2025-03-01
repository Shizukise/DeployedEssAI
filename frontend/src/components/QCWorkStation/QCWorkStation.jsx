import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/authContext";
import useGetCredentials from "../../hooks/getCredentials";
import PageSpinner from "../PageSpinner/PageSpinner";
import SupervisorSecNav from "../SupervisorSecNav/SupervisorSecNav";



function QCWorkStation() {
  const { user,jwtoken } = useAuth()
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
  

  return !loading ? (
    <>
      <SupervisorSecNav/>
      HOMEPAGE for QC
    </>
  ) : 
      <PageSpinner/>;
}

export default QCWorkStation;
