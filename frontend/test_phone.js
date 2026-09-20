const { parsePhoneNumberFromString } = require('libphonenumber-js');

function formatPhone(phone) {
  if (!phone) return '-';
  let p = phone.trim();
  if (!p.startsWith('+')) {
    p = '+' + p;
  }
  const parsed = parsePhoneNumberFromString(p);
  if (parsed) {
    return parsed.formatInternational();
  }
  return phone;
}

console.log(formatPhone("12243264981"));
console.log(formatPhone("1 914 455 1835"));
console.log(formatPhone("79991234567"));
console.log(formatPhone("+380991234567"));
