import { useNavigate } from "react-router-dom";
import  auth, {database}  from "./firebase";
import { signOut } from "firebase/auth";
import Header from "./Header";
import { writeUserData, readDatabase} from "./database_util";

const List = () => {
  const navigate = useNavigate();
  const user = auth.currentUser;

  const logoutUser = async (e) => {
    e.preventDefault();

    await signOut(auth);
    navigate("/");
  };

  // Empieza codigo.
  console.log(readDatabase());
  // Termina codigo.

  return (
    <>
      <Header> </Header>
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-4 text-center">
            
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

export default List;
