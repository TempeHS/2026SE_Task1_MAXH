// Register service worker
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("/static/js/serviceWorker.js")
      .then((res) => console.log("service Worker registered"))
      .catch((err) => console.log("service Worker not registered", err));
  });
}

// Online/Offline detection
const offlineBanner = document.getElementById("offline-banner");

function updateOnlineStatus() {
  if (navigator.onLine) {
    // User is online
    offlineBanner.style.display = "none";
    console.log("App is online");
  } else {
    // User is offline
    offlineBanner.style.display = "block";
    console.log("App is offline");
  }
}

// Check status when page loads
window.addEventListener("load", updateOnlineStatus);

// Listen for online event
window.addEventListener("online", function () {
  updateOnlineStatus();
  console.log("Connection restored");
});

// Listen for offline event
window.addEventListener("offline", function () {
  updateOnlineStatus();
  console.log("Connection lost");
});
