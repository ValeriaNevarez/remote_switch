const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;

import twilio from "twilio";

const GetCallList = async () => {
  const client = twilio(account_sid, auth_token);
  return await client.calls.list({
    pageSize: 1000,
  });
};

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const phone_numbers = req.body.phone_numbers;
  let dictionary = {};
  for (const phone_number of phone_numbers) {
    dictionary[phone_number] = {
      date: null,
      status: null,
      status_date: null,
    };
  }

  const call_list = await GetCallList();
  for (const element of call_list) {
    const date_created = element["dateCreated"];
    const phone_to = element["to"];
    let status = element["status"];
    const duration = element["duration"];

    if (!(phone_to in dictionary)) {
      continue;
    }

    if (status == "completed" && duration < 60) {
      status = "incompleted";
    }
    // Con esto llenamos la última llamada completada
    if (dictionary[phone_to]["date"] == null && status == "completed") {
      dictionary[phone_to]["date"] = date_created;
    }
    if (dictionary[phone_to]["status"] == null) {
      dictionary[phone_to]["status"] = status;
      dictionary[phone_to]["status_date"] = date_created;
    }
  }

  res.send(JSON.stringify({ dictionary: dictionary }));
};
