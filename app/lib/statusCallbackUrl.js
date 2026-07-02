export const statusCallbackBaseUrl = () => {
  const configured = process.env.TWILIO_STATUS_CALLBACK_BASE_URL?.trim();
  if (configured) {
    return configured.replace(/\/$/, "");
  }

  const vercelUrl = process.env.VERCEL_URL?.trim();
  if (vercelUrl) {
    return `https://${vercelUrl.replace(/\/$/, "")}`;
  }

  return null;
};

export const buildStatusCallbackUrl = (wantEnable) => {
  const baseUrl = statusCallbackBaseUrl();
  if (!baseUrl) {
    return null;
  }

  const completedState = wantEnable ? "on" : "off";
  const params = new URLSearchParams({ completed_state: completedState });
  return `${baseUrl}/api/twilioCallStatus?${params.toString()}`;
};
