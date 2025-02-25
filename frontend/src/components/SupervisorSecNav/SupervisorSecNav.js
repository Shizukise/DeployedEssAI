import './SupervisorSecNav.css'
import React from 'react'
import { Link } from 'react-router-dom'


const SupervisorSecNav = () => {
    return (
        <nav className='SupervisorSecNav'>
            <Link to="/Toolbox" className='ToolboxLink'>Toolbox <i className="bi bi-wrench-adjustable"></i></Link>
        </nav>
    )
}


export default SupervisorSecNav