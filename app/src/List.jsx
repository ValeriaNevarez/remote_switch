import Header from "./Header";
import {
  GetIdForSerialNumber,
  ReadDatabase,
  ChangeDeviceActive,
} from "./database_util";
import React, { useState, useEffect } from "react";
import {
  SendMessage,
  MakeCall,
  GetLastCallStatus,
  GetLastCompletedCallDate,
  GetStatusList,
} from "./twilio_util";


const List = () => {
  // Codigo que se hace una vez
  useEffect(() => {
    GetStatusList(["+16506697507", "+16508611877"]);
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

  return (
    <>
      <Header> </Header>
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-4 text-center">
            <div className="d-grid gap-2">
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default List;
