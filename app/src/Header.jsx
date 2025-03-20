import { useNavigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "./AuthProvider";
import React from "react";

function Header() {
  const navigate = useNavigate();
  const { logOut } = useContext(AuthContext);

  const logoutUser = async (e) => {
    e.preventDefault();
    await logOut();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg bg-dark" data-bs-theme="dark">
      <div className="container-fluid">
        <a className="navbar-brand">Switch Remoto</a>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <a className="nav-link active px-4" aria-current="page" href="./">
                Lista dispositivos
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link px-4" href="#">
                Reporte
              </a>
            </li>
          </ul>
          <button
            className="btn btn-primary d-flex"
            type="submit"
            onClick={(e) => logoutUser(e)}
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Header;
