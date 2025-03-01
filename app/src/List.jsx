import Header from "./Header";
import { ReadDatabase } from "./database_util";
import React, { useState, useEffect } from "react";
import { GetStatusList } from "./twilio_util";

const List = () => {
  const [list, setList] = useState({});

  // Codigo que se hace una vez
  useEffect(() => {
    GetList().then((result) => {
      setList(result);
    });
  }, []);

  return (
    <>
      <Header> </Header>
      <div className="container">
        <table className="table">
          <thead>
            <tr>
              <th scope="col">No. de serie</th>
              <th scope="col">No. de celular</th>
              <th scope="col">Activo/Inactivo</th>
              <th scope="col">Estatus</th>
              <th scope="col">Fecha de última llamada completada</th>
            </tr>
          </thead>
          <tbody className="table-group-divider">
            {Object.entries(list).map((entry) => {
              let phoneNumber = entry[0];
              let value = entry[1];
              return (
                <tr key={phoneNumber}>
                  <th scope="row">{value["serial_number"]}</th>
                  <td>{phoneNumber}</td>
                  <td>{value["is_active"] ? "Activo" : "Inactivo"} </td>
                  <td>{value["status"]}</td>
                  <td>{value["date"]}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
};

const GetList = async () => {
  const database = await ReadDatabase();
  let phoneNumberArray = [];
  for (const element in database) {
    phoneNumberArray.push(database[element]["phone_number"]);
  }
  let statusList = await GetStatusList(phoneNumberArray);
  for (const element in database) {
    const e = database[element];
    const isActive = e["is_active"];
    const phoneNumber = e["phone_number"];
    const serialNumber = e["serial_number"];
    statusList[phoneNumber]["is_active"] = isActive;
    statusList[phoneNumber]["serial_number"] = serialNumber;
  }

  return statusList;
};

export default List;
