import { database } from "./firebase";
import { ref, set, child, get, getDatabase, update } from "firebase/database";

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

const ChangeDeviceActive = async (serial, newIsActive) => {
  try {
    const id = await GetIdForSerialNumber(serial);
    await ChangeActive(id, newIsActive);
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
    throw 'Numero de serie no existe';
  } catch (error) {
    console.log(error);
    throw error;
  }
};

// const getDeviceData = (serial_number) => {
//   return "su phone number y su active";
// }

export { ChangeDeviceActive, ReadDatabase, GetIdForSerialNumber };
