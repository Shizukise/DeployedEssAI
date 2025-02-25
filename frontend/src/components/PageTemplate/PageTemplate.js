import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import './PageTemplate.css'
import { useAuth } from "../../context/authContext";
import useValidateSession from "../../hooks/sessionHooks/validateSession";
import PageSpinner from "../PageSpinner/PageSpinner";

const PageTemplate = ({ children }) => {

    const { logout, user, jwtoken } = useAuth()
    const validateSession = useValidateSession();

    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (!user || !jwtoken) {
            setLoading(true)
            return; // Don't attempt to fetch credentials if user or token is not set yet. A loading can be inserted here
        }
        validateSession()
        setLoading(false)
    }, [user, jwtoken])

    return !loading ? (
        <>
            <div id="TopNav">
                <button id="LogoutBtn" onClick={logout}>Déconnexion</button>
                <Link to="/dashboard"><i className="bi bi-house" id="HomeButton"></i></Link>
            </div>
            <div id="Children">
                {children}
            </div>
        </>
    ) :
        <>
            <PageSpinner/>
        </>
}


export default PageTemplate