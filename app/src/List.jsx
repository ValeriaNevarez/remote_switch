import Header from "./Header";
import { ReadDatabase } from "./database_util";
import { useState, useEffect, useContext } from "react";
import { AuthContext } from "./AuthProvider";
import { GetStatusList } from "./twilio_util";
import DataTable from "datatables.net-react";
import DT from "datatables.net-bs5";
import { Modal } from "bootstrap";
import "datatables.net-responsive-dt";
import AddClientModal from "./AddClientModal";
import CallModal from "./CallModal";

// eslint-disable-next-line react-hooks/rules-of-hooks
DataTable.use(DT);

const List = () => {
  const { user } = useContext(AuthContext);
  const [modalData, setModalData] = useState(null);
  const [dataArray, setDataArray] = useState([]);
  const [selectedSerialNumber, setSelectedSerialNumber] = useState(null);
  const [isAddClientModalOpen, setIsAddClientModalOpen] = useState(false);
  const isAuthorized = user?.email === "admin@admin.com";

  const columns = [
    {
      data: "serial_number",
      responsivePriority: 3,
      render: (serial_number, type) => {
        if (type == "filter") {
          return "#" + serial_number;
        } else {
          return serial_number;
        }
      },
    },
    { data: "phone_number", responsivePriority: 4 },
    { data: "client_name", responsivePriority: 2 },
    { data: "client_number", responsivePriority: 2 },
    {
      data: "enabled_and_is_active",
      responsivePriority: 1,
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
      responsivePriority: 1,
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
    { data: "date", responsivePriority: 1 },
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
    if (data.diffDays > 40) {
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
    responsive: {
      details: {
        type: "column",
      },
    },
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
      const new_modal_data = dataArray.find((data) => {
        return selectedSerialNumber == data.serial_number;
      });
      if (new_modal_data) {
        setModalData(new_modal_data);
      } else {
        // Device was deleted or not found, clear the state
        setSelectedSerialNumber(null);
        setModalData(null);
      }
    }
  }, [dataArray, selectedSerialNumber]);

  return (
    <>
      <CallModal
        data={modalData}
        update={() => {
          update();
        }}
        onClose={() => {
          setSelectedSerialNumber(null);
          setModalData(null);
        }}
      ></CallModal>
      {isAuthorized && (
        <AddClientModal
          onAdd={() => {
            update();
          }}
          isOpen={isAddClientModalOpen}
          handleClose={() => setIsAddClientModalOpen(false)}
        ></AddClientModal>
      )}
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
              <th scope="col"># Celular</th>
              <th scope="col">Cliente</th>
              <th scope="col"># Cliente</th>
              <th scope="col">
                <i className="bi bi-power"></i>
              </th>
              <th scope="col">Estatus</th>
              <th scope="col">Último enlace</th>
            </tr>
          </thead>
        </DataTable>
        {isAuthorized && (
          <button
            className="btn btn-primary mt-3"
            onClick={() => {
              setIsAddClientModalOpen(true);
            }}
          >
            Agregar cliente
          </button>
        )}
        <div className="mt-3">
          <a href="user_manual.pdf" target="_blank">
            Manual de usuario
          </a>
        </div>
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
