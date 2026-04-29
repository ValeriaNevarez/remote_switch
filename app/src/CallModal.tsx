import {
  ChangeDeviceActive,
  ChangeDeviceEnable,
  ChangeDeviceManualOverride,
  ChangeDeviceClientName,
  ChangeDeviceClientNumber,
  DeleteDevice,
} from "./database_util";
import { useState, useEffect, useContext } from "react";
import { MakeCall, SendMessageToChangeMaster } from "./twilio_util";
import { AuthContext } from "./AuthProvider";
import { Modal } from "bootstrap";
import PropTypes from "prop-types";
import "datatables.net-responsive-dt";

const CallModal = ({ data, update, onClose }) => {
  const { user } = useContext(AuthContext);
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

  useEffect(() => {
    const modalElement = document.getElementById("modal");
    if (modalElement && onClose) {
      const handleHidden = () => {
        onClose();
      };
      modalElement.addEventListener("hidden.bs.modal", handleHidden);

      return () => {
        modalElement.removeEventListener("hidden.bs.modal", handleHidden);
      };
    }
  }, [onClose]);

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
            {!data ? (
              <div>Borrando...</div>
            ) : (
              <>
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
                disabled={clientNameInput === ""}
                className="btn btn-outline-secondary"
                type="button"
                onClick={() => {
                  ChangeDeviceClientName(Number(data.serial_number), clientNameInput)
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
                disabled={clientNumberInput === ""}
                className="btn btn-outline-secondary"
                type="button"
                onClick={() => {
                  ChangeDeviceClientNumber(
                    Number(data.serial_number),
                    clientNumberInput
                  )
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
            <br />
            <b>Estado actual: </b>
            {data.is_active}
            <br />
            <b>Último estatus: </b>
            {data.status}
            <br />
            <br />
            <b>Estatus de pago: </b>
            {data.is_payment_current ? "al corriente" : "retrasado"}
            <br />
            <b>Control: </b>
            {data.is_manual_override ? "manual" : "automático"}
            <br />
            {data.is_manual_override && (
              <>
                <b>Manual On/Off: </b>
                {data.enable}
                <br />
              </>
            )}
            <br />
            <button
              type="button"
              onClick={() => {
                const effectiveEnabled = data.is_manual_override
                  ? data.enable == "On"
                  : data.is_payment_current;
                setCallButtonEnabled(false);
                MakeCall(data.phone_number, effectiveEnabled)
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
                    setNotice("Error al realizar la llamada:" + e);
                  });
              }}
              className="btn btn-secondary me-3 mb-3"
              disabled={!callButtonEnabled}
            >
              Llamar
            </button>
            <button
              type="button"
              onClick={() => {
                ChangeDeviceActive(
                  Number(data.serial_number),
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
              className="btn btn-secondary me-3 mb-3"
            >
              {data.is_active == "Activo" ? "Desactivar" : "Activar"}
            </button>
            {data.is_manual_override && (
              <button
                type="button"
                onClick={() => {
                  const newEnable = data.enable == "On" ? false : true;
                  ChangeDeviceEnable(Number(data.serial_number), newEnable)
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
                          setNotice("Error al realizar la llamada:" + e);
                        });
                    })
                    .catch((e) => {
                      setNotice("Error al actualizar el estado: " + e);
                    });
                }}
                className="btn btn-secondary me-3 mb-3"
                disabled={!callButtonEnabled}
              >
                {data.enable == "On" ? "Apagar" : "Encender"}
              </button>
            )}
            <button
              type="button"
              onClick={() => {
                ChangeDeviceManualOverride(
                  Number(data.serial_number),
                  !data.is_manual_override
                )
                  .then(() => {
                    setNotice("Se actualizó el control");
                    update();
                  })
                  .catch((e) => {
                    setNotice("Error al actualizar el control: " + e);
                  });
              }}
              className="btn btn-secondary me-3 mb-3"
            >
              {data.is_manual_override
                ? "Cambiar a automático"
                : "Cambiar a manual"}
            </button>
            <button
              type="button"
              onClick={() => {
                SendMessageToChangeMaster(data.phone_number)
                  .then(() => {
                    setNotice("Se envió el SMS");
                  })
                  .catch((e) => {
                    setNotice("Error al enviar el SMS:" + e);
                  });
              }}
              className="btn btn-secondary me-3 mb-3"
            >
              Enviar SMS
            </button>
            {user?.email === "admin@admin.com" && (
              <button
                type="button"
                className="btn btn-danger me-3 mb-3"
                onClick={() => {
                  if (window.confirm("¿Está seguro de que desea borrar este dispositivo?")) {
                    DeleteDevice(Number(data.serial_number))
                      .then(() => {
                        setNotice("Se eliminó el dispositivo correctamente");
                        update();
                        if (onClose) {
                          onClose();
                        }
                        setTimeout(() => {
                          const modalElement = document.getElementById("modal");
                          const modal = Modal.getInstance(modalElement);
                          if (modal) {
                            modal.hide();
                          }
                        }, 1500);
                      })
                      .catch((e) => {
                        setNotice("Error al eliminar el dispositivo: " + e);
                      });
                  }
                }}
              >
                Borrar
              </button>
            )}

            {"" !== notice && (
              <div className="alert alert-warning mt-3" role="alert">
                {notice}
              </div>
            )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

CallModal.propTypes = {
    data: PropTypes.object,
    update: PropTypes.func.isRequired,
    onClose: PropTypes.func,
};

export default CallModal;