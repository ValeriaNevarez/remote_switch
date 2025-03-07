import Header from "./Header";
import { ReadDatabase } from "./database_util";
import React, { useState, useEffect } from "react";
import { GetStatusList } from "./twilio_util";
import DataTable from "datatables.net-react";
import DT from "datatables.net-bs5";

DataTable.use(DT);

const List = () => {
  const [dataArray, setDataArray] = useState([]);
  const columns = [
    { data: "serial_number" },
    { data: "phone_number" },
    { data: "is_active" },
    { data: "status" },
    { data: "date" },
  ];

  const dataTableLayout = {
    topEnd: {},
    topStart: {
      search: {
        placeholder: "",
        text: "Buscar:",
      },
    },
  };

  const dataTableRowCallback = (row, data) => {
    if (data.is_active == "Activo" && !data.status.includes("completed")) {
      row.className = "table-danger";
    }
  };

  const dataTableOptions = {
    paging: false,
    layout: dataTableLayout,
    rowCallback: dataTableRowCallback,
  };

  // Codigo que se hace una vez
  useEffect(() => {
    GetList().then((result) => {
      const data = ListToDataArray(result);
      console.log(data);
      setDataArray(data);
    });
  }, []);

  return (
    <>
      <Header> </Header>
      <div className="container">
        <DataTable
          className="table table-hover"
          data={dataArray}
          columns={columns}
          options={dataTableOptions}
        >
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">No. de celular</th>
              <th scope="col">Activo / Inactivo</th>
              <th scope="col">Estatus</th>
              <th scope="col"> Última llamada completada</th>
            </tr>
          </thead>
        </DataTable>
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

const FormatDate = (date) => {
  let dt = new Date(date);
  if (isNaN(dt)) {
    return "-";
  }

  const year = dt.getFullYear();
  const month = (dt.getMonth() + 1).toString().padStart(2, "0");
  const day = dt.getDate().toString().padStart(2, "0");

  return day + "/" + month + "/" + year;
};

const ListToDataArray = (list) => {
  return Object.entries(list).map((entry) => {
    let phoneNumber = entry[0];
    let value = entry[1];
    let status = value["status"];
    return {
      serial_number: value["serial_number"],
      phone_number: phoneNumber,
      is_active: value["is_active"] ? "Activo" : "Inactivo",
      status: status + "  (" + FormatDate(value["status_date"]) + ") ",
      date: FormatDate(value["date"]),
    };
  });
};

export default List;
