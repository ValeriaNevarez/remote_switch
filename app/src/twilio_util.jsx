
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
    } catch (error) {
        console.log(error);
        throw error;
    }
}

const MakeCall = async (to,enable) => {
  try {
    const res = await fetch("/api/makeCall", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({to:to,enable:enable}),
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
    return data["dictionary"];

  } catch (error) {
    console.log(error);
    throw error;
  }
 
}

export {SendMessage, MakeCall, GetLastCallStatus, GetLastCompletedCallDate, GetStatusList};