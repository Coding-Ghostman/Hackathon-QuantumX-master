const app = document.querySelector(".weather-app");
const temp = document.querySelector(".temp");
const dateOutput = document.querySelector(".date");
const timeOutput = document.querySelector(".time");
const conditionOutput = document.querySelector(".condition");
const nameOutput = document.querySelector(".name");
const icon = document.querySelector(".icon");
const cloudOutput = document.querySelector(".cloud");
const humidityOutput = document.querySelector(".humidity");
const windOutput = document.querySelector(".wind");
const form = document.getElementById("locationInput");
const search = document.querySelector(".search");
const btn = document.querySelector(".submit");
const cities = document.querySelectorAll("ul li.city");
const envVariables = document.querySelector("#selection");
const select = document.getElementById("selection");
const graph = document.getElementById("graphContainer");
const date = document.createElement("p");

select.addEventListener("change", function handleChange(event) {
   console.log(event.target.value);
   cityInput = e.target.innerHTML;
   fetchWeatherData();
   const request = new XMLHttpRequest();
   request.open("POST", `/get_city_data/${JSON.stringify(cityInput)}/${JSON.stringify(event.target.value)}`);
   request.send();
   app.style.opacity = "0";
   fetch("/test")
      .then(function (response) {
         return response.json();
      })
      .then(function (text) {
         // document.write(text.ds);
         console.log("Get response: " + text);
      });
});

// Receiving GET request from Server

// Default city when the page loads.
let cityInput = "Bengaluru";

// Add click event to each city in the panel\
cities.forEach((city) => {
   city.addEventListener("click", (e) => {
      cityInput = e.target.innerHTML;
      fetchWeatherData();
      envVar = select.options[select.selectedIndex].value;
      const request = new XMLHttpRequest();
      request.open("POST", `/get_city_data/${JSON.stringify(cityInput)}/${JSON.stringify(envVar)}`);
      request.send();
      app.style.opacity = "0";
      fetch("/test")
         .then(function (response) {
            return response.json();
         })
         .then(function (text) {
            console.log("Get response: " + text);
         });
   });
});

// Add submit event to the form
form.addEventListener("submit", (e) => {
   if (search.value.length == 0) {
      alert("Please type in a city name");
   } else {
      cityInput = search.value;
      envVar = select.options[select.selectedIndex].value;
      fetchWeatherData();
      const request = new XMLHttpRequest();
      request.open("POST", `/get_city_data/${JSON.stringify(cityInput)}/${JSON.stringify(envVar)}`);
      request.send();
      search.value = "";
      app.style.opacity = "0";

      fetch("/test")
         .then(function (response) {
            return response.json();
         })
         .then(function (text) {
            text = JSON.parse(text);
            text.forEach((ele, i) => {
               let text = (document.createElement("p").id = `${ele}${i}`);
               var text2 = document.createTextNode(ele.ds);
               text.appendChild(`${text2}`);
               // text.innerHTML = ele.ds;
               graph.appendChild(text);
            });
            // document.write(text[0].ds);
            // document.getElementById("graphContainer").innerHTML = text[0].ds;
            console.log("Get response: " + text);
         });
   }

   e.preventDefault();
});

const request = new XMLHttpRequest();
envVar = select.options[select.selectedIndex].value;
request.open("POST", `/get_city_data/${JSON.stringify(cityInput)}/${JSON.stringify(envVar)}`);
request.send();

function dayOfTheWeek(day, month, year) {
   const weekday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
   return weekday[new Date(`${day}/${month}/${year}`).getDay()];
}

function fetchWeatherData() {
   fetch(`https://api.weatherapi.com/v1/current.json?key=00d66542b64e4d97855142340230601&q=${cityInput}&aqi=no`)
      .then((response) => response.json())
      .then((data) => {
         temp.innerHTML = data.current.temp_c + "&#176;";
         conditionOutput.innerHTML = data.current.condition.text;
         const date = data.location.localtime;
         const y = parseInt(date.substr(0, 4));
         const m = parseInt(date.substr(5, 2));
         const d = parseInt(date.substr(8, 2));
         const time = date.substr(11);
         dateOutput.innerHTML = `${dayOfTheWeek(d, m, y)} ${d}, ${m}, ${y}`;
         timeOutput.innerHTML = time;
         nameOutput.innerHTML = data.location.name;
         const iconId = data.current.condition.icon.substr("//cdn.weatherapi.com/weather/64x64/".length);
         icon.src = "static/icons/" + iconId;

         cloudOutput.innerHTML = data.current.cloud + "%";
         humidityOutput.innerHTML = data.current.humidity + "%";
         windOutput.innerHTML = data.current.wind_kph + "km/h";

         let timeOfDay = "day";
         const code = data.current.condition.code;

         if (!data.current.is_day) {
            timeOfDay = "night";
         }

         if (code == 1000) {
            app.style.backgroundImage = `url(static/images/${timeOfDay}/clear.jpg)`;
            btn.style.background = "#e5ba92";
            if (timeOfDay == "night") {
               btn.style.background = "#181e27";
            }
         } else if (code == 1003 || code == 1006 || code == 1009 || code == 1030 || code == 1069 || code == 1087 || code == 1135 || code == 1273 || code == 1276 || code == 1279 || code == 1282) {
            app.style.backgroundImage = `url(static/images/${timeOfDay}/cloudy.jpg)`;
            btn.style.background = "#fa6d1b";
            if (timeOfDay == "night") {
               btn.style.background = "#181e27";
            }
         } else if (
            code == 1064 ||
            code == 1069 ||
            code == 1072 ||
            code == 1150 ||
            code == 1153 ||
            code == 1180 ||
            code == 1183 ||
            code == 1186 ||
            code == 1189 ||
            code == 1192 ||
            code == 1195 ||
            code == 1204 ||
            code == 1207 ||
            code == 1240 ||
            code == 1243 ||
            code == 1246 ||
            code == 1249 ||
            code == 1252
         ) {
            app.style.backgroundImage = `url(static/images/${timeOfDay}/rainy.jpg)`;
            btn.style.background = "#647d75";
            if (timeOfDay == "night") {
               btn.style.background = "#325c80";
            }
         } else {
            app.style.backgroundImage = `url(static/images/${timeOfDay}/snowy.jpg)`;
            btn.style.background = "#4d72aa";
            if (timeOfDay == "night") {
               btn.style.background = "#1b1b1b";
            }
         }
         app.style.opacity = "1";
      })

      .catch(() => {
         alert("City not found");
         app.style.opacity = "1";
      });
}

fetchWeatherData();
app.style.opacity = "1";
