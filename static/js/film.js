const playButton = document.getElementById("play-button");
const trailerContainer = document.getElementById("trailerContainer");
const overlay = document.getElementById("overlay");

// ouvrir trailer
playButton.addEventListener("click", () => {
  overlay.style.display = "block";
  trailerContainer.style.display = "block";
});

// fermer trailer si on clique sur overlay
overlay.addEventListener("click", () => {
  overlay.style.display = "none";
  trailerContainer.style.display = "none";
});