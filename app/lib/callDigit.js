import { invertedPhoneNumbers } from "./repoConfig.js";

export const pressedDigitForEnable = (phoneNumber, wantEnable) => {
  const isInverted = invertedPhoneNumbers.has(phoneNumber);
  const enabled = Boolean(wantEnable);
  return (enabled && !isInverted) || (!enabled && isInverted) ? "5" : "1";
};

export const dtmfSignalForEnable = (phoneNumber, wantEnable) => {
  const digit = pressedDigitForEnable(phoneNumber, wantEnable);
  return digit === "5" ? "w5" : "w1";
};
