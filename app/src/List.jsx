import Header from "./Header";
import { ReadDatabase } from "./database_util";
import { useState, useEffect, useContext } from "react";
import { AuthContext } from "./AuthProvider";
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
        const days_since_status = status_and_diff_days["days_since_status"];

        if (type === "sort") {
          const is_completed = status === "completed";
          const days = days_since_status ?? 99999;
          return (is_completed ? 0 : 1) * 1_000_000 + days;
        }

        if (type === "filter") {
          if (status == "completed") {
            return "completed " + diff_days;
          }
          return (status ?? "") + " " + diff_days;
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
    {
      data: "last_link",
      responsivePriority: 1,
      render: (last_link, type) => {
        const text = last_link["text"];
        const hasMismatch = last_link["has_state_mismatch"];
        const completedState = last_link["completed_state"];
        const desiredState = last_link["desired_state"];

        if (type === "sort") {
          return last_link["days_since"] ?? 99999;
        }
        if (type === "filter") {
          return (
            text +
            " " +
            (hasMismatch ? "warning mismatch " : "") +
            (completedState ?? "")
          );
        }
        if (!hasMismatch) {
          return text;
        }
        return (
          '<i class="bi bi-exclamation-triangle-fill" ' +
          'style="color: rgb(245, 158, 11);" ' +
          `title="Última llamada completada dejó el interruptor en ${completedState}; esperado ${desiredState}"></i> ` +
          text
        );
      },
    },
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
    } else if (data.is_active == "Activo" && status != null && status != "completed") {
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
      <AddClientModal
        onAdd={() => {
          update();
        }}
        isOpen={isAddClientModalOpen}
        handleClose={() => setIsAddClientModalOpen(false)}
      ></AddClientModal>
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
          <a href="/manual/index.html" target="_blank" rel="noopener noreferrer">
            Manual de usuario
          </a>
        </div>
      </div>
    </>
  );
};

const GetList = async () => {
  const database = await ReadDatabase();
  const devices = [];
  for (const element in database) {
    const e = database[element];
    devices.push({
      serial_number: e["serial_number"],
      phone_number: e["phone_number"],
      client_name: e["client_name"],
      client_number: e["client_number"],
      is_active: e["is_active"],
      enabled: e["enabled"],
      is_manual_override: e["is_manual_override"],
      is_payment_current: e["is_payment_current"],
      last_completed_state: e["last_completed_state"] ?? null,
      last_call_status: e["last_call_status"] ?? null,
      last_call_at: e["last_call_at"] ?? null,
      last_completed_call_at: e["last_completed_call_at"] ?? null,
    });
  }
  return devices;
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
    return "120+ días";
  }

  let days = "";
  if (diffDays == 1) {
    days = " día";
  } else {
    days = " días";
  }

  return diffDays + days;
};

const formatOnOff = (enabled) => (enabled ? "on" : "off");

const ListToDataArray = (devices) => {
  return devices.map((value) => {
    const status = value["last_call_status"];
    const lastCallAt = value["last_call_at"];
    const lastCompletedCallAt = value["last_completed_call_at"];
    const effectiveEnabled = value["is_manual_override"]
      ? value["enabled"]
      : value["is_payment_current"];
    const lastCompletedState = value["last_completed_state"];
    const hasStateMismatch =
      value["is_active"] &&
      status === "completed" &&
      lastCompletedState != null &&
      lastCompletedState !== effectiveEnabled;
    return {
      serial_number: value["serial_number"],
      phone_number: value["phone_number"],
      client_name: value["client_name"],
      client_number: value["client_number"],
      is_active: value["is_active"] ? "Activo" : "Inactivo",
      status:
        status == null
          ? "-"
          : status + "  (" + FormatDate(lastCallAt) + ") ",
      diffDays: GetDaysSince(lastCompletedCallAt),
      enable: value["enabled"] ? "On" : "Off",
      is_manual_override: value["is_manual_override"],
      is_payment_current: value["is_payment_current"],
      status_icon: status,
      enabled_and_is_active: {
        // Effective on/off: respect manual override, otherwise follow Toku payment status.
        enabled: effectiveEnabled,
        is_active: value["is_active"],
      },
      status_and_diff_days: {
        status: status,
        diff_days: FormatDate(lastCallAt),
        days_since_status: GetDaysSince(lastCallAt),
      },
      last_link: {
        text: FormatDate(lastCompletedCallAt),
        days_since: GetDaysSince(lastCompletedCallAt),
        completed_state:
          lastCompletedState == null ? null : formatOnOff(lastCompletedState),
        desired_state: formatOnOff(effectiveEnabled),
        has_state_mismatch: hasStateMismatch,
      },
    };
  });
};

export default List;
