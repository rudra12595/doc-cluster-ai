// Firebase Configuration for DocCluster AI
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js";

const firebaseConfig = {
  apiKey: "AIzaSyD9IjojxQ2qyjakkrNVI4v7kH93r_05f3s",
  authDomain: "doc-cluster-bad7c.firebaseapp.com",
  projectId: "doc-cluster-bad7c",
  storageBucket: "doc-cluster-bad7c.firebasestorage.app",
  messagingSenderId: "755629157502",
  appId: "1:755629157502:web:25738f1d12be0187657c2f",
  measurementId: "G-0F5MZC5858"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

console.log("Firebase initialized successfully.");
