import { useNavigate } from "react-router-dom";
import auth  from "./firebase";
import { signOut } from "firebase/auth";
import Header from "./Header";


const Report = () => {
  const navigate = useNavigate();
  const user = auth.currentUser;

  const logoutUser = async (e) => {
    e.preventDefault();

    await signOut(auth);
    navigate("/");
  };
  return (
    <>
      <Header currentPage={"reporte"}> </Header>
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-4 text-center">
            <p>
              Welcome{" "}
              <em className="text-decoration-underline">{user.email}</em>. You
              are logged in!
            </p>
            <div className="d-grid gap-2">
              <button
                type="submit"
                className="btn btn-primary pt-3 pb-3"
                onClick={(e) => logoutUser(e)}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Report;