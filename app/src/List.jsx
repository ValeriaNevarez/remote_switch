import Header from "./Header";
import {
  ChangeDeviceActive,
  ReadDatabase,
  ChangeDeviceEnable,
  ChangeDeviceClientName,
  ChangeDeviceClientNumber,
} from "./database_util";
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
  const [clientNameInput, setClientNameInput] = useState("");
  const [clientNumberInput, setClientNumberInput] = useState("");

  useEffect(() => {
    setClientNameInput("");
    setClientNumberInput("");
  }, [data]);

  useEffect(() => {
    if (notice != "") {
      setTimeout(() => {
        setNotice("");
      }, 3000);
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
            <div className="input-group mb-3">
              <span className="input-group-text">Nombre de cliente</span>
              <input
                type="text"
                className="form-control"
                placeholder={data.client_name}
                value={clientNameInput}
                onChange={(e) => {
                  setClientNameInput(e.target.value);
                }}
              ></input>
              <button
                className="btn btn-outline-secondary"
                type="button"
                onClick={() => {
                  ChangeDeviceClientName(data.serial_number, clientNameInput)
                    .then(() => {
                      setNotice("Se actualizó el nombre del cliente");
                      update();
                    })
                    .catch((e) => {
                      setNotice(
                        "Error al actualizar el nombre del cliente: " + e
                      );
                    });
                }}
              >
                <i className="bi bi-check-lg"></i>
              </button>
            </div>
            <div className="input-group mb-3">
              <span className="input-group-text">No. de cliente</span>
              <input
                type="text"
                className="form-control"
                placeholder={data.client_number}
                value={clientNumberInput}
                onChange={(e) => {
                  setClientNumberInput(e.target.value);
                }}
              ></input>
              <button
                className="btn btn-outline-secondary"
                type="button"
                onClick={() => {
                  ChangeDeviceClientNumber(data.serial_number, clientNumberInput)
                    .then(() => {
                      setNotice("Se actualizó el número de cliente");
                      update();
                    })
                    .catch((e) => {
                      setNotice(
                        "Error al actualizar el número de cliente: " + e
                      );
                    });
                }}
              >
                <i className="bi bi-check-lg"></i>
              </button>
            </div>

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
            <b>On/Off: </b>
            {data.enable}
            <br />
            <br />
            <button
              type="button"
              onClick={() => {
                setCallButtonEnabled(false);
                MakeCall(data.phone_number, data.enable == "On")
                  .then(() => {
                    setNotice("Se realizó la llamada");
                    update();
                    setTimeout(() => {
                      update();
                    }, 10000);
                    setTimeout(() => {
                      update();
                      setCallButtonEnabled(true);
                    }, 90000);
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
            <button
              type="button"
              onClick={() => {
                const currentEnable = data.enable;
                const newEnable = data.enable == "On" ? false : true;
                ChangeDeviceEnable(data.serial_number, newEnable)
                  .then(() => {
                    setNotice("Se actualizó el estado");
                    update();
                    setCallButtonEnabled(false);
                    MakeCall(data.phone_number, newEnable)
                      .then(() => {
                        setNotice(
                          "Se realizó la llamada para cambiar el estado."
                        );
                        update();
                        setTimeout(() => {
                          update();
                        }, 10000);
                        setTimeout(() => {
                          update();
                          setCallButtonEnabled(true);
                        }, 90000);
                      })
                      .catch((e) => {
                        setNotice("Error al realizar la llamada:" + error);
                      });
                  })
                  .catch((e) => {
                    setNotice("Error al actualizar el estado: " + e);
                  });
              }}
              className={
                data.enable == "On"
                  ? "btn btn-secondary ms-3"
                  : "btn btn-success ms-3"
              }
              disabled={!callButtonEnabled}
            >
              {data.enable == "On" ? "Apagar" : "Encender"}
            </button>

            {"" !== notice && (
              <div className="alert alert-warning mt-3" role="alert">
                {notice}
              </div>
            )}
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
    { data: "client_name" },
    { data: "client_number" },
    {
      data: "enabled_and_is_active",
      render: (enabled_and_is_active, type) => {
        const enabled = enabled_and_is_active["enabled"];
        const is_active = enabled_and_is_active["is_active"];

        if (type !== "display") {
          if (is_active == false) {
            return "inactivo";
          }
          if (is_active == true && enabled == true) {
            return "on";
          }
          if (is_active == true && enabled == false) {
            return "off";
          }
        }
        if (is_active == false) {
          return '<i class="bi bi-circle"></i>';
        }
        if (is_active == true && enabled == true) {
          return '<i class="bi bi-circle-fill" style="font-size: 1rem; color: green;"></i>';
        }
        if (is_active == true && enabled == false) {
          return '<i class="bi bi-circle-fill" style="font-size: 1rem; color: rgb(194, 66, 66);"></i>';
        }
      },
    },
    {
      data: "status_and_diff_days",
      render: (status_and_diff_days, type) => {
        const status = status_and_diff_days["status"];
        const diff_days = status_and_diff_days["diff_days"];

        if (type !== "display") {
          if (status == "completed") {
            return "aacompleted";
          } else {
            return "bb" + status;
          }
        }

        if (status == "completed") {
          return (
            '<i class="bi bi-check-lg" style="color: rgb(40, 179, 86);"></i>' +
            " " +
            diff_days
          );
        } else if (
          status == "in-progress" ||
          status == "ringing" ||
          status == "queued"
        ) {
          return '<i class="bi bi-telephone-outbound" style="color: rgb(35, 101, 177);" ></i>';
        } else {
          return (
            '<i class="bi bi-telephone-x" style="color: rgb(194, 66, 66);"></i>' +
            " " +
            diff_days
          );
        }
      },
    },
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
    const status = data["status_and_diff_days"]["status"];
    if (status == "in-progress" || status == "ringing" || status == "queued") {
      row.className = "table-info";
    } else if (data.is_active == "Activo" && status != "completed") {
      row.className = "table-warning";
    }
    if (data.diffDays > 30) {
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

  useEffect(() => {
    update();
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
              <th scope="col">Cliente</th>
              <th scope="col">No. de cliente</th>
              <th scope="col">
                <i className="bi bi-power"></i>
              </th>
              <th scope="col">Estatus</th>
              <th scope="col">Último enlace</th>
            </tr>
          </thead>
        </DataTable>
        <a href="user_manual.pdf" target="_blank">
          Manual de usuario
        </a>
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
    const enable = e["enabled"];
    statusList[phoneNumber]["enabled"] = enable;
    statusList[phoneNumber]["client_name"] = e["client_name"];
    statusList[phoneNumber]["client_number"] = e["client_number"];
  }

  return statusList;
};

const GetDaysSince = (date_str) => {
  if (date_str == null) {
    return null;
  }

  let date = new Date(date_str);
  if (isNaN(date)) {
    return null;
  }

  let today = new Date();

  const diffTime = Math.abs(today.getTime() - date.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  return diffDays;
};

const FormatDate = (date_str) => {
  const diffDays = GetDaysSince(date_str);
  if (diffDays == null) {
    return "-";
  }

  let days = "";
  if (diffDays == 1) {
    days = " día";
  } else {
    days = " días";
  }

  return diffDays + days;
};

const ListToDataArray = (list) => {
  return Object.entries(list).map((entry) => {
    let phoneNumber = entry[0];
    let value = entry[1];
    let status = value["status"];
    return {
      serial_number: value["serial_number"],
      phone_number: phoneNumber,
      client_name: value["client_name"],
      client_number: value["client_number"],
      is_active: value["is_active"] ? "Activo" : "Inactivo",
      status:
        status == null
          ? "-"
          : status + "  (" + FormatDate(value["status_date"]) + ") ",
      date: FormatDate(value["date"]),
      diffDays: GetDaysSince(value["date"]),
      enable: value["enabled"] ? "On" : "Off",
      status_icon: status,
      enabled_and_is_active: {
        enabled: value["enabled"],
        is_active: value["is_active"],
      },
      status_and_diff_days: {
        status: status,
        diff_days: FormatDate(value["status_date"]),
      },
    };
  });
};

export default List;
