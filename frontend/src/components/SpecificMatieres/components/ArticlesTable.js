import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/authContext';
import './ArticlesTable.css';  // Import the CSS file
import useRefreshJWToken from '../../../hooks/sessionHooks/refreshJWToken';

const ArticlesTable = () => {
    const [data, setData] = useState([]);
    const nav = useNavigate()
    const { user, logout } = useAuth()
    const refreshJWToken = useRefreshJWToken()
    const [filters, setFilets] = useState()

    useEffect(() => {
        
        const fetchData = async (token) => {
            try {
                const response = await fetch(`http://134.122.108.55:8000/api/dive/fetchall`, {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const result = await response.json();
                    setData(result.data);
                } else {
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

export default ArticlesTable;
