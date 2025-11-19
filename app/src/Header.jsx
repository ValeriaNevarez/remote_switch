import { useNavigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "./AuthProvider";
import React from "react";

const Header = ({ currentPage }) => {
  const navigate = useNavigate();
  const { logOut, user } = useContext(AuthContext);

  const logoutUser = async (e) => {
    e.preventDefault();
    await logOut();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg bg-dark" data-bs-theme="dark">
      <div className="container-fluid">
        <a className="navbar-brand">Switch Remoto</a>
        
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          </ul>
          <div className="d-flex align-items-center me-3">
            <span className="text-light me-3">
              {user?.email || "Usuario"}
            </span>
          </div>
          <button
            className="btn btn-primary d-flex"
            type="submit"
            onClick={(e) => logoutUser(e)}
          >
            Cerrar sesión
          </button>
        </div>
    </nav>
  );
};

export default Header;
