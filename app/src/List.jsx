import Header from "./Header";
import { ChangeDeviceActive, ReadDatabase } from "./database_util";
import React, { useState, useEffect } from "react";
import { GetStatusList, MakeCall } from "./twilio_util";
import DataTable from "datatables.net-react";
import DT from "datatables.net-bs5";
import { Modal } from "bootstrap";
import { data } from "react-router-dom";

DataTable.use(DT);

const CallModal = ({ data }) => {
  const [notice, setNotice] = useState("");
  const [callButtonEnabled, setCallButtonEnabled] = useState(true);

  if (!data) return <></>;
  return (
    <div
      className="modal fade"
      id="modal"
      data-bs-backdrop="static"
      data-bs-keyboard="false"
      tabIndex="-1"
      aria-labelledby="staticBackdropLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h1 className="modal-title fs-5" id="staticBackdropLabel">
              Panel de control
            </h1>
            <button
              type="button"
              className="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div className="modal-body">
            <b>Número de serie: </b>
            {data.serial_number}
            <br />
            <b>Celular: </b>
            {data.phone_number}
            <br />
            <b>Estado actual: </b>
            {data.is_active}
            <br />
            <br />
            <button
              type="button"
              onClick={() => {
                setCallButtonEnabled(false);
                MakeCall(data.phone_number)
                  .then(() => {
                    setNotice("Se realizó la llamada");
                  })
                  .catch((e) => {
                    setNotice("Error al realizar la llamada:" + error);
                  });
              }}
              className="btn btn-dark"
              disabled={!callButtonEnabled}
            >
              Llamar
            </button>
            <button
              type="button"
              onClick={() => {
                ChangeDeviceActive(
                  data.serial_number,
                  data.is_active == "Activo" ? false : true
                )
                  .then(() => {
                    setNotice("Se actualizó el estado");
                  })
                  .catch((e) => {
                    setNotice("Error al actualizar el estado: " + error);
                  });
              }}
              className={
                data.is_active == "Activo"
                  ? "btn btn-secondary"
                  : "btn btn-primary"
              }
            >
              {data.is_active == "Activo" ? "Desactivar" : "Activar"}
            </button>
            {"" !== notice && (
              <div className="alert alert-warning" role="alert">
                {notice}
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-primary"
              data-bs-dismiss="modal"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const List = () => {
  const [modalData, setModalData] = useState({});
  const [dataArray, setDataArray] = useState([]);
  const [selectedSerialNumber, setSelectedSerialNumber] = useState(null);

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

    row.onclick = () => {
      const modal = new Modal("#modal");
      modal.show();
      setSelectedSerialNumber(data.serial_number);
      setModalData(data);
    };
  };

  const dataTableOptions = {
    paging: false,
    layout: dataTableLayout,
    rowCallback: dataTableRowCallback,
  };

  // Codigo que se hace una vez
  useEffect(() => {
    const update = () => {
      GetList().then((result) => {
        const data = ListToDataArray(result);
        setDataArray(data);
      });
    };
    update();
    setInterval(() => {
      update();
    }, 5000);
  }, []);

  useEffect(() => {
    if (selectedSerialNumber !== null) {
      setModalData(
        dataArray.find((data) => {
          return selectedSerialNumber == data.serial_number;
        })
      );
    }
  }, [dataArray]);

  return (
    <>
      <CallModal data={modalData}></CallModal>
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
