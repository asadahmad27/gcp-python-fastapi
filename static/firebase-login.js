"use strict";

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyC4eJpAyxKlSFAtmzSS21M6Dm7wBRhvxOM",
  authDomain: "fluted-reporter-415320.firebaseapp.com",
  projectId: "fluted-reporter-415320",
  storageBucket: "fluted-reporter-415320.appspot.com",
  messagingSenderId: "132606520507",
  appId: "1:132606520507:web:3837f8e46268dc55d04d9e",
  measurementId: "G-GBJNZV62JB",
};

function updateUI(cookie) {
  var token = parsedCookieToken(cookie);
  if (token?.length == 0) {
  } else {
  }
}
function parsedCookieToken(cookie) {
  var strings = cookie.split(";");
  for (let i = 0; i < strings.length; i++) {
    var temp = strings[i].split("=");
    if (temp[0] == "token") {
      return temp[1];
    }
  }
  return "";
}
window.addEventListener("load", function () {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  //   updateUI(document.cookie);
  console.log("hello world load");

  document.getElementById("signup").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential?.user;

        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
          window.location = "/";
        });
      })
      .catch((e) => console.log(e));
  });

  document.getElementById("login").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential?.user;

        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
          window.location = "/";
        });
      })
      .catch((e) => console.log(e));
  });

  document.getElementById("signout").addEventListener("click", function () {
    signOut(auth)
      .then((userCredential) => {
        document.cookie = "token=;path=/;SameSite=Strict";
        window.location = "/";
      })
      .catch((e) => console.log(e));
  });
});
