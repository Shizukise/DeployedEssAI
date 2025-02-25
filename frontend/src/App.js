import React from 'react';
import { AuthProvider } from './context/authContext'
import Development from './developmentdiv';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import Login from './LoginComponent';
import PageTemplate from './components/PageTemplate/PageTemplate'
import ToolboxPage from './components/Toolbox/Toolbox';
import MatieresSpecifiquesPage from './components/SpecificMatieres/SpecificMatieres';


function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path='/dashboard' element={<ProtectedRoute><PageTemplate><Development/></PageTemplate></ProtectedRoute>}/> 
          <Route path='/Toolbox' element={<ProtectedRoute><PageTemplate><ToolboxPage/></PageTemplate></ProtectedRoute>}/>
          <Route path='//specificMatieres' element={<ProtectedRoute><PageTemplate><MatieresSpecifiquesPage/></PageTemplate></ProtectedRoute>}/>
          <Route path='/' element={<Login />}/> 
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
