import { AddDevice } from "./database_util";
import { useState, useEffect } from "react";
import { Modal } from "bootstrap";
import PropTypes from "prop-types";
import "datatables.net-responsive-dt";

const AddClientModal = ({ onAdd, isOpen, handleClose }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [serialNumber, setSerialNumber] = useState("");
  const [notice, setNotice] = useState("");

  const validateNumericInput = (value) => {
    // Only allow numbers and the "+" character
    return value.replace(/[^0-9+]/g, "");
  };

  useEffect(() => {
    if (notice != "") {
      setTimeout(() => {
        setNotice("");
      }, 3000);
    }
  }, [notice]);

  useEffect(() => {
    const modalElement = document.getElementById("addClientModal");
    if (modalElement) {
      const modal = Modal.getInstance(modalElement) || new Modal(modalElement);
      if (isOpen) {
        modal.show();
        setPhoneNumber("");
        setSerialNumber("");
        setNotice("");
      } else {
        modal.hide();
      }
    }
  }, [isOpen]);

  useEffect(() => {
    const modalElement = document.getElementById("addClientModal");
    if (modalElement) {
      // Listen for Bootstrap modal hide events (backdrop click, ESC key)
      // This ensures handleClose is called when modal is closed via Bootstrap
      const handleHidden = () => {
        // Only call handleClose if modal was actually open
        // This prevents calling handleClose when we programmatically hide it
        if (isOpen) {
          handleClose();
        }
      };
      modalElement.addEventListener("hidden.bs.modal", handleHidden);

      return () => {
        modalElement.removeEventListener("hidden.bs.modal", handleHidden);
      };
    }
  }, [isOpen, handleClose]);

  const handleAdd = () => {
    const trimmedPhoneNumber = phoneNumber.trim();
    const trimmedSerialNumber = serialNumber.trim();

    if (trimmedPhoneNumber === "" || trimmedSerialNumber === "") {
      setNotice("Por favor, complete todos los campos");
      return;
    }

    AddDevice(trimmedSerialNumber, trimmedPhoneNumber)
      .then(() => {
        setNotice("Se agregó correctamente a la base de datos.");
        setPhoneNumber("");
        setSerialNumber("");
        onAdd();
        setTimeout(() => {
          handleClose();
        }, 3000);
      })
      .catch((e) => {
        setNotice("Error al agregar cliente: " + e);
      });
  };

  const handleCancel = () => {
    setPhoneNumber("");
    setSerialNumber("");
    setNotice("");
    handleClose();
  };

  return (
    <div
      className="modal fade"
      id="addClientModal"
      data-bs-backdrop="static"
      data-bs-keyboard="true"
      tabIndex="-1"
      aria-labelledby="addClientModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h1 className="modal-title fs-5" id="addClientModalLabel">
              Alta de cliente
            </h1>
            <button
              type="button"
              className="btn-close"
              onClick={handleClose}
              aria-label="Close"
            ></button>
          </div>
          <div className="modal-body">
            <div className="input-group mb-3">
              <span className="input-group-text">Celular: </span>
              <input
                type="text"
                className="form-control"
                value={phoneNumber}
                onChange={(e) => {
                  const validatedValue = validateNumericInput(e.target.value);
                  setPhoneNumber(validatedValue);
                }}
              ></input>
            </div>
            <div className="input-group mb-3">
              <span className="input-group-text">Número de serie: </span>
              <input
                type="text"
                className="form-control"
                value={serialNumber}
                onChange={(e) => {
                  const validatedValue = validateNumericInput(e.target.value);
                  setSerialNumber(validatedValue);
                }}
              ></input>
            </div>
            {"" !== notice && (
              <div className="alert alert-warning mt-3" role="alert">
                {notice}
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleCancel}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleAdd}
              disabled={phoneNumber.trim() === "" || serialNumber.trim() === ""}
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

AddClientModal.propTypes = {
  onAdd: PropTypes.func.isRequired,
  isOpen: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
};

export default AddClientModal;