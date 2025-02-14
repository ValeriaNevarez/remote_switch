// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getDatabase } from "firebase/database";


// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCDgGTu9Je9qncnW_z8E0bsJhSYRDDkS8g",
  authDomain: "remote-switch-6d907.firebaseapp.com",
  projectId: "remote-switch-6d907",
  storageBucket: "remote-switch-6d907.firebasestorage.app",
  messagingSenderId: "368091458955",
  appId: "1:368091458955:web:ded067debbc73b3afd138e",
  measurementId: "G-ZCRHZ9R00F",
  databaseURL: "https://remote-switch-6d907-default-rtdb.firebaseio.com/",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const database = getDatabase(app);

export default auth;
export { database};