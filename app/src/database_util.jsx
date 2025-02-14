import  {database}  from "./firebase";
import { ref, set } from "firebase/database";

const writeUserData = (userId, name, email) => {
  const db = database;
  set(ref(db, "users/" + userId), {
    username: name,
    email: email,
  });
};

const changeDeviceActive = (serial, new_is_active) => {
  
}

const readDatabase = () => {
  // Modificar para que regrese los contenidos de la base de datos.
  return "contenidos de la base de datos";
}

const getDeviceData = (serial_number) => {
  return "su phone number y su active";
}

export {writeUserData, readDatabase}
