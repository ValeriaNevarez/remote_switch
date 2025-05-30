import { useState, useEffect } from "react";
import { AuthContext } from "./AuthProvider";
import { useNavigate } from "react-router-dom";
import { useContext } from "react";

const Login = () => {
  const { loginUser, loading, user, error } = useContext(AuthContext);
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState("");

  const loginWithUsernameAndPassword = async (e) => {
    e.preventDefault();
    loginUser(email, password);
  };

  useEffect(() => {
    if (user) {
      navigate("/");
    }
  }, [user]);

  useEffect(() => {
    if (error) {
      setNotice("Usuario o contraseña incorrectos.");
    }
  }, [error]);

  return (
    <>
      <div className="container">
        <div className="row justify-content-center">
          <form className="col-md-4 mt-3 pt-3 pb-3">
            {notice == "" ? (
              ""
            ) : (
              <div className="alert alert-warning" role="alert">
                {notice}
              </div>
            )}
            <img src="logo2.png" alt="logo" className="img-fluid"></img>
            <p></p>
            <div className="form-floating mb-3">
              <input
                type="email"
                className="form-control"
                id="exampleInputEmail1"
                aria-describedby="emailHelp"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              ></input>
              <label htmlFor="exampleInputEmail1" className="form-label">
                Correo electrónico
              </label>
            </div>
            <div className="form-floating mb-3">
              <input
                type="password"
                className="form-control"
                id="exampleInputPassword1"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              ></input>
              <label htmlFor="exampleInputPassword1" className="form-label">
                Contraseña
              </label>
            </div>
            <div className="d-grid">
              <button
                type="submit"
                className="btn btn-primary pt-3 pb-3"
                onClick={(e) => loginWithUsernameAndPassword(e)}
              >
                Ingresar
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
};

export default Login;
