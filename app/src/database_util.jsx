import  {database}  from "./firebase";
import { ref, set, child, get, getDatabase } from "firebase/database";

const writeUserData = (userId, name, email) => {
  const db = database;
  set(ref(db, "users/" + userId), {
    username: name,
    email: email,
  });
};

const changeDeviceActive = (serial, new_is_active) => {
  

}

// Modificar para que regrese los contenidos de la base de datos.
const readDatabase = async () => {
  const dbRef = ref(getDatabase());
  let result = [];
  await get(child(dbRef, `devices`)).then((snapshot) => {
    if (snapshot.exists()) {
      result = snapshot.val();
    } else {
      console.log("No hay datos disponibles");
    }
  }).catch((error) => {
    console.error(error);
  });

  return result;
}

const GetIdForSerialNumber = async (serial_number) => {
  const db = await readDatabase();
  for (let i = 0; i < db.length; i++) {
    if( db[i]["serial_number"] == serial_number ) {
      return i
    }
  }  
  return -1
};




// const getDeviceData = (serial_number) => {
//   return "su phone number y su active";
// }

export {writeUserData, readDatabase, GetIdForSerialNumber};
