import admin from "firebase-admin";

let initialized = false;

const initAdmin = () => {
  if (initialized) {
    return;
  }

  const encoded = process.env.FIREBASE_SERVICE_ACCOUNT_B64;
  const databaseURL = process.env.FIREBASE_DATABASE_URL;
  if (!encoded || !databaseURL) {
    throw new Error(
      "FIREBASE_SERVICE_ACCOUNT_B64 and FIREBASE_DATABASE_URL are required",
    );
  }

  const serviceAccount = JSON.parse(
    Buffer.from(encoded, "base64").toString("utf-8"),
  );

  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL,
  });
  initialized = true;
};

export const getAdminDatabase = () => {
  initAdmin();
  return admin.database();
};

export const findDeviceKeyByPhone = async (phoneNumber) => {
  const snapshot = await getAdminDatabase().ref("devices").get();
  if (!snapshot.exists()) {
    return null;
  }

  for (const [key, device] of Object.entries(snapshot.val())) {
    if (device?.phone_number === phoneNumber) {
      return key;
    }
  }
  return null;
};

export const updateDeviceLastCall = async (deviceKey, fields) => {
  await getAdminDatabase().ref(`devices/${deviceKey}`).update(fields);
};
