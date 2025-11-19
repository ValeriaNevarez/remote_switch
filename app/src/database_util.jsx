import { database } from "./firebase";
import { ref, set, child, get, getDatabase, update, push } from "firebase/database";

const ChangeActive = async (deviceId, isActive) => {
  try {
    const db = database;
    await update(ref(db, "devices/" + deviceId), {
      is_active: isActive,
    });
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeEnable = async (deviceId, isEnabled) => {
  try {
    const db = database;
    await update(ref(db, "devices/" + deviceId), {
      enabled: isEnabled,
    });
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeClientName = async (deviceId, clientName) => {
  try {
    const db = database;
    await update(ref(db, "devices/" + deviceId), {
      client_name: clientName,
    });
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeClientNumber = async (deviceId, clientNumber) => {
  try {
    const db = database;
    await update(ref(db, "devices/" + deviceId), {
      client_number: clientNumber,
    });
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeDeviceActive = async (serial, newIsActive) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeActive(id, newIsActive);
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeDeviceClientName = async (serial, newClientName) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeClientName(id, newClientName);
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeDeviceClientNumber = async (serial, newClientNumber) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeClientNumber(id, newClientNumber);
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeDeviceEnable = async (serial, newIsEnabled) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeEnable(id, newIsEnabled);
  } catch (error) {
    console.log(error);
    throw error;
  }
};

// Modificar para que regrese los contenidos de la base de datos.
const ReadDatabase = async () => {
  try {
    const dbRef = ref(getDatabase());
    let result = [];
    await get(child(dbRef, `devices`)).then((snapshot) => {
      if (snapshot.exists()) {
        result = snapshot.val();
      } else {
        console.log("No hay datos disponibles");
      }
    });
    return result;
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const GetIdForSerialNumber = async (serial_number) => {
  try {
    const db = await ReadDatabase();
    for (let i = 0; i < db.length; i++) {
      if (db[i]["serial_number"] == serial_number) {
        return i;
      }
    }
    throw "Numero de serie no existe";
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const AddDevice = async (serialNumber, phoneNumber) => {
  try {
    const db = database;
    const newDeviceRef = push(ref(db, "devices"));
    await set(newDeviceRef, {
      serial_number: serialNumber,
      phone_number: phoneNumber,
      client_name: "",
      client_number: "",
      is_active: true,
      enabled: false,
    });
  } catch (error) {
    console.log(error);
    throw error;
  }
};

export {
  ChangeDeviceActive,
  ReadDatabase,
  GetIdForSerialNumber,
  ChangeDeviceEnable,
  ChangeDeviceClientName,
  ChangeDeviceClientNumber,
  AddDevice,
};
