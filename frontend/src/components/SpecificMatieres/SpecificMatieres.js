import './SpecificMatieres.css';
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import SupervisorSecNav from '../SupervisorSecNav/SupervisorSecNav';
import useRefreshJWToken from '../../hooks/sessionHooks/refreshJWToken';
import useDiveIn from './hooks/runscripthook';
import useDiveOut from './hooks/diveOut';
import useGetCredentials from '../../hooks/getCredentials';
import { useAuth } from '../../context/authContext';
import PageSpinner from '../PageSpinner/PageSpinner';

/* This page should call the backend for a scraper which will gather data in tuple pairs.
   This scraper, optimally will run in off-hours, and store the data in the database, so then it can be fetched on render for the user to access without 
   waiting for the scraper. This will work because data that might be created in a day might not be relevant for that same day. And if it is, the user has the
   possibility to run the scraper (with a filter also to speed the process).
   So in default, it is just a data render page with an update data feature (scraper run).
*/


const MatieresSpecifiquesPage = () => {
    const [data, setData] = useState([]); // Each tuple has a material type or item and a quantity ex: "(article,24)"
    const diveIn = useDiveIn();
    const diveOut = useDiveOut();
    const [credentials, setCredentials] = useState({ username: null, api_key: null });
    const getCredentials = useGetCredentials()    // Get credentials api hook, calls the api with the current logged user and retrieves username and api_key
    // Then stores it in useState credentials
    const [loading, setLoading] = useState(false)
    const nav = useNavigate()
    const [filters, setFilters] = useState({ "Agence": "Tous", "Team": "Tous" })

    const [selectedTeam, setSelectedTeam] = useState(null)
    const [selectedAgence, setSelectedAgence] = useState(null)
    const teamSelectRef = useRef()
    const agenceSelectRef = useRef()

    
    const permited = false //testing, should be based on user role

    const { user, jwtoken, logout } = useAuth()

    useEffect(() => {
        const fetchCredentials = async () => {
            if (!user || !jwtoken) {
                setLoading(true);
                return;
            }

            try {
                // Explicitly await the credentials promise
                const creds = await getCredentials();
                setCredentials(creds);
                setLoading(false);
            } catch (error) {
                console.error("Failed to fetch credentials:", error);
                setLoading(false);
                logout();
            }
        };

        fetchCredentials();
    }, [jwtoken, user]); // Remove getCredentials from dependencies


    const ArticlesTable = () => {

        //This endpoint needs to accept filters, as for now, team //
        const [data, setData] = useState([]);
        const { user, logout } = useAuth()
        const refreshJWToken = useRefreshJWToken()

        useEffect(() => {

            const fetchData = async (token) => {
                try {
                    const response = await fetch(`http://134.122.108.55:8000/api/dive/fetchall?team=${filters['Team']}&agence=${filters['Agence']}`, {
                        method: "GET",
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    });

                    if (response.ok) {
                        const result = await response.json();
                        setData(result.data);
                    } else if (response.status === "401") {
                        try {
                            await refreshJWToken(); //this is the userefreshjwtoken hook, not the context method
                            console.log("Session validated!");
                            const new_token = localStorage.getItem('jwtoken')
                            fetchData(new_token)
                            
                        } catch (error) {
                            console.log(error);
                            nav('/');  // Redirect if refresh fails
                            logout(user);  // Clear user session
                            return;  // Break out of the function here
                        };
                    };
                    console.error("Failed to fetch data:", response.statusText);
                } catch (error) {
                    console.error("Error fetching data:", error);
                }
            };

            fetchData(localStorage.getItem('jwtoken'));
        }, []);


        //TECHNICAL DEBT BELOW, AGENCE IS ONLY A NUMBER, BECAUSE IN DATABASE I DID DB.INTEGER, SHOULD BE DB.STRING SO IT CAN HOLD AGENCE NAME
        return (
            <div className="articles-table-container">
                {data.length > 0 ? (
                    <table className="articles-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Article Name</th>
                                <th>Quantity</th>
                                <th>Order CO</th>
                                <th>Team</th>
                                <th>Agence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((item) => (
                                <tr key={item.ID}>
                                    <td>{item.ID}</td>
                                    <td>{item["Article Name"]}</td>
                                    <td>{item.Quantity}</td>
                                    <td><a href={item.href}>{item["Order CO"]}</a></td>
                                    <td>{item.Team}</td>
                                    <td>{item.Agence}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p className="loading-message">Loading data...</p>
                )}
            </div>
        );
    };


    const updateDataTuples = async () => {
        if (!credentials.username || !credentials.api_key) {
            console.error("Credentials not loaded yet.");
            return;
        }
        try {
            let userInput = prompt("Enter password:");
            const result = await diveIn(localStorage.getItem('jwtoken'), credentials.api_key, credentials.username,userInput); // Call the backend
            if (result && result.message) {
                console.log(result.message);
                setData(result.message);
                return;
            } else {
                console.error('Unexpected response structure:', result);
                return;
            }
        } catch (error) {
            console.error('Error while fetching data:', error); // Handle errors
            return;
        }
    };

    const generateFile = async () => {
        try {
            const result = await diveOut(localStorage.getItem('jwtoken'));
            if (result) {
                console.log("Table downloaded")
            } else {
                console.error('Unexpected response', result)
            };
        } catch (error) {
            console.error('Error while trying to export file', error);
        };
    };

    const handleTeamSelect = () => {
        setSelectedTeam(teamSelectRef.current.value)
        setFilters((prevData) => ({
            ...prevData,
            ["Team"]: teamSelectRef.current.value,
        }));
    };
    const handleAgenceSelect = () => {
        setSelectedAgence(agenceSelectRef.current.value)
        setFilters((prevData) => ({
            ...prevData,
            ["Agence"]: agenceSelectRef.current.value,
        }));
    };

    return !loading ? (
        <>
            <SupervisorSecNav />
            <div className="container-fluid text-center" id="main-container">
                <div className="row">
                    <div className="col-md-3 col-12" id="left">
                        <h1 className='container-title'>
                            Actions
                        </h1>
                        <div id="user-actions">
                            <button onClick={() => generateFile()}>Télécharger les informations</button>
                            <button onClick={() => updateDataTuples()} disabled={permited}>Mettre à jour</button>
                            <button onClick={() => console.log(filters)}>Notifier l'atelier</button>
                            <div id="filters">
                                <p>Filter content</p>
                                <select onChange={handleAgenceSelect} ref={agenceSelectRef}>
                                    <option disabled selected>Agence</option>
                                    <option>Tous</option>
                                    <option value="001">001 - C.R.P.H.</option>
                                    <option value="003">003 - SEP INCENDIE</option>
                                    <option value="015">015 - SUD INCENDIE</option>
                                    <option value="036">036 - O.R.S</option>
                                    <option value="041">041 - SARL MARSELLA</option>
                                    <option value="100">100 - DESAUTEL MONTLUEL</option>
                                    <option value="101">101 - DESAUTEL LYON OUEST</option>
                                    <option value="102">102 - DESAUTEL GRENOBLE</option>
                                    <option value="103">103 - DESAUTEL BORDEAUX</option>
                                    <option value="104">104 - DESAUTEL NANCY</option>
                                    <option value="105">105 - DESAUTEL LILLE</option>
                                    <option value="106">106 - DESAUTEL TOULOUSE</option>
                                    <option value="107">107 - DESAUTEL MONTPELLIER</option>
                                    <option value="108">108 - DESAUTEL PARIS NORD</option>
                                    <option value="109">109 - DESAUTEL PARIS SUD</option>
                                    <option value="110">110 - DESAUTEL MARSEILLE</option>
                                    <option value="111">111 - DESAUTEL STRASBOURG</option>
                                    <option value="112">112 - DESAUTEL ST ETIENNE</option>
                                    <option value="113">113 - DESAUTEL CLERMONT</option>
                                    <option value="115">115 - DESAUTEL NICE</option>
                                    <option value="116">116 - DESAUTEL DIJON</option>
                                    <option value="117">117 - DESAUTEL NANTES</option>
                                    <option value="118">118 - DESAUTEL POITIERS</option>
                                    <option value="119">119 - DESAUTEL TOURS</option>
                                    <option value="120">120 - DESAUTEL BESANCON</option>
                                    <option value="121">121 - DESAUTEL LYON EST</option>
                                    <option value="122">122 - DESAUTEL REIMS</option>
                                    <option value="123">123 - DESAUTEL RENNES</option>
                                    <option value="124">124 - DESAUTEL PARIS CENTRE</option>
                                    <option value="125">125 - DESAUTEL PARIS OUEST</option>
                                    <option value="126">126 - DESAUTEL CAEN</option>
                                    <option value="132">132 - DESAUTEL ROUEN</option>
                                    <option value="133">133 - FRANSEL</option>
                                </select>
                                <select onChange={handleTeamSelect} ref={teamSelectRef}>
                                    <option disabled selected>Team </option>
                                    <option>Tous</option>
                                    <option> Jeremy</option>
                                    <option> Aurélien</option>
                                    <option> Tepea</option>
                                </select>
                                <select>
                                    <option disabled selected>Matiere backend necessary</option>
                                    <option>Tous</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-9 col-12" id="right">
                        <h1 className='container-title'>
                            Matieres Specifiques
                        </h1>
                        <div id='data-render'>
                            <ArticlesTable />
                        </div>
                    </div>
                </div>
            </div>
        </>
    ) : (
        <PageSpinner />
    );
};

export default MatieresSpecifiquesPage;
