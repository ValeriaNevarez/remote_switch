import Header from "./Header";
import { ChangeDeviceActive, ReadDatabase } from "./database_util";
import React, { useState, useEffect } from "react";
import { GetStatusList, MakeCall } from "./twilio_util";
import DataTable from "datatables.net-react";
import DT from "datatables.net-bs5";
import { Modal } from "bootstrap";
import { data } from "react-router-dom";

DataTable.use(DT);

const CallModal = ({ data, update }) => {
  const [notice, setNotice] = useState("");
  const [callButtonEnabled, setCallButtonEnabled] = useState(true);

  useEffect(() => {
    if (notice != "") {
      setTimeout(() => {
        setNotice("");
      }, 2000);
    }
  }, [notice]);

  if (!data) return <></>;
  return (
    <div
      className="modal fade"
      id="modal"
      data-bs-backdrop="static"
      data-bs-keyboard="true"
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
            <b>Último estatus: </b>
            {data.status}
            <br />
            <br />
            <button
              type="button"
              onClick={() => {
                setCallButtonEnabled(false);
                MakeCall(data.phone_number)
                  .then(() => {
                    setNotice("Se realizó la llamada");
                    update();
                    setTimeout(() => {
                      update();
                    }, 10000);
                    setTimeout(() => {
                      update();
                      setCallButtonEnabled(true);
                    }, 80000);
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
                    update();
                  })
                  .catch((e) => {
                    setNotice("Error al actualizar el estado: " + e);
                  });
              }}
              className={
                data.is_active == "Activo"
                  ? "btn btn-secondary ms-3"
                  : "btn btn-primary ms-3"
              }
            >
              {data.is_active == "Activo" ? "Desactivar" : "Activar"}
            </button>
            {"" !== notice && (
              <div className="alert alert-warning mt-3" role="alert">
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
    if (
      data.status.includes("in-progress") ||
      data.status.includes("ringing") ||
      data.status.includes("queued")
    ) {
      row.className = "table-info";
    } else if (
      data.is_active == "Activo" &&
      !data.status.includes("completed")
    ) {
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

  const update = () => {
    GetList().then((result) => {
      const data = ListToDataArray(result);
      setDataArray(data);
    });
  };

  // Codigo que se hace una vez
  useEffect(() => {
    update();
    // setInterval(() => {
    //   update();
    // }, 60000);
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
      <CallModal
        data={modalData}
        update={() => {
          update();
        }}
      ></CallModal>
      <Header currentPage={"lista"}> </Header>
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
  if (date == null) {
    return "-";
  }

  let dt = new Date(date);
  if (isNaN(dt)) {
    return "-";
  }

  const date1 = dt;
  let today = new Date();
  const date2 = today;

  const diffTime = Math.abs(date2.getTime() - date1.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  let days = "";
  if (diffDays == 1) {
    days = " día";
  } else {
    days = " días";
  }

  return "Hace " + diffDays + days;
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
