import { AddDevice } from "./database_util";
import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import "datatables.net-responsive-dt";

const AddClientModal = ({ onAdd, isOpen, handleClose }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [serialNumber, setSerialNumber] = useState<number | null>(null);
  const [notice, setNotice] = useState("");

  const validateNumericInput = (value : string): number | null => {
    // Only allow numbers
    const numericString = value.replace(/[^0-9]/g, "");
    return numericString === "" ? null : Number(numericString);
  };

  const validatePhoneNumberInput = (value) => {
    // Only allow numbers and the "+" character
    const cleaned = value.replace(/[^0-9+]/g, "");
    // Ensure +52 prefix is always present
    if (!cleaned.startsWith("+52")) {
      // If user tries to delete the prefix, restore it
      if (cleaned.startsWith("+")) {
        // User might have typed just +, ensure it becomes +52
        return "+52" + cleaned.substring(1).replace(/[^0-9]/g, "");
      }
      // If no + at all, add +52 prefix
      return "+52" + cleaned.replace(/[^0-9]/g, "");
    }
    return cleaned;
  };

  useEffect(() => {
    if (notice != "") {
      setTimeout(() => {
        setNotice("");
      }, 3000);
    }
  }, [notice]);

  useEffect(() => {
    if (isOpen) {
      setPhoneNumber("+52");
      setSerialNumber(null);
      setNotice("");
    }
  }, [isOpen]);

  const handleAdd = () => {
    const trimmedPhoneNumber = phoneNumber.trim();

    if (trimmedPhoneNumber === "" || serialNumber == null) {
      setNotice("Por favor, complete todos los campos");
      return;
    }

    AddDevice(serialNumber, trimmedPhoneNumber)
      .then(() => {
        setNotice("Se agregó correctamente a la base de datos.");
        setPhoneNumber("");
        setSerialNumber(null);
        onAdd();
        handleClose();
      })
      .catch((e) => {
        setNotice("Error al agregar cliente: " + e);
      });
  };

  if (!isOpen) return null;

  return (
    <>
      <div
        className="modal-backdrop fade show"
        onClick={handleClose}
      ></div>
      <div
        className="modal fade show"
        style={{ display: "block" }}
        tabIndex="-1"
        aria-hidden="false"
      >
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h1 className="modal-title fs-5">
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
              <span className="input-group-text">+52</span>
              <input
                type="text"
                className="form-control"
                value={phoneNumber.startsWith("+52") ? phoneNumber.substring(3) : phoneNumber}
                onChange={(e) => {
                  const userInput = e.target.value.replace(/[^0-9]/g, "");
                  setPhoneNumber("+52" + userInput);
                }}
              ></input>
            </div>
            <div className="input-group mb-3">
              <span className="input-group-text">Número de serie: </span>
              <input
                type="text"
                className="form-control"
                value={serialNumber !== null ? serialNumber.toString() : ""}
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
              onClick={handleClose}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleAdd}
              disabled={phoneNumber.trim() === "" || serialNumber == null}
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
    </>
  );
};

AddClientModal.propTypes = {
  onAdd: PropTypes.func.isRequired,
  isOpen: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
};

export default AddClientModal;