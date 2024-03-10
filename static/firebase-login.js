"use strict";

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

const firebaseConfig = {
  // apiKey: "AIzaSyC4eJpAyxKlSFAtmzSS21M6Dm7wBRhvxOM",
  // authDomain: "fluted-reporter-415320.firebaseapp.com",
  // projectId: "fluted-reporter-415320",
  // storageBucket: "fluted-reporter-415320.appspot.com",
  // messagingSenderId: "132606520507",
  // appId: "1:132606520507:web:3837f8e46268dc55d04d9e",
  // measurementId: "G-GBJNZV62JB"
  apiKey: "AIzaSyDd1po0Vd4eZlXK1DMVjGwut2qRFn4MZvg",
  authDomain: "durable-catbird-416619.firebaseapp.com",
  projectId: "durable-catbird-416619",
  storageBucket: "durable-catbird-416619.appspot.com",
  messagingSenderId: "985992435220",
  appId: "1:985992435220:web:c6f109cde8d58571e83901",
  measurementId: "G-DWZTGTREQL",
};

function updateUI(cookie) {
  console.log("inside", cookie);
  var token = parsedCookieToken(cookie);

  if (token?.length > 0) {
    document.getElementById("login-box").hidden = true;
    document.getElementById("signout").hidden = false;
  } else {
    document.getElementById("login-box").hidden = false;
    document.getElementById("signout").hidden = true;
  }
}
function parsedCookieToken(cookie) {
  var strings = cookie?.split(";");
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
  console.log("hello world load before" + document.cookie);
  updateUI(document.cookie);
  console.log("hello world loasssd" + document.cookie);

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
      .catch((e) => {
        console.log(e);
        document.getElementById("error-box").innerHTML = e;
      });
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
      .catch((e) => {
        console.log(e);
        document.getElementById("error-box").innerHTML = e;
      });
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
