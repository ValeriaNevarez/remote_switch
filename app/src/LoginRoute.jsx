import { useContext } from "react";
import { AuthContext } from "./AuthProvider";
import PropTypes from "prop-types";
import { Navigate } from "react-router-dom";

const LoginRoute = ({ children }) => {
  const { loading, user } = useContext(AuthContext);

  if (loading) {
    return <span className="loading loading-dots loading-lg"></span>;
  }

  if (!user) {
    return children;
  }

  return <Navigate to="/" />;
};

LoginRoute.propTypes = {
  children: PropTypes.node,
};

export default LoginRoute;
