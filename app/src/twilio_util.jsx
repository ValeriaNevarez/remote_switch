
const SendMessage = async (to,text) => {
    try {
    const res = await fetch("/api/sendMessage", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ to: to, body: text }),
      });
  
      const data = await res.json();

      console.log(data);
    } catch (error) {
        console.log(error);
        throw error;
    }
}

const MakeCall = async (to) => {
  try {
    const res = await fetch("/api/makeCall", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({to:to}),
    });

    const data = await res.json();

  } catch (error) {
    console.log(error);
    throw error;
  }

}

const GetLastCallStatus = async (phone_number) => {
  try {
    const res = await fetch("/api/getLastCallStatus", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({phone_number: phone_number}),
    });

    const data = await res.json();
    if (data["success"] === false) {
      return "Error"
    }

    console.log(data["status"]);
    return data["status"];

  } catch (error) {
    console.log(error);
    throw error;
  }
 
}

const GetLastCompletedCallDate = async (phone_number) => {
  try {
    const res = await fetch("/api/getLastCompletedCallDate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({phone_number: phone_number}),
    });

    const data = await res.json();
    if (data["success"] === false) {
      return "Error"
    }

    console.log(data["lastCallDate"]);
    return data["lastCallDate"];

  } catch (error) {
    console.log(error);
    throw error;
  }
 
}

const GetStatusList = async (phone_numbers) => {
  try {
    const res = await fetch("/api/getStatusList", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({phone_numbers: phone_numbers}),
    });

    const data = await res.json();


    console.log(data['dictionary']);
    // return data["status"];

  } catch (error) {
    console.log(error);
    throw error;
  }
 
}

export {SendMessage, MakeCall, GetLastCallStatus, GetLastCompletedCallDate, GetStatusList};