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
          <ul className="navbar-nav d-flex justify-content-evenly">
            <li className="nav-item">
              <a
                className="nav-link active px-4"
                aria-current="page"
                href="./lista"
              >
                Lista dispositivos
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link px-4" href="#">
                Realizar llamada
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link px-4" href="#">
                Activar/Desactivar dispositivo
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link px-4" href="#">
                Reporte
              </a>
            </li>
            <li className="nav-item">
              <button
                className="btn btn-primary "
                type="submit"
                onClick={(e) => logoutUser(e)}
              >
                Cerrar sesión
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Header;
