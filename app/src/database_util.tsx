import { database } from "./firebase";
import { ref, set, child, get, getDatabase, update, push, remove } from "firebase/database";

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

const ChangeDeviceActive = async (serial: number, newIsActive) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeActive(id, newIsActive);
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeDeviceClientName = async (serial: number, newClientName) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeClientName(id, newClientName);
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeDeviceClientNumber = async (serial: number, newClientNumber) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeClientNumber(id, newClientNumber);
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const ChangeDeviceEnable = async (serial: number, newIsEnabled) => {
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

const GetIdForSerialNumber = async (serial_number: number) => {
  try {
    const db = await ReadDatabase();
    for (let i = 0; i < db.length; i++) {
      if (Number(db[i]["serial_number"]) == serial_number) {
        return i;
      }
    }
    throw "Numero de serie no existe";
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const AddDevice = async (serialNumber: number, phoneNumber: string) => {
  try {
    const db = database;
    
    // Get the current devices to find the highest numeric key
    const devicesRef = ref(db, "devices");
    const snapshot = await get(devicesRef);
    
    let nextKey = 0;
    if (snapshot.exists()) {
      const devices = snapshot.val();
      // Find the maximum numeric key
      const keys = Object.keys(devices);
      const numericKeys = keys
        .map(key => parseInt(key))
        .filter(key => !isNaN(key));
      
      if (numericKeys.length > 0) {
        nextKey = Math.max(...numericKeys) + 1;
      }
    }
    
    // Use the incremental number as the key
    const newDeviceRef = ref(db, `devices/${nextKey}`);
    await set(newDeviceRef, {
      serial_number: serialNumber,
      phone_number: phoneNumber,
      client_name: "",
      client_number: "",
      is_active: true,
      enabled: true,
    });
  } catch (error) {
    console.log(error);
    throw error;
  }
};

const DeleteDevice = async (serial_number) => {
  try {
    const db = await ReadDatabase();
    let deviceKey: number | null = null;
    
    // Find the device key by serial number
    for (const key in db) {
      if (db[key] && db[key]["serial_number"] == serial_number) {
        deviceKey = key;
        break;
      }
    }
    
    if (deviceKey === null) {
      throw "Numero de serie no existe";
    }
    
    // Remove the device from Firebase
    await remove(ref(database, "devices/" + deviceKey));
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
  DeleteDevice,
};

