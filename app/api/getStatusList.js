const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;

import twilio from "twilio";

const GetLastCallStatus = async (phone_number) => {
  const client = twilio(account_sid, auth_token);
  let status = "Internal error";
  await client.calls
    .list({
      to: phone_number,
      limit: 1,
    })
    .then((CallInstances) => {
      if (CallInstances.length != 0) {
        status = CallInstances[0]["status"];
      }
    })
    .catch((err) => {
      console.log(err);
    });

  return status;
};

const GetLastCompletedCallDate = async (phone_number) => {
  const client = twilio(account_sid, auth_token);
  let date = "Internal error";
  await client.calls
    .list({
      to: phone_number,
      status: "completed",
      limit: 1,
    })
    .then((CallInstances) => {
      if (CallInstances.length != 0) {
        date = CallInstances[0]["dateCreated"];
      }
    })
    .catch((err) => {
      console.log(err);
    });

  return date;
};

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const phone_numbers = req.body.phone_numbers;
  let dictionary = {};
  for (const phone_number of phone_numbers) {
    dictionary[phone_number] = {};
    dictionary[phone_number]["status"] = await GetLastCallStatus(phone_number);
    dictionary[phone_number]["date"] = await GetLastCompletedCallDate(
      phone_number
    );
  }

  res.send(JSON.stringify({ dictionary: dictionary }));
};
