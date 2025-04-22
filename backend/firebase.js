// backend/firebaseAdmin.js or wherever you configure Firebase
const admin = require("firebase-admin");
require("dotenv").config(); // loads .env

const serviceAccount = require(process.env.GOOGLE_APPLICATION_CREDENTIALS);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

module.exports = admin;
