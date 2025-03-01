import './Toolbox.css'
import React from 'react'
import { Link } from 'react-router-dom'
import SupervisorSecNav from '../SupervisorSecNav/SupervisorSecNav' //Need to make this less repetitive, maybe a second page template for each user role


const ToolboxPage = () => {

    return (
        <>  
            <SupervisorSecNav/>   
            <Link to="/specificMatieres" className="ToolLink">Matieres Specifiques</Link>
        </>
    )
}

export default ToolboxPage