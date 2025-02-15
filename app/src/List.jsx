import { useNavigate } from "react-router-dom";
import auth, { database } from "./firebase";
import { signOut } from "firebase/auth";
import Header from "./Header";
import { GetIdForSerialNumber, readDatabase } from "./database_util";
import React, { useState, useEffect } from "react";

const List = () => {
  const navigate = useNavigate();
  const user = auth.currentUser;
  const [databaseContent, setDatabaseContents] = useState([]);
  const [id, setId] = useState(-1);

  const logoutUser = async (e) => {
    e.preventDefault();

    await signOut(auth);
    navigate("/");
  };

  // Empieza codigo.
  useEffect(() => {
    GetIdForSerialNumber(37).then((result) => {
      setId(result);
    });
  }, []);

  // Termina codigo.
  useEffect(() => {
    console.log(id)
    // if (databaseContent.length != 0) {
    //   console.log(databaseContent);
    //   // console.log(databaseContent[0]['phone_number']);
    // }
  }, [id]);

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
