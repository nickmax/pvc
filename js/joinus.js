// click on the moon icon in the top-right corner of the screen to switch to dark mode
window.theme = "light";

const container = document.getElementById("container");
const togglebtn = document.getElementById("dark-mode-toggle");

function toggleTheme() {
  if (window.theme === "light") {
    container.classList.add("dark");
    window.theme = "dark";
    togglebtn.innerHTML = `<span class="material-icons">brightness_4</span>`;
  } else {
    container.classList.remove("dark");
    window.theme = "light";
    togglebtn.innerHTML = `<span class="material-icons">nights_stay</span>`;
  }
}

togglebtn.addEventListener("click", toggleTheme);