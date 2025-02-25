import { useNavigate } from "react-router-dom";
import auth, { database } from "./firebase";
import { signOut } from "firebase/auth";
import Header from "./Header";
import { GetIdForSerialNumber, ReadDatabase, ChangeDeviceActive } from "./database_util";
import React, { useState, useEffect } from "react";
import {SendMessage, MakeCall, GetLastCallStatus, GetLastCompletedCallDate, GetStatusList} from "./twilio_util";


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

  // Codigo que se hace una vezcd 
  useEffect(() => {
    GetStatusList(['+16506697507', '+16508611877','pepe']);
    // GetLastCompletedCallDate('+16508611877');
    // GetLastCallStatus('+16508611877').then((status)=> {console.log("react"+status)})
    // MakeCall('+16508611877');
    // SendMessage('+16508611877','hello')
    // ChangeDeviceActive(500,true).catch((error) => {
    //   console.error(error);
    // } )
    // GetIdForSerialNumber(37).then((result) => {
    //   setId(result);
    // });
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
